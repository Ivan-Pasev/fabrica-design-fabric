import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {spawnSync, execFileSync} from 'node:child_process';
const SCRIPT = resolve('scripts/omega10-upstream-lock.py');
const run = (cwd, ...args) => execFileSync('git', args, {cwd,encoding:'utf8',stdio:['ignore','pipe','pipe']}).trim();
function fixture(){
 const root = mkdtempSync(join(tmpdir(),'fab-upstream-git-'));
 run(root,'init','-q');
 run(root,'config','user.name','Fixture');
 run(root,'config','user.email','fixture@example.invalid');
 writeFileSync(join(root,'LICENSE'),'MIT EXAMPLE ONLY\n');
 mkdirSync(join(root,'kit'));
 writeFileSync(join(root,'kit','sample.mjs'),'export const x = 1;\n');
 run(root,'add','.');run(root,'commit','-qm','fixture');
 return {root,sha:run(root,'rev-parse','HEAD')};
}
const invoke=(root,sha,count,out)=>spawnSync('python3',[SCRIPT,'--root',root,'--commit',sha,'--count',String(count),'--output',out],{encoding:'utf8'});
test('Ω10 full-tree recorder verifies exact tracked Git blobs',()=>{
 const {root,sha}=fixture();try{
  const out=join(root,'receipt.json');const p=invoke(root,sha,2,out);
  assert.equal(p.status,0,p.stderr);const v=JSON.parse(readFileSync(out,'utf8'));
  assert.equal(v.tracked_blobs,2);assert.equal(v.commit,sha);assert.match(v.root_sha256,/^[a-f0-9]{64}$/);
  assert.equal(v.files.length,2);assert.equal(v.files[0].path,'LICENSE');
  assert.equal(v.status,'SOURCE_PARITY_PASS_NOT_UPSTREAM_TEST_CERTIFIED');
 }finally{rmSync(root,{recursive:true,force:true})}
});
test('Ω10 recorder blocks wrong commit, count and modified tracked files',()=>{
 const {root,sha}=fixture();try{
  const out=join(root,'receipt.json');
  assert.equal(invoke(root,'0'.repeat(40),2,out).status,2);
  assert.equal(invoke(root,sha,3,out).status,2);
  writeFileSync(join(root,'kit','sample.mjs'),'export const x = 2;\n');
  assert.equal(invoke(root,sha,2,out).status,2);
 }finally{rmSync(root,{recursive:true,force:true})}
});
