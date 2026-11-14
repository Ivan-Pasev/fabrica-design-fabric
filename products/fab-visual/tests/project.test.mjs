import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync,writeFileSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {assertScene} from '../src/visual/contract.mjs';
import {canonicalJSON,sha256} from '../src/visual/provenance.mjs';
import {forkVisualScene,visualDiff,zipStore,projectFiles} from '../src/visual/project.mjs';
import {loadDomainTemplates} from '../src/visual/gallery.mjs';
import {renderStudio} from '../src/visual/studio.mjs';

const base=JSON.parse(readFileSync(new URL('../templates/energy-microgrid.scene.json',import.meta.url),'utf8'));
const copy=o=>structuredClone(o),digest='sha256:'+sha256(canonicalJSON(base));
const root=fileURLToPath(new URL('../',import.meta.url));
const edit=()=>{const s=copy(base);s.parts[0].x+=24;s.parts[0].w+=18;
  s.links.pop();
  s.visualEdit={schema:'fab.visual.visual-edit.v1',sourceDigest:digest,
    provenance:'DERIVED_PRESENTATION_ONLY_NOT_MODEL_AUTHORITY',operation:'connection_removal',
    release:'HOLD'};
  return s;
};
test('Ω11M source-preserving fork creates distinct visual ID/revision and exact ancestry',()=>{
 const fork=forkVisualScene(base,'study-01',digest);
 assert.equal(fork.id,base.id+'--fork-study-01');
 assert.equal(fork.model.revision,base.model.revision+'+visual-fork.study-01');
 assert.equal(fork.fork.sourceSceneId,base.id);
 assert.equal(fork.fork.sourceDigest,digest);
 assert.equal(fork.fork.sourceModelRevision,base.model.revision);
 assert.equal(fork.fork.release,'HOLD');
 assert.equal(fork.model.authority,base.model.authority);
 assert.equal(fork.claim.status,'EXPLANATORY');
 assert.deepEqual(base,JSON.parse(readFileSync(new URL('../templates/energy-microgrid.scene.json',import.meta.url),'utf8')));
 assert.doesNotThrow(()=>assertScene(fork));
});
test('fork refuses empty/malformed/unsafe slug, nested forks and source SHA corruption',()=>{
 for(const slug of ['', '../pass', 'UPPER', 'has space', 'a'.repeat(41),'end-','é','x\\y'])
   assert.throws(()=>forkVisualScene(base,slug,digest),/VISUAL_FORK_REJECT/);
 assert.throws(()=>forkVisualScene(base,'ok','sha256:'+'0'.repeat(62)),/digest/);
 assert.throws(()=>forkVisualScene(forkVisualScene(base,'ok',digest),'again',digest),/nested fork/);
});
test('fork rejects synthetic science claim escalation and unauthorized large model',()=>{
 const s=copy(base);s.claim.status='CERTIFIED';
 assert.throws(()=>forkVisualScene(s,'ok',digest),/synthetic source claim escalated/);
 const huge=copy(base);huge.parts=Array.from({length:301},(_,i)=>({...huge.parts[0],id:'p'+i}));
 assert.throws(()=>forkVisualScene(huge,'ok',digest),/bounded size/);
});
test('unchanged model yields zero visual diff with explicit limits',()=>{
 const d=visualDiff(base,copy(base),digest);
 assert.equal(d.changed,false);
 assert.equal(d.move.length,0);assert.equal(d.addedLinks.length,0);
 assert.equal(d.sourceAuthorityPreserved,true);assert.equal(d.physicalValidation,'NOT_RUN');
 assert.equal(d.release,'HOLD');
});
test('source-vs-edited diff identifies exact moved, resized and removed links',()=>{
 const d=visualDiff(base,edit(),digest);
 assert.equal(d.changed,true);
 assert.deepEqual(d.move.map(x=>x.id),['pv']);
 assert.equal(d.move[0].to.x,59);
 assert.equal(d.resize[0].to.w,188);
 assert.equal(d.removedLinks.length,1);
 assert.equal(d.removedLinks[0].from,'dispatch');
 assert.equal(d.addedLinks.length,0);
});
test('added illustrative typed source connection produces exact additive diff',()=>{
 const s=copy(base);s.links.push({from:'pv',to:'dc-bus',flow:'energy',fromPort:'dc-out',toPort:'pv-in'});
 const d=visualDiff(base,s,digest);
 assert.equal(d.addedLinks.length,1);
 assert.equal(d.removedLinks.length,0);
 assert.equal(d.changed,true);
});
test('visual fork diff preserves scientific model and records fork ID',()=>{
 const f=forkVisualScene(edit(),'sim-1',digest);
 const d=visualDiff(base,f,digest);
 assert.equal(d.sourceSceneId,base.id);
 assert.equal(d.derivedSceneId,f.id);
 assert.equal(d.move.length,1);
 assert.equal(d.removedLinks.length,1);
 assert.equal(d.originalClaimPreserved,true);
});
test('reject sneaky approval metadata or source model authority mutation',()=>{
 const a=edit();a.hiddenReleaseApproval='APPROVE';
 assert.throws(()=>visualDiff(base,a,digest),/hidden authority field mutation/);
 const b=edit();b.model.authority='signed by live network';
 assert.throws(()=>visualDiff(base,b,digest),/model authority drift/);
 const c=edit();c.claim.status='CERTIFIED';
 assert.throws(()=>visualDiff(base,c,digest),/source claim/);
});
test('reject altered template origin, measurements and untrusted audit fields',()=>{
 for(const modify of [
   s=>s.template.source_status='MEASURED',
   s=>s.audit.empirical_validation='PASS',
   s=>s.observables[0].value=999,
   s=>s.parts[0].status='RELEASED',
   s=>s.parts[0].ports[0].flow='control',
   s=>s.representation='PHYSICAL'
 ]){
   const v=edit();modify(v);
   assert.throws(()=>visualDiff(base,v,digest),/VISUAL_DIFF_REJECT/);
 }
});
test('visual edit metadata cannot forge signatures, release or source digests',()=>{
 for(const change of [
   s=>s.visualEdit.release='ALLOW',
   s=>s.visualEdit.sourceDigest='sha256:'+'0'.repeat(64),
   s=>s.visualEdit.provenance='REAL_HOST_AUTHORITY'
 ]){
   const v=edit();change(v);
   assert.throws(()=>visualDiff(base,v,digest),/untrusted visual edit provenance/);
 }
});
test('changed fork cannot invent publisher authentication or different revision',()=>{
 const f=forkVisualScene(base,'fork1',digest);f.fork.publisherSignature='CERTIFIED';
 assert.throws(()=>visualDiff(base,f,digest),/fork provenance/);
 const g=forkVisualScene(base,'fork1',digest);g.model.revision='source validated';
 assert.throws(()=>visualDiff(base,g,digest),/fork provenance/);
});
test('reject missing/duplicated model nodes, broken ports and NaN coordinates',()=>{
 const a=edit();a.parts[1].id=a.parts[0].id;
 assert.throws(()=>visualDiff(base,a,digest),/missing\/duplicate/);
 const b=edit();b.parts[0].x=Infinity;
 assert.throws(()=>visualDiff(base,b,digest),/nonfinite geometry/);
 const c=edit();c.links[0].toPort='wrong';
 assert.throws(()=>visualDiff(base,c,digest),/invalid typed link port/);
});
test('deterministic ZIP contains local and central headers and CRC32 metadata',()=>{
 const files=[{path:'a.txt',content:'alpha\n'},{path:'b/c.json',content:'{"thing":"Ω"}\n'}];
 const one=zipStore(files),two=zipStore(files);
 assert.deepEqual(one,two);
 assert.equal(one[0],0x50);assert.equal(one[1],0x4b);
 assert.equal(one[2],0x03);assert.equal(one[3],0x04);
 assert.equal(one.at(-22),0x50);assert.equal(one.at(-21),0x4b);
 assert.ok(one.length>80);
});
test('ZIP rejects unsafe paths, duplicate names, unsupported binary and oversized payload',()=>{
 for(const path of ['../escape','/root','bad\\name','a//b','a/../b','a/./b','UPPER.txt']){
   assert.throws(()=>zipStore([{path,content:'x'},{path:'good.txt',content:'okay'}]),/PROJECT_ZIP_REJECT/);
 }
 assert.throws(()=>zipStore([{path:'x.txt',content:'a'},{path:'x.txt',content:'b'}]),/duplicate/);
 assert.throws(()=>zipStore([{path:'x.txt',content:new Uint8Array([1])},{path:'y.txt',content:'b'}]),/UTF-8/);
 assert.throws(()=>zipStore([{path:'big.txt',content:'x'.repeat(3000001)},{path:'small.txt',content:'x'}]),/large/);
});
test('portable project contains original source, synthetic fork, diff and timeline with authority HOLD',()=>{
 const e=edit();
 const result=projectFiles(base,e,[base,e],digest,'project01',visualDiff,forkVisualScene);
 assert.equal(result.files.length,6);
 const names=result.files.map(x=>x.path);
 assert.deepEqual(names,[
  'manifest.json','source/original.scene.json','derived/fork.scene.json',
  'evidence/visual-diff.json','evidence/edit-history.json','readme.txt']);
 assert.equal(result.manifest.release,'HOLD');
 assert.equal(result.manifest.hostAuthorization,'NOT_RUN');
 const fork=JSON.parse(result.files[2].content);
 assert.equal(fork.fork.sourceDigest,digest);
 assert.equal(fork.model.authority,base.model.authority);
 const output=zipStore(result.files);
 assert.ok(output.length>3000);
});
test('portable project refuses tampered source/publisher evidence and unreviewed history',()=>{
 const a=edit();a.model.authority='new';
 assert.throws(()=>projectFiles(base,a,[base,a],digest,'good',visualDiff,forkVisualScene),/model authority drift/);
 const b=edit();const hist=copy(base);hist.claim.status='ALLOWED';
 assert.throws(()=>projectFiles(base,b,[base,hist],digest,'good',visualDiff,forkVisualScene),/source claim/);
 assert.throws(()=>projectFiles(base,b,[],digest,'good',visualDiff,forkVisualScene),/visual snapshots required/);
});
test('all three original domain templates admit local fork and diff but no empirical uplift',()=>{
 for(const item of loadDomainTemplates()){
   const scene=item.scene,hash='sha256:'+sha256(canonicalJSON(scene));
   const f=forkVisualScene(scene,'site-a',hash);
   assert.equal(visualDiff(scene,f,hash).changed,false);
   assert.equal(f.audit.scientific_admission,'NOT_RUN');
   assert.equal(f.template.source_status,'NOT_MEASURED');
 }
});
test('generated standalone Studio includes real accessible project/diff/connector controls',()=>{
 const a=renderStudio(base);
 for(const needle of ['id="edit-fork-slug"','id="edit-fork"','id="edit-project"',
    'id="edit-diff-toggle"','id="edit-revision"','id="edit-canvas-connect"'])
   assert.ok(a.html.includes(needle),needle);
 assert.equal(a.metadata.release,'HOLD');
 assert.match(a.html,/PROJECT_ZIP_REJECT/);
});
test('CLI project emits independently reconstructable ZIP and witness without source overwrite',()=>{
 const d=mkdtempSync(join(tmpdir(),'fab-omega11m-'));
 try{
   const source=join(d,'source.scene.json'),derived=join(d,'edited.scene.json'),out=join(d,'project.zip');
   writeFileSync(source,JSON.stringify(base));writeFileSync(derived,JSON.stringify(edit()));
   const r=spawnSync(process.execPath,['bin/fab-visual.mjs','project',source,derived,'local-test',out],
     {cwd:root,encoding:'utf8'});
   assert.equal(r.status,0,r.stderr);
   assert.ok(existsSync(out));
   const receipt=JSON.parse(readFileSync(out+'.witness.json','utf8'));
   assert.equal(receipt.entries.length,6);
   assert.equal(receipt.release,'HOLD');
   assert.equal(receipt.archiveSha256,'sha256:'+sha256(readFileSync(out)));
   assert.equal(JSON.parse(readFileSync(source)).id,base.id);
 }finally{rmSync(d,{recursive:true,force:true})}
});
test('CLI project refuses source file overwrite and invalid fork slug',()=>{
 const d=mkdtempSync(join(tmpdir(),'fab-omega11m-'));
 try{
   const input=join(d,'input.scene.json'),out=join(d,'safe.zip');
   writeFileSync(input,JSON.stringify(base));
   for(const args of [
      ['project',input,input,'bad',input],
      ['project',input,input,'../evil',out]
   ]){
     const r=spawnSync(process.execPath,['bin/fab-visual.mjs',...args],{cwd:root,encoding:'utf8'});
     assert.notEqual(r.status,0);
   }
   assert.equal(JSON.parse(readFileSync(input)).id,base.id);
 }finally{rmSync(d,{recursive:true,force:true})}
});
