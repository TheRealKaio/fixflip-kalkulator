'use strict';
const cp=require('node:child_process'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const executable=process.env.NIC_PHP_BIN||'php',prefix=JSON.parse(process.env.NIC_PHP_ARGS||'[]');
function run(args){const r=cp.spawnSync(executable,[...prefix,...args],{encoding:'utf8'});assert.equal(r.status,0,r.stderr+r.stdout);return r.stdout;}
const root=path.resolve(__dirname,'../webspace');
for(const dir of ['immocheck-api','immocheck-private'])for(const file of fs.readdirSync(path.join(root,dir)))if(file.endsWith('.php'))run(['-l',path.join(root,dir,file)]);
for(const mode of ['normal','admin','ordinary','blocked','expired','unknown','csrf-invalid','settings-invalid','email-invalid']){
 const text=run(['-f',path.join(__dirname,'policies.php'),'--',mode]);if(['normal','admin'].includes(mode))assert(text.includes('PASS'),text);else assert(JSON.parse(text).error,mode);
}
console.log('PHP API checks passed: syntax, configuration validation, normal/admin roles, blocked/expired/unknown sessions and CSRF checks. SQLite fixtures, no live MariaDB or SMTP connection.');
