<?php
declare(strict_types=1);
require dirname(__DIR__).'/webspace/immocheck-private/app.php';
function check(bool $value,string $message): void {if(!$value)throw new RuntimeException($message);}
$mode=$argv[1]??'normal';
$c=['pepper'=>str_repeat('t',64)];
if($mode==='settings-invalid'){nic_clean_settings(['version'=>1,'access'=>['pdfShare'=>'false']]);throw new RuntimeException('invalid accepted');}
if($mode==='email-invalid'){nic_email("x@example.com\r\nBcc: y@example.com");throw new RuntimeException('header injection accepted');}
if($mode==='normal'){
 $s=nic_clean_settings(['version'=>1,'secret'=>'must disappear','access'=>['pdfDownload'=>false,'pdfShare'=>true]]);
 check(!isset($s['secret']),'unknown top-level settings retained');check($s['access']['calculators']===true,'missing defaults');check($s['access']['pdfDownload']===false,'false lost');
 check(nic_email(' TEST@EXAMPLE.COM ')==='test@example.com','email normalization');check(nic_name(' Kai ')==='Kai','name trim');
 check(nic_hash('session|one',$c)!==nic_hash('session|two',$c),'hash separation');
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
