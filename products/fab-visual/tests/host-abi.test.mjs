import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,mkdirSync,readFileSync,existsSync,rmSync,symlinkSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const doctor=fileURLToPath(new URL('../scripts/host-abi-doctor.mjs',import.meta.url));
const installer=fileURLToPath(new URL('../scripts/install-codexstation.mjs',import.meta.url));
function run(script,root,args=[]){return spawnSync(process.execPath,[script,'--root',root,...args],{encoding:'utf8'});}
function host(type){const root=mkdtempSync(join(tmpdir(),'fab-omega8-abi-'));
 if(type==='codexcodingstation'){
  mkdirSync(join(root,'src'),{recursive:true});mkdirSync(join(root,'plugin'),{recursive:true});
  writeFileSync(join(root,'AGENTS.md'),'HOST != STATION; CAPABILITY != AUTHORIZATION; no root modifications\n');
  writeFileSync(join(root,'package.json'),JSON.stringify({name:'@gilc/codexcodingstation-local-companion',version:'0.2.1-rc.2',private:true}));
  writeFileSync(join(root,'src/core.mjs'),'// simulated host marker; not genuine private source\n');
  writeFileSync(join(root,'plugin/orca-plugin.json'),'{}');
 }else if(type==='antigravity'){
  writeFileSync(join(root,'GEMINI.md'),'Synthetic Antigravity constitutional placeholder; not local Windows host\n');
  mkdirSync(join(root,'.agents/rules'),{recursive:true});
  writeFileSync(join(root,'.agents/rules/host.md'),'local host rule preserved\n');
 }
 return root;}
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
for(const type of ['codexcodingstation','antigravity']){
 test('read-only '+type+' profile and dry-run preserve host control',()=>{
  const root=host(type), sentinel=type==='codexcodingstation'?'AGENTS.md':'GEMINI.md';
  try {const before=hash(join(root,sentinel));const d=run(doctor,root,['--profile',type]);assert.equal(d.status,0,d.stderr);const j=JSON.parse(d.stdout);assert.equal(j.status,'CANDIDATE_ONLY');assert.equal(j.hostAuthority,'NOT_GRANTED');assert.equal(j.rootRedacted,true);assert.equal(hash(join(root,sentinel)),before);const r=run(installer,root);assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/DRY_RUN/);assert.equal(existsSync(join(root,'.codexstation')),false);assert.equal(hash(join(root,sentinel)),before);}
  finally{rmSync(root,{recursive:true,force:true});}
 });
 test('opt-in overlay on disposable '+type+' copy retains host byte hashes and complete notices',()=>{
  const root=host(type),sentinel=type==='codexcodingstation'?'AGENTS.md':'GEMINI.md';
  try {const before=hash(join(root,sentinel));const r=run(installer,root,['--apply']);assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/INSTALLED_NOT_AUTHORIZED/);assert.equal(hash(join(root,sentinel)),before);
   const ext=join(root,'.codexstation/extensions/fab-visual');for(const f of ['LICENSE','NOTICE','UPSTREAM_LOCK.json','vendor/anatomy/LICENSE','vendor/anatomy/SOURCE_LOCK.json'])assert.equal(existsSync(join(ext,f)),true,f);
   const ver=spawnSync(process.execPath,[join(ext,'bin/fab-visual.mjs'),'anatomy-verify'],{cwd:root,encoding:'utf8'});assert.equal(ver.status,0,ver.stderr);assert.match(ver.stdout,/"ok": true/);
   const again=run(installer,root,['--apply']);assert.equal(again.status,2);assert.match(again.stderr,/HOLD_COLLISION/);
  } finally {rmSync(root,{recursive:true,force:true});}
 });
}
test('doctor never promotes a host without policy evidence',()=>{const root=host('none');try{const r=run(doctor,root);assert.equal(r.status,2);assert.equal(JSON.parse(r.stdout).status,'HOLD_POLICY_UNRESOLVED');}finally{rmSync(root,{recursive:true,force:true});}});
test('doctor rejects symlinked policy documents',()=>{const root=host('none'),target=join(root,'real.txt');try{writeFileSync(target,'synthetic');symlinkSync(target,join(root,'AGENTS.md'));const r=run(doctor,root);assert.equal(r.status,2);assert.equal(JSON.parse(r.stdout).status,'HOLD_UNSAFE_ENTRY');}finally{rmSync(root,{recursive:true,force:true});}});
