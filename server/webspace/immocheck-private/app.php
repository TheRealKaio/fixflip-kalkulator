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
function nic_statistics_table(PDO $db): void {
    $db->exec("CREATE TABLE IF NOT EXISTS nic_statistics_daily (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,stat_date DATE NOT NULL,event_name VARCHAR(24) NOT NULL,dimension_hash CHAR(64) NOT NULL,section_name VARCHAR(16) NOT NULL DEFAULT '',calculator VARCHAR(16) NOT NULL DEFAULT '',device VARCHAR(32) NOT NULL DEFAULT '',operating_system VARCHAR(40) NOT NULL DEFAULT '',source VARCHAR(120) NOT NULL DEFAULT '',hits BIGINT UNSIGNED NOT NULL DEFAULT 0,UNIQUE KEY nic_statistics_event_bucket(stat_date,event_name,dimension_hash),INDEX(stat_date),INDEX(event_name,stat_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
}
function nic_remove_account(PDO $db, string $id): void {
    nic_query($db,'UPDATE nic_settings SET updated_by=NULL WHERE updated_by=?',[$id]);
    nic_query($db,'UPDATE nic_audit SET actor_id=NULL WHERE actor_id=?',[$id]);
    nic_query($db,'UPDATE nic_audit SET target_id=NULL WHERE target_id=?',[$id]);
    nic_query($db,'DELETE FROM nic_users WHERE id=?',[$id]);
}
function nic_email_change_table(PDO $db): void {
    nic_query($db,"CREATE TABLE IF NOT EXISTS nic_email_changes (user_id CHAR(32) PRIMARY KEY, old_email VARCHAR(254) NOT NULL, new_email VARCHAR(254) NOT NULL, token_hash CHAR(64) UNIQUE NULL, code_hash CHAR(64) NOT NULL, stage VARCHAR(16) NOT NULL, attempts INT NOT NULL DEFAULT 0, expires_at DATETIME NOT NULL, FOREIGN KEY (user_id) REFERENCES nic_users(id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
}
function nic_email_change_dispatch(PDO $db, array $c, string $userId): array {
    nic_limit($db,$c,'email-change-send',$userId,3600,5);
    $db->beginTransaction();
    $change=nic_query($db,'SELECT * FROM nic_email_changes WHERE user_id=? FOR UPDATE',[$userId])->fetch(PDO::FETCH_ASSOC);
    $u=nic_query($db,'SELECT email,status FROM nic_users WHERE id=? FOR UPDATE',[$userId])->fetch(PDO::FETCH_ASSOC);
    if(!$change||!$u||$u['status']!=='active'||!nic_email_change_valid($change,$u['email'],'approved')){$db->rollBack();nic_fail('Bitte zuerst die bisherige Adresse bestätigen oder den Vorgang neu starten.',400);}
    $code=(string)random_int(10000000,99999999);$hash=nic_hash('email-change-code|'.$userId.'|'.$code,$c);
    nic_query($db,'UPDATE nic_email_changes SET code_hash=?,expires_at=? WHERE user_id=?',[$hash,nic_now(600),$userId]);$db->commit();
    try{nic_send_message($c['smtp'],$change['new_email'],'Dein ImmoCheck-Bestätigungscode',"Dein Bestätigungscode für die neue E-Mail-Adresse lautet: $code\n\nGib ihn innerhalb von 10 Minuten in deinem Nutzerkonto unter Email ändern ein. Nur dieser zuletzt angeforderte Code gilt.");}
    catch(Throwable $e){error_log('ImmoCheck: email change SMTP submission failed');nic_fail('Die bisherige Adresse ist bestätigt, aber der Versand an die neue Adresse konnte nicht bestätigt werden. Bitte im Nutzerkonto Code erneut senden wählen.',502);}
    return ['ok'=>true,'smtpAccepted'=>true,'recipient'=>$change['new_email']];
}
function nic_complete_email_change(PDO $db, string $userId, string $oldEmail, string $newEmail): string {
    $email=nic_email($newEmail);
    $changed=nic_query($db,'UPDATE nic_users SET email=?,verified_at=? WHERE id=? AND email=? AND status=?',[$email,nic_now(),$userId,$oldEmail,'active']);
    if($changed->rowCount()!==1) throw new RuntimeException('Email change was not saved');
    if(nic_query($db,'SELECT email FROM nic_users WHERE id=?',[$userId])->fetchColumn()!==$email) throw new RuntimeException('Email change verification failed');
    nic_query($db,'DELETE FROM nic_sessions WHERE user_id=?',[$userId]);
    nic_query($db,'DELETE FROM nic_challenges WHERE user_id=?',[$userId]);
    nic_query($db,'DELETE FROM nic_email_changes WHERE user_id=?',[$userId]);
    return $email;
}
function nic_email_change_valid(array $change, string $email, string $stage): bool {
    return $change['old_email']===$email && $change['stage']===$stage && $change['expires_at']>=nic_now() && (int)$change['attempts']<5;
}
function nic_auth_allowed(array $settings, ?array $user, bool $register): bool {
    if (($user['role'] ?? '') === 'admin') return true;
    if (($settings['access']['loginBlocked'] ?? false) === true) return false;
    if ($register && ($settings['access']['registrationBlocked'] ?? false) === true) return false;
    return true;
}
function nic_auth_settings(PDO $db): array {
    $payload=nic_query($db,'SELECT payload FROM nic_settings WHERE id=1')->fetchColumn();
    if (!$payload) nic_fail('Einrichtung fehlt.',503);
    return json_decode($payload,true,16,JSON_THROW_ON_ERROR);
}
function nic_clean_settings(mixed $raw): array {
    if (!is_array($raw) || ($raw['version'] ?? null) !== 1) nic_fail('Ungültige Einstellungen.');
    $keys = ['version','company','layout','social','meta','favicon','websiteLogo','appleTouchIcon','imageAlts','sharing','reporting','legal','access','contentSections'];
    $s = array_intersect_key($raw, array_flip($keys));
    foreach (['company','layout','social','meta','imageAlts','sharing','reporting','legal','access'] as $key) if (isset($s[$key]) && !is_array($s[$key])) nic_fail('Ungültiges Einstellungsfeld: ' . $key);
    $s['access'] = $s['access'] ?? [];
    foreach (['registrationBlocked','loginBlocked','calculators','pdfDownload','pdfShare','budgetInsightsLoginRequired'] as $key) {
        $value = $s['access'][$key] ?? !in_array($key,['registrationBlocked','loginBlocked','budgetInsightsLoginRequired'],true);
        if (array_key_exists($key,$s['access']) && !is_bool($s['access'][$key])) nic_fail('Ungültige Zugangsregel.');
        $s['access'][$key] = $value;
    }
    $s['access'] = array_intersect_key($s['access'], array_flip(['registrationBlocked','loginBlocked','calculators','pdfDownload','pdfShare','budgetInsightsLoginRequired']));
    $sections = $s['contentSections'] ?? [];
    if (!is_array($sections) || count($sections) > 200) nic_fail('Ungültige Box-Einstellungen.');
    foreach ($sections as $key => $rule) {
        if (!is_string($key) || !preg_match('/^[a-z0-9][a-z0-9._-]{0,120}$/', $key) || !is_array($rule)) nic_fail('Ungültige Box-Einstellung.');
        foreach (['visible','guestAllowed'] as $field) {
            if (array_key_exists($field,$rule) && !is_bool($rule[$field])) nic_fail('Ungültige Box-Einstellung.');
            $rule[$field] = $rule[$field] ?? true;
        }
        $sections[$key] = array_intersect_key($rule, array_flip(['visible','guestAllowed']));
    }
    $s['contentSections'] = $sections;
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
        nic_reply(['ok'=>true,'ready'=>$ready,'version'=>'8.360']);
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
        nic_reply(['settings'=>json_decode($row['payload'],true,16,JSON_THROW_ON_ERROR),'revision'=>(int)$row['revision'],'authControlsVersion'=>1,'contentSectionsVersion'=>1]);
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
        $u=nic_query($db,'SELECT id,status,role,verified_at FROM nic_users WHERE email=?',[$email])->fetch(PDO::FETCH_ASSOC);
        if (!nic_auth_allowed(nic_auth_settings($db),$u?:null,!$u || empty($u['verified_at']))) nic_fail('Registrierung oder Anmeldung ist derzeit gesperrt.',403);
        if (!$u && ($input['register']??false)===true) {
            $id=bin2hex(random_bytes(16));
            nic_query($db,'INSERT IGNORE INTO nic_users(id,email,first_name,last_name,created_at) VALUES (?,?,?,?,?)',[$id,$email,$first,$last,nic_now()]);
            $u=nic_query($db,'SELECT id,status,role,verified_at FROM nic_users WHERE email=?',[$email])->fetch(PDO::FETCH_ASSOC);
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
        if (!nic_auth_allowed(nic_auth_settings($db),$u,empty($u['verified_at']))) {$db->commit();nic_fail('Registrierung oder Anmeldung ist derzeit gesperrt.',403);}
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
    if ($route==='email-change-status' && $method==='GET') {
        $u=nic_session($db,$c);nic_email_change_table($db);
        $change=nic_query($db,'SELECT * FROM nic_email_changes WHERE user_id=?',[$u['id']])->fetch(PDO::FETCH_ASSOC);
        $valid=$change && nic_email_change_valid($change,$u['email'],$change['stage']);
        nic_reply(['change'=>$valid?['email'=>$change['new_email'],'stage'=>$change['stage']]:null]);
    }
    if ($route==='email-change-start' && $method==='POST') {
        $u=nic_session($db,$c);$email=nic_email($input['email']??null);
        if ($email===$u['email']) nic_fail('Bitte eine andere E-Mail-Adresse eingeben.');
        nic_limit($db,$c,'email-change',$u['id'],3600,3);
        if (nic_query($db,'SELECT id FROM nic_users WHERE email=?',[$email])->fetchColumn()) nic_fail('Diese E-Mail-Adresse kann nicht verwendet werden.',409);
        nic_email_change_table($db);
        $token=bin2hex(random_bytes(32));$hash=nic_hash('email-change|'.$token,$c);
        nic_query($db,"INSERT INTO nic_email_changes(user_id,old_email,new_email,token_hash,code_hash,stage,attempts,expires_at) VALUES (?,?,?,?,'','pending',0,?) ON DUPLICATE KEY UPDATE old_email=VALUES(old_email),new_email=VALUES(new_email),token_hash=VALUES(token_hash),code_hash='',stage='pending',attempts=0,expires_at=VALUES(expires_at)",[$u['id'],$u['email'],$email,$hash,nic_now(1800)]);
        $link='https://www.neustart-immocheck.de/email-change.html#token='.$token;
        try {nic_send_message($c['smtp'],$u['email'],'E-Mail-Änderung bestätigen',"Möchtest du deine E-Mail-Adresse zu ".$email." ändern?\n\nÖffne diesen Link und bestätige die Änderung innerhalb von 30 Minuten:\n".$link."\n\nWenn du die Änderung nicht angefordert hast, bestätige sie nicht. Deine bisherige Adresse bleibt gültig.");}
        catch(Throwable $e){nic_query($db,'DELETE FROM nic_email_changes WHERE user_id=? AND token_hash=?',[$u['id'],$hash]);throw $e;}
        nic_reply(['ok'=>true]);
    }
    if ($route==='email-change-approve' && $method==='POST') {
        nic_limit($db,$c,'email-change-approve-ip',$_SERVER['REMOTE_ADDR']??'',900,20);
        $token=$input['token']??'';if(!is_string($token)||!preg_match('/^[a-f0-9]{64}$/D',$token))nic_fail('Bestätigung ungültig oder abgelaufen.',400);
        $db->beginTransaction();
        $change=nic_query($db,'SELECT * FROM nic_email_changes WHERE token_hash=? FOR UPDATE',[nic_hash('email-change|'.$token,$c)])->fetch(PDO::FETCH_ASSOC);
        if(!$change){$db->rollBack();nic_fail('Bestätigung ungültig oder abgelaufen.',400);}
        $u=nic_query($db,'SELECT email,status FROM nic_users WHERE id=? FOR UPDATE',[$change['user_id']])->fetch(PDO::FETCH_ASSOC);
        if(!$u||$u['status']!=='active'||!nic_email_change_valid($change,$u['email'],'pending')){$db->rollBack();nic_fail('Bestätigung ungültig oder abgelaufen.',400);}
        nic_query($db,"UPDATE nic_email_changes SET stage='approved',token_hash=NULL,expires_at=? WHERE user_id=?",[nic_now(600),$change['user_id']]);
        $db->commit();
        nic_reply(nic_email_change_dispatch($db,$c,$change['user_id']));
    }
    if ($route==='email-change-resend' && $method==='POST') {
        $u=nic_session($db,$c);nic_reply(nic_email_change_dispatch($db,$c,$u['id']));
    }
    if ($route==='email-change-finish' && $method==='POST') {
        $u=nic_session($db,$c);$code=$input['code']??'';
        nic_limit($db,$c,'email-change-finish',$u['id'],900,20);
        if(!is_string($code)||!preg_match('/^[0-9]{8}$/D',$code))nic_fail('Bitte den achtstelligen Code eingeben.');
        $db->beginTransaction();
        $change=nic_query($db,'SELECT * FROM nic_email_changes WHERE user_id=? FOR UPDATE',[$u['id']])->fetch(PDO::FETCH_ASSOC);
        $current=nic_query($db,'SELECT email,status FROM nic_users WHERE id=? FOR UPDATE',[$u['id']])->fetch(PDO::FETCH_ASSOC);
        if(!$change||!$current||$current['status']!=='active'||!nic_email_change_valid($change,$current['email'],'approved')){$db->rollBack();nic_fail('Bitte zuerst über deine bisherige Adresse bestätigen. Der Vorgang darf nicht abgelaufen sein.',400);}
        if(!hash_equals($change['code_hash'],nic_hash('email-change-code|'.$u['id'].'|'.$code,$c))){nic_query($db,'UPDATE nic_email_changes SET attempts=attempts+1 WHERE user_id=?',[$u['id']]);$db->commit();nic_fail('Code ungültig oder abgelaufen.',400);}
        if(nic_query($db,'SELECT id FROM nic_users WHERE email=?',[$change['new_email']])->fetchColumn()){$db->rollBack();nic_fail('Diese E-Mail-Adresse kann nicht verwendet werden.',409);}
        $newEmail=nic_complete_email_change($db,$u['id'],$change['old_email'],$change['new_email']);
        $db->commit();
        setcookie('__Host-nic_session','',['expires'=>1,'path'=>'/','secure'=>true,'httponly'=>true,'samesite'=>'Lax']);
        // Respond immediately after commit. SMTP must not time out an already completed change.
        nic_reply(['ok'=>true,'email'=>$newEmail,'loggedOut'=>true]);
    }
    if ($route==='profile' && $method==='POST') {
        $u=nic_session($db,$c);
        $first=nic_name($input['first_name']??null);$last=nic_name($input['last_name']??null);
        nic_query($db,'UPDATE nic_users SET first_name=?,last_name=? WHERE id=?',[$first,$last,$u['id']]);
        $u['first_name']=$first;$u['last_name']=$last;nic_reply(['user'=>$u]);
    }
    if ($route==='delete-own-account' && $method==='POST') {
        $u=nic_session($db,$c);
        if (($input['confirm']??false)!==true) nic_fail('Bitte Löschung bestätigen.');
        if ($u['role']==='admin') nic_fail('Admin-Konten werden über die Benutzerverwaltung verwaltet.',403);
        $db->beginTransaction();
        nic_query($db,'SELECT id FROM nic_settings WHERE id=1 FOR UPDATE');
        $current=nic_query($db,'SELECT role,status FROM nic_users WHERE id=? FOR UPDATE',[$u['id']])->fetch(PDO::FETCH_ASSOC);
        if (!$current || $current['role']==='admin' || $current['status']!=='active') {$db->rollBack();nic_fail('Konto nicht verfügbar.',403);}
        nic_remove_account($db,$u['id']);
        $db->commit();
        setcookie('__Host-nic_session','',['expires'=>1,'path'=>'/','secure'=>true,'httponly'=>true,'samesite'=>'Lax']);nic_reply(['ok'=>true]);
    }
    if ($route==='statistics-event' && $method==='POST') {
        $event=$input['event']??'';$section=$input['section']??'';$calculator=$input['calculator']??'';
        $events=['page_view','calculator_use','calculate','pdf_download','pdf_share'];$sections=['website','company','budget','own','rent','flip'];$calculators=['budget','own','rent','flip','finance'];
        if(!is_string($event)||!in_array($event,$events,true)||!is_string($section)||!in_array($section,$sections,true))nic_fail('Ungültiges Statistikereignis.');
        if($calculator!==null&&$calculator!==''&&(!is_string($calculator)||!in_array($calculator,$calculators,true)))nic_fail('Ungültiger Kalkulator.');
        $calculator=is_string($calculator)?$calculator:'';
        $dimension=static function(mixed $value,int $max,string $fallback):string{if(!is_string($value)||!preg_match('//u',$value))return $fallback;$value=trim($value);if($value===''||strlen($value)>$max||preg_match('/[\\x00-\\x1f\\x7f]/u',$value))return $fallback;return $value;};
        $device=$event==='page_view'?$dimension($input['device']??null,32,'Unbekannt'):'';$system=$event==='page_view'?$dimension($input['system']??null,40,'Unbekannt'):'';$source=$event==='page_view'?$dimension($input['source']??null,120,'Direkt / unbekannt'):'';
        nic_limit($db,$c,'statistics-event',$_SERVER['REMOTE_ADDR']??'',60,120);nic_statistics_table($db);$today=(new DateTimeImmutable('now',new DateTimeZone('Europe/Berlin')))->format('Y-m-d');
        $dimensionHash=hash('sha256',json_encode([$section,$calculator,$device,$system,$source],JSON_THROW_ON_ERROR));nic_query($db,'INSERT INTO nic_statistics_daily(stat_date,event_name,dimension_hash,section_name,calculator,device,operating_system,source,hits) VALUES (?,?,?,?,?,?,?,?,1) ON DUPLICATE KEY UPDATE hits=hits+1',[$today,$event,$dimensionHash,$section,$calculator,$device,$system,$source]);
        nic_reply(['ok'=>true]);
    }
    $admin=nic_admin($db,$c);
    if ($route==='statistics' && $method==='GET') {
        nic_statistics_table($db);$days=(int)($_GET['days']??30);if(!in_array($days,[7,30,90],true))nic_fail('Ungültiger Statistikzeitraum.');
        $today=new DateTimeImmutable('today',new DateTimeZone('Europe/Berlin'));$from=$today->modify('-'.($days-1).' days')->format('Y-m-d');
        $rows=nic_query($db,'SELECT event_name,calculator,device,operating_system,source,SUM(hits) AS hits FROM nic_statistics_daily WHERE stat_date>=? AND stat_date<=? GROUP BY event_name,calculator,device,operating_system,source',[$from,$today->format('Y-m-d')])->fetchAll(PDO::FETCH_ASSOC);
        $events=['page_view'=>0,'calculator_use'=>0,'calculate'=>0,'pdf_download'=>0,'pdf_share'=>0];$calculators=[];foreach(['budget','own','rent','flip','finance'] as $key)$calculators[$key]=['calculator_use'=>0,'calculate'=>0,'pdf_download'=>0,'pdf_share'=>0];$breakdowns=['devices'=>[],'systems'=>[],'sources'=>[]];
        foreach($rows as $row){$event=$row['event_name'];$count=(int)$row['hits'];if(array_key_exists($event,$events))$events[$event]+=$count;$key=$row['calculator'];if(isset($calculators[$key][$event]))$calculators[$key][$event]+=$count;if($event==='page_view'){foreach(['device'=>'devices','operating_system'=>'systems','source'=>'sources'] as $field=>$target){$value=$row[$field];if($value!=='')$breakdowns[$target][$value]=($breakdowns[$target][$value]??0)+$count;}}}
        nic_reply(['events'=>$events,'calculators'=>$calculators,'devices'=>$breakdowns['devices'],'systems'=>$breakdowns['systems'],'sources'=>$breakdowns['sources'],'from'=>$from,'through'=>$today->format('Y-m-d')]);
    }
    if ($route==='statistics-reset' && $method==='POST') {
        nic_statistics_table($db);$db->beginTransaction();nic_query($db,'SELECT id FROM nic_settings WHERE id=1 FOR UPDATE');$deleted=$db->exec('DELETE FROM nic_statistics_daily');nic_audit($db,$admin['id'],'statistics-reset');$db->commit();nic_reply(['ok'=>true,'deleted'=>max(0,(int)$deleted)]);
    }
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
    if ($route==='users-import' && $method==='POST') {
        $rows=$input['users']??null;
        if(!is_array($rows)||count($rows)<1||count($rows)>2000)nic_fail('Der Import muss 1 bis 2.000 Nutzerkonten enthalten.');
        $users=[];$emails=[];
        foreach($rows as $row){
            if(!is_array($row))nic_fail('Ungültiger Datensatz in der Importdatei.');
            $email=nic_email($row['email']??null);$first=nic_name($row['first_name']??null);$last=nic_name($row['last_name']??null);
            if(isset($emails[$email]))nic_fail('Eine E-Mail-Adresse ist in der Importdatei mehrfach vorhanden.');
            $emails[$email]=true;$users[]=['email'=>$email,'first_name'=>$first,'last_name'=>$last];
        }
        $db->beginTransaction();
        try{
            nic_query($db,'SELECT id FROM nic_settings WHERE id=1 FOR UPDATE');
            $created=0;$updated=0;
            foreach($users as $row){
                $id=nic_query($db,'SELECT id FROM nic_users WHERE email=? FOR UPDATE',[$row['email']])->fetchColumn();
                if($id!==false){
                    nic_query($db,'UPDATE nic_users SET first_name=?,last_name=? WHERE id=?',[$row['first_name'],$row['last_name'],$id]);$updated++;continue;
                }
                nic_query($db,'INSERT INTO nic_users(id,email,first_name,last_name,role,status,verified_at,created_at) VALUES (?,?,?,?,?,?,NULL,?)',[bin2hex(random_bytes(16)),$row['email'],$row['first_name'],$row['last_name'],'user','active',nic_now()]);$created++;
            }
            nic_audit($db,$admin['id'],'users-import');$db->commit();
        }catch(Throwable $error){if($db->inTransaction())$db->rollBack();throw $error;}
        nic_reply(['ok'=>true,'created'=>$created,'updated'=>$updated]);
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
            nic_remove_account($db,$target);
        } else {
            nic_query($db,'UPDATE nic_users SET status=? WHERE id=?',[$action==='block'?'blocked':'active',$target]);
            if($action==='block') {nic_query($db,'DELETE FROM nic_sessions WHERE user_id=?',[$target]);nic_query($db,'DELETE FROM nic_challenges WHERE user_id=?',[$target]);}
        }
        $db->commit();nic_reply(['ok'=>true]);
    }
    nic_fail('Nicht gefunden.',404);
}
