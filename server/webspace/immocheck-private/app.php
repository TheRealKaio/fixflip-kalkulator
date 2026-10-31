<?php
declare(strict_types=1);
require_once __DIR__ . '/smtp.php';

function nic_reply(array $body, int $status = 200): never {
    http_response_code($status);
    echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
    exit;
}
function nic_fail(string $message, int $status = 400): never { nic_reply(['error' => $message], $status); }
function nic_now(int $offset = 0): string { return gmdate('Y-m-d H:i:s', time() + $offset); }
function nic_query(PDO $db, string $sql, array $args = []): PDOStatement {
    $s = $db->prepare($sql); $s->execute($args); return $s;
}
function nic_hash(string $value, array $config): string { return hash_hmac('sha256', $value, $config['pepper']); }
function nic_email(mixed $value): string {
    if (!is_string($value)) nic_fail('Bitte eine gültige E-Mail-Adresse eingeben.');
    $email = strtolower(trim($value));
    if (strlen($email) > 254 || !filter_var($email, FILTER_VALIDATE_EMAIL) || preg_match('/[^\x21-\x7e]/', $email)) nic_fail('Bitte eine gültige E-Mail-Adresse eingeben.');
    return $email;
}
function nic_name(mixed $value): string {
    if (!is_string($value) || !preg_match('//u', $value) || trim($value) === '' || strlen($value) > 100 || preg_match('/[\x00-\x1f\x7f]/', $value)) nic_fail('Bitte Vor- und Nachname eingeben (je maximal 100 Bytes).');
    return trim($value);
}
function nic_config(): array {
    if (!is_file(__DIR__ . '/config.php')) nic_fail('Die Serverkonfiguration fehlt noch.', 503);
    $c = require __DIR__ . '/config.php';
    if (!is_array($c) || strlen($c['pepper'] ?? '') < 64 || strlen($c['setup_key'] ?? '') < 64) nic_fail('Die Serverkonfiguration ist unvollständig.', 503);
    return $c;
}
function nic_db(array $c): PDO {
    foreach (['host','name','user','password'] as $key) if (!is_string($c['db'][$key] ?? null) || $c['db'][$key] === '') nic_fail('Die Datenbankkonfiguration ist unvollständig.', 503);
    if (preg_match('/[;\x00-\x20]/', $c['db']['host'] . $c['db']['name'])) throw new RuntimeException('Invalid DB configuration');
    $db = new PDO('mysql:host=' . $c['db']['host'] . ';dbname=' . $c['db']['name'] . ';charset=utf8mb4', $c['db']['user'], $c['db']['password'], [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_EMULATE_PREPARES => false]);
    $db->exec("SET time_zone = '+00:00'");
    $GLOBALS['nic_db'] = $db;
    return $db;
}
function nic_limit(PDO $db, array $c, string $scope, string $key, int $seconds, int $max): void {
    $bucket = nic_hash($scope . '|' . $key . '|' . (int)floor(time() / $seconds), $c);
    nic_query($db, 'INSERT INTO nic_rate_limits(bucket,hits,window_start) VALUES (?,1,?) ON DUPLICATE KEY UPDATE hits=hits+1', [$bucket, nic_now()]);
    if ((int)nic_query($db, 'SELECT hits FROM nic_rate_limits WHERE bucket=?', [$bucket])->fetchColumn() > $max) nic_fail('Zu viele Versuche. Bitte später erneut versuchen.', 429);
}
function nic_session(PDO $db, array $c, bool $required = true): ?array {
    $token = $_COOKIE['__Host-nic_session'] ?? '';
    if (!is_string($token) || !preg_match('/^[a-f0-9]{64}$/D', $token)) {
        if ($required) nic_fail('Bitte zuerst anmelden.', 401);
        return null;
    }
    $u = nic_query($db, 'SELECT u.id,u.email,u.first_name,u.last_name,u.role,u.status,s.csrf_hash FROM nic_sessions s JOIN nic_users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>? AND u.verified_at IS NOT NULL', [nic_hash('session|' . $token, $c), nic_now()])->fetch(PDO::FETCH_ASSOC);
    if (!$u || $u['status'] !== 'active') {
        if ($required) nic_fail('Die Sitzung ist abgelaufen oder das Konto ist gesperrt.', 401);
        return null;
    }
    if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'GET') {
        $csrf = $_SERVER['HTTP_X_NIC_CSRF'] ?? '';
        if (!is_string($csrf) || !hash_equals($u['csrf_hash'], hash('sha256', $csrf))) nic_fail('Die Anfrage konnte nicht bestätigt werden. Bitte erneut anmelden.', 403);
    }
    unset($u['csrf_hash']);
    return $u;
}
function nic_admin(PDO $db, array $c): array {
    $u = nic_session($db, $c);
    if ($u['role'] !== 'admin') nic_fail('Nur für Administratoren verfügbar.', 403);
    return $u;
}
function nic_audit(PDO $db, ?string $actor, string $action, ?string $target = null): void {
    nic_query($db, 'INSERT INTO nic_audit(actor_id,action,target_id,created_at) VALUES (?,?,?,?)', [$actor,$action,$target,nic_now()]);
}
function nic_clean_settings(mixed $raw): array {
    if (!is_array($raw) || ($raw['version'] ?? null) !== 1) nic_fail('Ungültige Einstellungen.');
    $keys = ['version','company','layout','social','meta','favicon','websiteLogo','appleTouchIcon','imageAlts','sharing','reporting','legal','access'];
    $s = array_intersect_key($raw, array_flip($keys));
    foreach (['company','layout','social','meta','imageAlts','sharing','reporting','legal','access'] as $key) if (isset($s[$key]) && !is_array($s[$key])) nic_fail('Ungültiges Einstellungsfeld: ' . $key);
    $s['access'] = $s['access'] ?? [];
    foreach (['calculators','pdfDownload','pdfShare'] as $key) {
        $value = $s['access'][$key] ?? true;
        if (array_key_exists($key,$s['access']) && !is_bool($s['access'][$key])) nic_fail('Ungültige Zugangsregel.');
        $s['access'][$key] = $value;
    }
    $s['access'] = array_intersect_key($s['access'], array_flip(['calculators','pdfDownload','pdfShare']));
    // Inputs are public website settings, never server configuration or account data.
    $check = function (mixed $v, int $depth = 0) use (&$check): void {
        if ($depth > 5) nic_fail('Einstellungen zu tief verschachtelt.');
        if (is_array($v)) { if(count($v)>100)nic_fail('Zu viele Einstellungsfelder.'); foreach ($v as $k=>$item) {if (!is_string($k) || strlen($k)>100)nic_fail('Ungültiges Einstellungsfeld.');$check($item,$depth+1);} }
        elseif (!is_string($v) && !is_bool($v) && !is_int($v) && !is_float($v) && $v !== null) nic_fail('Ungültiger Einstellungswert.');
        elseif (is_string($v) && (strlen($v)>400000 || !preg_match('//u',$v))) nic_fail('Einstellungswert zu lang oder ungültig.');
    };
    $check($s);
    if (strlen(json_encode($s, JSON_THROW_ON_ERROR)) > 4000000) nic_fail('Einstellungen zu groß.');
    return $s;
}
function nic_run(): void {
    $c = nic_config();
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    $method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
    $origins = $c['allowed_origins'] ?? [];
    if ($origin !== '') {
        if (!in_array($origin, $origins, true)) nic_fail('Dieser Ursprung ist nicht freigegeben.', 403);
        header('Access-Control-Allow-Origin: ' . $origin); header('Vary: Origin');
        header('Access-Control-Allow-Credentials: true');
        header('Access-Control-Allow-Headers: Content-Type, X-NIC-Request, X-NIC-CSRF');
        header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    }
    if ($method === 'OPTIONS') { http_response_code(204); return; }
    if (!in_array($method, ['GET','POST'], true)) nic_fail('Methode nicht erlaubt.', 405);
    if ($method === 'POST' && ($origin === '' || ($_SERVER['HTTP_X_NIC_REQUEST'] ?? '') !== '1')) nic_fail('Unbestätigte Anfrage.', 403);
    if (empty($_SERVER['HTTPS']) || $_SERVER['HTTPS'] === 'off') nic_fail('HTTPS ist erforderlich.', 400);
    $route = $_GET['r'] ?? 'health';
    if (!is_string($route)) nic_fail('Ungültige Route.');
    $input = [];
    if ($method === 'POST') {
        if (!str_starts_with(strtolower($_SERVER['CONTENT_TYPE'] ?? ''), 'application/json')) nic_fail('JSON erforderlich.', 415);
        $body = file_get_contents('php://input', false, null, 0, 4000001);
        if ($body === false || strlen($body)>4000000) nic_fail('Anfrage zu groß.', 413);
        try { $input = json_decode($body, true, 16, JSON_THROW_ON_ERROR); } catch (JsonException) { nic_fail('Ungültige JSON-Anfrage.'); }
        if (!is_array($input)) nic_fail('Ungültige Anfrage.');
    }
    $db = nic_db($c);
    if ($route === 'health' && $method === 'GET') {
        $ready = false;
        try { $ready = (bool)nic_query($db, 'SELECT id FROM nic_settings WHERE id=1')->fetchColumn(); } catch (PDOException) {}
        nic_reply(['ok'=>true,'ready'=>$ready]);
    }
    if ($route === 'setup' && $method === 'POST') {
        if (!is_string($input['key'] ?? null) || !hash_equals($c['setup_key'], $input['key'])) nic_fail('Einrichtungsschlüssel ungültig.', 403);
        // Database advisory lock prevents simultaneous first-admin bootstraps.
        if ((int)nic_query($db,"SELECT GET_LOCK('nic_initial_setup',5)")->fetchColumn()!==1) nic_fail('Einrichtung läuft bereits.',409);
        try {
            foreach (explode(';', file_get_contents(__DIR__ . '/schema.sql')) as $sql) if (trim($sql)!=='') $db->exec($sql);
            if (nic_query($db, 'SELECT id FROM nic_settings WHERE id=1')->fetchColumn()) nic_fail('Die Einrichtung wurde bereits abgeschlossen.', 409);
            $admin = $c['admin']; $email=nic_email($admin['email']);$first=nic_name($admin['first_name']);$last=nic_name($admin['last_name']);
            $initial=nic_clean_settings(json_decode(file_get_contents(__DIR__.'/initial-settings.json'),true,16,JSON_THROW_ON_ERROR));
            $initial['access']=['calculators'=>true,'pdfDownload'=>true,'pdfShare'=>true];
            $db->beginTransaction();$id=bin2hex(random_bytes(16));
            nic_query($db,'INSERT INTO nic_users(id,email,first_name,last_name,role,created_at) VALUES (?,?,?,?,\'admin\',?)',[$id,$email,$first,$last,nic_now()]);
            nic_query($db,'INSERT INTO nic_settings(id,payload,revision,updated_by,updated_at) VALUES (1,?,1,?,?)',[json_encode($initial,JSON_THROW_ON_ERROR),$id,nic_now()]);
            nic_audit($db,$id,'setup');$db->commit();
        } finally { nic_query($db,"SELECT RELEASE_LOCK('nic_initial_setup')"); }
        nic_reply(['ok'=>true]);
    }
    if ($route==='settings' && $method==='GET') {
        $row=nic_query($db,'SELECT payload,revision FROM nic_settings WHERE id=1')->fetch(PDO::FETCH_ASSOC);
        if (!$row) nic_fail('Die Einrichtung ist noch nicht abgeschlossen.',503);
        nic_reply(['settings'=>json_decode($row['payload'],true,16,JSON_THROW_ON_ERROR),'revision'=>(int)$row['revision']]);
    }
    if ($route==='me' && $method==='GET') {
        $u=nic_session($db,$c,false);
        nic_reply(['user'=>$u,'csrf'=>$u?nic_hash('csrf|'.$_COOKIE['__Host-nic_session'],$c):null]);
    }
    if ($route==='request-code' && $method==='POST') {
        $email=nic_email($input['email']??null);
        nic_limit($db,$c,'email', $email,600,4);
        nic_limit($db,$c,'ip',$_SERVER['REMOTE_ADDR']??'',900,20);
        $first=$last='';
        if (($input['register']??false)===true) {$first=nic_name($input['first_name']??null);$last=nic_name($input['last_name']??null);}
        $u=nic_query($db,'SELECT id,status FROM nic_users WHERE email=?',[$email])->fetch(PDO::FETCH_ASSOC);
        if (!$u && ($input['register']??false)===true) {
            $id=bin2hex(random_bytes(16));
            nic_query($db,'INSERT IGNORE INTO nic_users(id,email,first_name,last_name,created_at) VALUES (?,?,?,?,?)',[$id,$email,$first,$last,nic_now()]);
            $u=nic_query($db,'SELECT id,status FROM nic_users WHERE email=?',[$email])->fetch(PDO::FETCH_ASSOC);
        }
        $challenge=bin2hex(random_bytes(32));
        if ($u && $u['status']==='active') {
            $code=(string)random_int(10000000,99999999);
            $db->beginTransaction();
            nic_query($db,'SELECT id FROM nic_users WHERE id=? FOR UPDATE',[$u['id']]);
            nic_query($db,'DELETE FROM nic_challenges WHERE user_id=?',[$u['id']]);
            nic_query($db,'INSERT INTO nic_challenges(id,user_id,code_hash,expires_at,created_at) VALUES (?,?,?,?,?)',[$challenge,$u['id'],nic_hash($challenge.'|'.$code,$c),nic_now(600),nic_now()]);
            $db->commit();
            try {nic_send_code($c['smtp'],$email,$code);} catch (Throwable $e) {nic_query($db,'DELETE FROM nic_challenges WHERE id=?',[$challenge]);throw $e;}
        }
        // Unknown and blocked accounts deliberately get the same response.
        nic_reply(['ok'=>true,'challenge'=>$challenge,'message'=>'Wenn das Konto nutzbar ist, erhältst du einen Code per E-Mail.']);
    }
    if ($route==='verify-code' && $method==='POST') {
        nic_limit($db,$c,'verify-ip',$_SERVER['REMOTE_ADDR']??'',900,40);
        $id=$input['challenge']??'';$code=$input['code']??'';
        if(!is_string($id)||!is_string($code)||!preg_match('/^[a-f0-9]{64}$/D',$id)||!preg_match('/^[0-9]{8}$/D',$code))nic_fail('Code ungültig oder abgelaufen.',401);
        $db->beginTransaction();
        $ch=nic_query($db,'SELECT * FROM nic_challenges WHERE id=? FOR UPDATE',[$id])->fetch(PDO::FETCH_ASSOC);
        if (!$ch || $ch['expires_at']<nic_now() || (int)$ch['attempts']>=5) {$db->commit();nic_fail('Code ungültig oder abgelaufen.',401);}
        if (!hash_equals($ch['code_hash'],nic_hash($id.'|'.$code,$c))) {
            nic_query($db,'UPDATE nic_challenges SET attempts=attempts+1 WHERE id=?',[$id]);$db->commit();nic_fail('Code ungültig oder abgelaufen.',401);
        }
        $u=nic_query($db,'SELECT * FROM nic_users WHERE id=? FOR UPDATE',[$ch['user_id']])->fetch(PDO::FETCH_ASSOC);
        if (!$u||$u['status']!=='active'){$db->commit();nic_fail('Konto nicht verfügbar.',401);}
        nic_query($db,'DELETE FROM nic_challenges WHERE id=?',[$id]);
        nic_query($db,'UPDATE nic_users SET verified_at=COALESCE(verified_at,?) WHERE id=?',[nic_now(),$u['id']]);
        $token=bin2hex(random_bytes(32));$csrf=nic_hash('csrf|'.$token,$c);
        nic_query($db,'INSERT INTO nic_sessions(token_hash,user_id,csrf_hash,expires_at,created_at) VALUES (?,?,?,?,?)',[nic_hash('session|'.$token,$c),$u['id'],hash('sha256',$csrf),nic_now(86400*14),nic_now()]);
        $db->commit();setcookie('__Host-nic_session',$token,['expires'=>time()+86400*14,'path'=>'/','secure'=>true,'httponly'=>true,'samesite'=>'Lax']);
        unset($u['verified_at'],$u['created_at']);nic_reply(['user'=>$u,'csrf'=>$csrf]);
    }
    if ($route==='logout' && $method==='POST') {
        nic_session($db,$c);
        nic_query($db,'DELETE FROM nic_sessions WHERE token_hash=?',[nic_hash('session|'.$_COOKIE['__Host-nic_session'],$c)]);
        setcookie('__Host-nic_session','',['expires'=>1,'path'=>'/','secure'=>true,'httponly'=>true,'samesite'=>'Lax']);nic_reply(['ok'=>true]);
    }
    if ($route==='authorize' && $method==='POST') {
        $row=nic_query($db,'SELECT payload FROM nic_settings WHERE id=1')->fetchColumn();
        if(!$row)nic_fail('Einrichtung fehlt.',503);
        $s=json_decode($row,true,16,JSON_THROW_ON_ERROR);$action=$input['action']??'';
        if(!in_array($action,['calculators','pdfDownload','pdfShare'],true))nic_fail('Unbekannte Funktion.');
        if(($s['access']['calculators']??true)!==true || ($s['access'][$action]??true)!==true)nic_session($db,$c);
        nic_reply(['ok'=>true]);
    }
    $admin=nic_admin($db,$c);
    if ($route==='settings' && $method==='POST') {
        $s=nic_clean_settings($input['settings']??null);$revision=$input['revision']??null;
        if(!is_int($revision)||$revision<1)nic_fail('Versionsnummer fehlt.');
        $db->beginTransaction();
        $changed=nic_query($db,'UPDATE nic_settings SET payload=?,revision=revision+1,updated_by=?,updated_at=? WHERE id=1 AND revision=?',[json_encode($s,JSON_THROW_ON_ERROR),$admin['id'],nic_now(),$revision]);
        if(!$changed->rowCount()){$db->rollBack();nic_fail('Die Einstellungen wurden inzwischen geändert. Bitte neu laden.',409);}
        nic_audit($db,$admin['id'],'settings');$db->commit();nic_reply(['ok'=>true,'revision'=>$revision+1,'settings'=>$s]);
    }
    if ($route==='users' && $method==='GET') {
        $page=max(0,min(100000,(int)($_GET['page']??0)));$offset=$page*50;
        $users=nic_query($db,'SELECT id,email,first_name,last_name,role,status,verified_at,created_at FROM nic_users ORDER BY created_at,id LIMIT 51 OFFSET '.$offset)->fetchAll(PDO::FETCH_ASSOC);
        $more=count($users)>50;nic_reply(['users'=>array_slice($users,0,50),'more'=>$more]);
    }
    if ($route==='user-action' && $method==='POST') {
        $target=$input['id']??'';$action=$input['action']??'';
        if(!is_string($target)||!preg_match('/^[a-f0-9]{32}$/D',$target)||!in_array($action,['block','unblock','delete'],true))nic_fail('Ungültige Benutzeraktion.');
        $db->beginTransaction();
        // Serialize all administrative deletions/blocks with the settings singleton.
        nic_query($db,'SELECT id FROM nic_settings WHERE id=1 FOR UPDATE');
        $u=nic_query($db,'SELECT id,role,status FROM nic_users WHERE id=? FOR UPDATE',[$target])->fetch(PDO::FETCH_ASSOC);
        if(!$u){$db->rollBack();nic_fail('Benutzer nicht gefunden.',404);}
        if($target===$admin['id']){$db->rollBack();nic_fail('Das eigene Admin-Konto kann hier nicht gesperrt oder gelöscht werden.',409);}
        if($u['role']==='admin' && $u['status']==='active' && $action!=='unblock') {
            $count=(int)nic_query($db,"SELECT COUNT(*) FROM nic_users WHERE role='admin' AND status='active'")->fetchColumn();
            if($count<=1){$db->rollBack();nic_fail('Der letzte aktive Administrator muss erhalten bleiben.',409);}
        }
        nic_audit($db,$admin['id'],$action,$target);
        if($action==='delete') {
            nic_query($db,'UPDATE nic_settings SET updated_by=NULL WHERE updated_by=?',[$target]);
            nic_query($db,'UPDATE nic_audit SET actor_id=NULL WHERE actor_id=?',[$target]);
            nic_query($db,'UPDATE nic_audit SET target_id=NULL WHERE target_id=?',[$target]);
            nic_query($db,'DELETE FROM nic_users WHERE id=?',[$target]);
        } else {
            nic_query($db,'UPDATE nic_users SET status=? WHERE id=?',[$action==='block'?'blocked':'active',$target]);
            if($action==='block') {nic_query($db,'DELETE FROM nic_sessions WHERE user_id=?',[$target]);nic_query($db,'DELETE FROM nic_challenges WHERE user_id=?',[$target]);}
        }
        $db->commit();nic_reply(['ok'=>true]);
    }
    nic_fail('Nicht gefunden.',404);
}
