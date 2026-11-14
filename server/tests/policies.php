<?php
declare(strict_types=1);
require dirname(__DIR__).'/webspace/immocheck-private/app.php';
function check(bool $value,string $message): void {if(!$value)throw new RuntimeException($message);}
$mode=$argv[1]??'normal';
$c=['pepper'=>str_repeat('t',64)];
if($mode==='settings-invalid'){nic_clean_settings(['version'=>1,'access'=>['pdfShare'=>'false']]);throw new RuntimeException('invalid accepted');}
if($mode==='email-invalid'){nic_email("x@example.com\r\nBcc: y@example.com");throw new RuntimeException('header injection accepted');}
if($mode==='normal'){
 $change=['old_email'=>'old@example.test','stage'=>'pending','expires_at'=>nic_now(60),'attempts'=>0];
 check(nic_email_change_valid($change,'old@example.test','pending'),'pending old confirmation');
 check(!nic_email_change_valid($change,'old@example.test','approved'),'new code requires old approval');
 check(!nic_email_change_valid($change,'other@example.test','pending'),'changed old address invalidates request');
 check(!nic_email_change_valid(array_replace($change,['expires_at'=>nic_now(-60)]),'old@example.test','pending'),'expired request rejected');
 check(!nic_email_change_valid(array_replace($change,['attempts'=>5]),'old@example.test','pending'),'attempts capped');

 foreach ([false,true] as $registration) foreach ([false,true] as $login) {
  $rules=['access'=>['registrationBlocked'=>$registration,'loginBlocked'=>$login]];
  check(nic_auth_allowed($rules,['role'=>'admin'],true),'admin must always be allowed');
  check(nic_auth_allowed($rules,['role'=>'user'],false)===!$login,'existing user login policy');
  check(nic_auth_allowed($rules,null,true)===(!$login&&!$registration),'registration policy');
  check(nic_auth_allowed($rules,['role'=>'user'],true)===(!$login&&!$registration),'pending code registration policy');
 }

 $s=nic_clean_settings(['version'=>1,'secret'=>'must disappear','access'=>['pdfDownload'=>false,'pdfShare'=>true]]);
 check(!isset($s['secret']),'unknown top-level settings retained');check($s['access']['calculators']===true,'missing defaults');check($s['access']['pdfDownload']===false,'false lost');
 $content=['settlement'=>['title'=>'Mieterabrechnung','boxTitle'=>'Meine Box','description'=>'<p>Einleitung</p><h3>Mehr</h3><p>Text</p>']];
 $wire=nic_clean_settings(['version'=>1,'meta'=>['content'=>$content]]);
 check($wire['meta']['content']===$content,'legacy settings API must retain editable content transport');
 check(nic_email(' TEST@EXAMPLE.COM ')==='test@example.com','email normalization');check(nic_name(' Kai ')==='Kai','name trim');
 check(nic_hash('session|one',$c)!==nic_hash('session|two',$c),'hash separation');
 $test=new PDO('sqlite::memory:');$test->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);$test->exec('PRAGMA foreign_keys=ON');
 $test->exec('CREATE TABLE nic_users(id TEXT PRIMARY KEY);CREATE TABLE nic_sessions(user_id TEXT REFERENCES nic_users(id) ON DELETE CASCADE);CREATE TABLE nic_challenges(user_id TEXT REFERENCES nic_users(id) ON DELETE CASCADE);CREATE TABLE nic_settings(updated_by TEXT);CREATE TABLE nic_audit(actor_id TEXT,target_id TEXT)');
 $test->exec("INSERT INTO nic_users VALUES ('self'),('other');INSERT INTO nic_sessions VALUES ('self'),('other');INSERT INTO nic_challenges VALUES ('self'),('other');INSERT INTO nic_settings VALUES ('self');INSERT INTO nic_audit VALUES ('self','other'),('other','self')");
 $test->beginTransaction();nic_remove_account($test,'self');$test->commit();
 check($test->query('SELECT id FROM nic_users')->fetchColumn()==='other','other account must remain');
 foreach(['nic_sessions','nic_challenges'] as $table)check($test->query('SELECT user_id FROM '.$table)->fetchAll(PDO::FETCH_COLUMN)===['other'],'own tokens must be removed');
 check($test->query('SELECT updated_by FROM nic_settings')->fetchColumn()===null,'settings reference must be cleared');
 check((int)$test->query("SELECT COUNT(*) FROM nic_audit WHERE actor_id='self' OR target_id='self'")->fetchColumn()===0,'audit references must be cleared');
 $emailDb=new PDO('sqlite::memory:');$emailDb->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);
 $emailDb->exec('CREATE TABLE nic_users(id TEXT PRIMARY KEY,email TEXT UNIQUE,status TEXT,role TEXT,verified_at TEXT);CREATE TABLE nic_sessions(user_id TEXT);CREATE TABLE nic_challenges(user_id TEXT);CREATE TABLE nic_email_changes(user_id TEXT)');
 $emailDb->exec("INSERT INTO nic_users VALUES ('owner','old@example.test','active','user','2026-01-01');INSERT INTO nic_users VALUES ('other','other@example.test','active','user','2026-01-01');INSERT INTO nic_sessions VALUES ('owner'),('owner'),('other');INSERT INTO nic_challenges VALUES ('owner'),('other');INSERT INTO nic_email_changes VALUES ('owner')");
 $emailDb->beginTransaction();$newEmail=nic_complete_email_change($emailDb,'owner','old@example.test',' NEW@EXAMPLE.TEST ');$emailDb->commit();
 check($newEmail==='new@example.test','new email normalized and returned');
 check(!nic_query($emailDb,'SELECT id FROM nic_users WHERE email=?',['old@example.test'])->fetchColumn(),'old email no longer logs in');
 $login=nic_query($emailDb,'SELECT id,status,role,verified_at FROM nic_users WHERE email=?',[nic_email('NEW@example.test')])->fetch(PDO::FETCH_ASSOC);
 check($login && $login['id']==='owner' && $login['status']==='active' && !empty($login['verified_at']),'new email eligible for login-code delivery');
 foreach(['nic_sessions','nic_challenges'] as $table)check(nic_query($emailDb,'SELECT user_id FROM '.$table)->fetchAll(PDO::FETCH_COLUMN)===['other'],'all owner sessions and codes revoked');
 check((int)$emailDb->query('SELECT COUNT(*) FROM nic_email_changes')->fetchColumn()===0,'email request consumed');
 echo "PASS: input validation, public access defaults, independent flags, no unknown top-level settings, keyed hash separation\n";exit;
}
$db=new PDO('sqlite::memory:');$db->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);
$db->exec('CREATE TABLE nic_users(id TEXT PRIMARY KEY,email TEXT,first_name TEXT,last_name TEXT,role TEXT,status TEXT,verified_at TEXT)');
$db->exec('CREATE TABLE nic_sessions(token_hash TEXT,user_id TEXT,csrf_hash TEXT,expires_at TEXT)');
$token=str_repeat('a',64);$csrf=nic_hash('csrf|'.$token,$c);$role=$mode==='ordinary'?'user':'admin';$status=$mode==='blocked'?'blocked':'active';
nic_query($db,'INSERT INTO nic_users VALUES (?,?,?,?,?,?,?)',['u1','test@example.com','Test','Person',$role,$status,nic_now()]);
nic_query($db,'INSERT INTO nic_sessions VALUES (?,?,?,?)',[nic_hash('session|'.$token,$c),'u1',hash('sha256',$csrf),$mode==='expired'?nic_now(-60):nic_now(60)]);
$_COOKIE['__Host-nic_session']=$mode==='unknown'?str_repeat('b',64):$token;
$_SERVER['REQUEST_METHOD']=$mode==='csrf-invalid'?'POST':'GET';$_SERVER['HTTP_X_NIC_CSRF']='wrong';
if(in_array($mode,['ordinary','admin'],true)){$u=nic_admin($db,$c);check($u['role']==='admin','admin expected');echo 'PASS admin';exit;}
$u=nic_session($db,$c);echo 'unexpectedly authorized';
