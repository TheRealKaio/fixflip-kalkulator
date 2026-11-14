<?php
declare(strict_types=1);
require dirname(__DIR__) . '/webspace/immocheck-private/app.php';

class ImportFixturePDO extends PDO {
    public function prepare(string $query, array $options = []): PDOStatement|false {
        return parent::prepare(preg_replace('/\s+FOR UPDATE\b/', '', $query), $options);
    }
}
$db = new ImportFixturePDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$db->exec('CREATE TABLE nic_users(id TEXT PRIMARY KEY,email TEXT COLLATE NOCASE UNIQUE,first_name TEXT,last_name TEXT,role TEXT,status TEXT,verified_at TEXT,created_at TEXT)');
$db->exec('CREATE TABLE nic_settings(id INTEGER PRIMARY KEY)');
$db->exec('INSERT INTO nic_settings VALUES (1)');
$db->exec('CREATE TABLE nic_audit(actor_id TEXT,action TEXT,target_id TEXT,created_at TEXT)');
nic_query($db,'INSERT INTO nic_users VALUES (?,?,?,?,?,?,?,?)',[str_repeat('1',32),'existing@example.test','Before','Name','admin','blocked','2025-01-01','2025-01-01']);
nic_query($db,'INSERT INTO nic_users VALUES (?,?,?,?,?,?,?,?)',[str_repeat('2',32),'untouched@example.test','Unchanged','Person','user','active','2025-01-01','2025-01-01']);
$destination = $argv[2];
register_shutdown_function(static function () use ($db, $destination): void {
    file_put_contents($destination, json_encode(['users'=>$db->query('SELECT * FROM nic_users ORDER BY email')->fetchAll(PDO::FETCH_ASSOC),
        'audit'=>(int)$db->query('SELECT COUNT(*) FROM nic_audit')->fetchColumn()], JSON_THROW_ON_ERROR));
});
$mode = $argv[1];
$rows = [['email'=>'EXISTING@example.test','first_name'=>'  José  ','last_name'=>'Müller'],
         ['email'=>'NEW@example.test','first_name'=>'Ana','last_name'=>'Gonçalves','role'=>'admin','status'=>'blocked','verified_at'=>'2000-01-01']];
if ($mode === 'duplicate') $rows[] = $rows[0];
if ($mode === 'invalid') $rows[1]['email'] = 'not-an-email';
if ($mode === 'too-many') $rows = array_fill(0,2001,$rows[0]);
if ($mode === 'rollback') {
    $db->exec("CREATE TRIGGER reject_fixture BEFORE INSERT ON nic_users WHEN NEW.email='fail@example.test' BEGIN SELECT RAISE(ABORT,'forced failure'); END");
    $rows[] = ['email'=>'fail@example.test','first_name'=>'Fail','last_name'=>'Fixture'];
}
$admin = ['id'=>str_repeat('1',32)];
$input = ['users'=>$rows]; $route = 'users-import'; $method = 'POST';
$source = file_get_contents(dirname(__DIR__) . '/webspace/immocheck-private/app.php');
$start = strpos($source, "    if (\$route==='users-import' && \$method==='POST') {");
$end = strpos($source, "    if (\$route==='user-action' && \$method==='POST') {", $start);
if ($start === false || $end === false) throw new RuntimeException('Import fixture route missing');
try { eval(substr($source, $start, $end-$start)); }
catch (Throwable $error) { echo json_encode(['error'=>'transaction rolled back']); }
