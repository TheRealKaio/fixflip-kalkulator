'use strict';
const cp=require('node:child_process'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const executable=process.env.NIC_PHP_BIN||'php',prefix=JSON.parse(process.env.NIC_PHP_ARGS||'[]');
function run(args){const r=cp.spawnSync(executable,[...prefix,...args],{encoding:'utf8'});assert.equal(r.status,0,r.stderr+r.stdout);return r.stdout;}
const root=path.resolve(__dirname,'../webspace');
for(const dir of ['immocheck-web','immocheck-web/api','immocheck-private'])for(const file of fs.readdirSync(path.join(root,dir)))if(file.endsWith('.php'))run(['-l',path.join(root,dir,file)]);
const entry=JSON.parse(run(['-f',path.join(root,'immocheck-web/api/index.php')]));assert(entry.error.includes('Serverkonfiguration fehlt'),'new entry must resolve the sibling private application');
for(const mode of ['normal','admin','ordinary','blocked','expired','unknown','csrf-invalid','settings-invalid','email-invalid']){
 const text=run(['-f',path.join(__dirname,'policies.php'),'--',mode]);if(['normal','admin'].includes(mode))assert(text.includes('PASS'),text);else assert(JSON.parse(text).error,mode);
}
console.log('PHP API checks passed: syntax, configuration validation, normal/admin roles, blocked/expired/unknown sessions and CSRF checks. SQLite fixtures, no live MariaDB or SMTP connection.');
const importTemp=fs.mkdtempSync(path.join(require('node:os').tmpdir(),'nic-import-test-'));
try{
 for(const mode of ['valid','duplicate','invalid','too-many','rollback']){
  const statePath=path.join(importTemp,mode+'.json');
  const result=JSON.parse(run(['-f',path.join(__dirname,'user_import.php'),'--',mode,statePath]));
  const state=JSON.parse(fs.readFileSync(statePath,'utf8'));
  if(mode==='valid'){
   assert.equal(result.created,1);assert.equal(result.updated,1);assert.equal(state.audit,1);
   const existing=state.users.find(u=>u.email==='existing@example.test'),added=state.users.find(u=>u.email==='new@example.test');
   assert.equal(existing.first_name,'José');assert.equal(existing.last_name,'Müller');
   assert.equal(existing.role,'admin');assert.equal(existing.status,'blocked');assert.equal(existing.verified_at,'2025-01-01');
   assert.equal(added.last_name,'Gonçalves');assert.equal(added.role,'user');assert.equal(added.status,'active');assert.equal(added.verified_at,null);
  }else{assert(result.error,mode);assert.equal(state.users.length,2,mode);assert.equal(state.audit,0,mode);assert.equal(state.users.find(u=>u.email==='existing@example.test').first_name,'Before',mode);}
 }
 console.log('CSV import backend passed: Unicode names, normalized email, existing roles/status preserved, new users unconfirmed, duplicate/invalid/oversize rejection and complete transaction rollback. No live accounts imported.');
}finally{fs.rmSync(importTemp,{recursive:true,force:true});}
