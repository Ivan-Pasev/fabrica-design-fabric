import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,existsSync,readFileSync,rmSync,symlinkSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve,join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {planIdePackage} from '../src/ide/ide-package.mjs';

const root=fileURLToPath(new URL('../',import.meta.url));
const cloneScope=fn=>{
 const dir=mkdtempSync(join(tmpdir(),'fabvisual-ide-package-'));
 try{return fn(dir)}finally{rmSync(dir,{recursive:true,force:true})}
};
test('Ω11P zero-write dry-run emits 5 source-hashed files and release HOLD',()=>{
 cloneScope(dir=>{
   const target=join(dir,'fab-visual-ide');
   const plan=planIdePackage(target,{mode:'dry-run'});
   assert.equal(plan.schema,'fab.visual.ide-package-plan.v1');
   assert.equal(plan.files.length,5);
   assert.equal(plan.wroteFiles,false);
   assert.equal(plan.hostAuthorization,'REQUIRED');
   assert.equal(plan.release,'HOLD');
   assert.equal(existsSync(target),false);
   assert.ok(plan.files.every(x=>/^[a-f0-9]{64}$/.test(x.sha256)));
 });
});
test('explicit write creates only isolated reference skill payload and evidence',()=>{
 cloneScope(dir=>{
   const target=join(dir,'fab-visual-ide');
   const report=planIdePackage(target,{mode:'write'});
   assert.equal(report.wroteFiles,true);
   assert.equal(report.files.length,5);
   for(const f of report.files){
     const buf=readFileSync(join(target,f.destination));
     assert.equal(buf.length,f.bytes);
   }
   const evidence=JSON.parse(readFileSync(join(target,'PACKAGE_EVIDENCE.json'),'utf8'));
   assert.equal(evidence.release,'HOLD');
   assert.equal(evidence.executesFetchedCode,false);
   assert.equal(evidence.installScope,'REFERENCE_SKILL_FILES_ONLY_NO_RUNTIME_BINARY');
 });
});
test('repeated install cannot overwrite or mutate previous package',()=>{
 cloneScope(dir=>{
   const target=join(dir,'fab-visual-ide');
   planIdePackage(target,{mode:'write'});
   const before=readFileSync(join(target,'SKILL.md'));
   assert.throws(()=>planIdePackage(target,{mode:'write'}),/destination already exists/);
   assert.deepEqual(readFileSync(join(target,'SKILL.md')),before);
 });
});
test('strict mode parser rejects omitted or guessed permission and mode',()=>{
 cloneScope(dir=>{
   for(const mode of ['install','overwrite',true,null]){
     assert.throws(()=>planIdePackage(join(dir,'pkg'),{mode}),/explicit destination and dry-run\/write/);
   }
 });
});
test('package never auto-installs to current product or current repository root',()=>{
 assert.throws(()=>planIdePackage(resolve(root,'some-skill'),{mode:'dry-run'}),/inside source repository/);
});
test('symlink destination parent and symlink target are refused',()=>{
 cloneScope(dir=>{
   const real=join(dir,'real'),link=join(dir,'link');
   mkdirSync(real);symlinkSync(real,link);
   assert.throws(()=>planIdePackage(join(link,'package'),{mode:'dry-run'}),/symlink ancestor/);
   const target=join(dir,'package');symlinkSync(real,target);
   assert.throws(()=>planIdePackage(target,{mode:'dry-run'}),/destination already exists/);
 });
});
test('missing parent or nonexistent directory cannot be silently created',()=>{
 cloneScope(dir=>{
   const target=join(dir,'unapproved-parent','skill');
   assert.throws(()=>planIdePackage(target,{mode:'dry-run'}),/parent directory must already exist/);
   assert.equal(existsSync(join(dir,'unapproved-parent')),false);
 });
});
test('NUL and empty targets rejected safely',()=>{
 assert.throws(()=>planIdePackage('',{mode:'dry-run'}),/explicit destination/);
 assert.throws(()=>planIdePackage('a\0b',{mode:'dry-run'}),/NUL destination/);
});
test('human-invoked CLI --dry-run leaves filesystem unchanged',()=>{
 cloneScope(dir=>{
   const dest=join(dir,'skill');
   const p=spawnSync(process.execPath,['bin/fab-visual.mjs','ide-package','--dry-run',dest],
     {cwd:root,encoding:'utf8'});
   assert.equal(p.status,0,p.stderr);
   const report=JSON.parse(p.stdout);
   assert.equal(report.wroteFiles,false);
   assert.equal(report.mode,'dry-run');
   assert.equal(existsSync(dest),false);
 });
});
test('CLI without exact --dry-run/--write permission is rejected',()=>{
 cloneScope(dir=>{
   const dest=join(dir,'skill');
   for(const flag of ['--install','--force','--yes']){
     const p=spawnSync(process.execPath,['bin/fab-visual.mjs','ide-package',flag,dest],
       {cwd:root,encoding:'utf8'});
     assert.notEqual(p.status,0);
     assert.equal(existsSync(dest),false);
   }
 });
});
test('an explicit CLI --write creates a reference-only package',()=>{
 cloneScope(dir=>{
   const dest=join(dir,'skill');
   const p=spawnSync(process.execPath,['bin/fab-visual.mjs','ide-package','--write',dest],
     {cwd:root,encoding:'utf8'});
   assert.equal(p.status,0,p.stderr);
   const manifest=JSON.parse(p.stdout);
   assert.equal(manifest.wroteFiles,true);
   assert.ok(existsSync(join(dest,'SKILL.md')));
   assert.equal(existsSync(join(dest,'package.json')),false);
 });
});
test('packaged skill and source remain readable and unchanged',()=>{
 cloneScope(dir=>{
   const target=join(dir,'skill');
   const report=planIdePackage(target,{mode:'write'});
   assert.ok(readFileSync(join(target,'SKILL.md'),'utf8').startsWith('---'));
   assert.equal(report.publisherSignature,'NOT_PRESENT');
   assert.equal(report.scientificAdmission,'NOT_RUN');
   assert.equal(report.noNetwork,true);
 });
});
