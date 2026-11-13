import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,cpSync,appendFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {verifyAnatomyBlobs,anatomySceneModel,renderAnatomySvg,renderAnatomyHtml} from '../src/adapters/anatomy-kernel.mjs';
import {checkSceneAabbIndependently} from '../src/adapters/independent-occlusion.mjs';
import * as K from '../vendor/anatomy/kit/iso-kit.mjs';
import * as A from '../vendor/anatomy/kit/audit.mjs';
const fixture=JSON.parse(readFileSync(new URL('../fixtures/policy-scene.json',import.meta.url),'utf8'));
const clone=x=>structuredClone(x);
test('all five pinned original Anatomy blobs match known Git object hashes',()=>{
 const check=verifyAnatomyBlobs();assert.equal(check.ok,true);assert.equal(check.results.length,5);assert.equal(check.license,'MIT');
});
test('upstream actual projection has reproducible numerical geometry',()=>{
 const p={origin:[100,100],scale:1,azimuth:45,elevation:30};
 const result=K.iso([10,20,0],p);
 assert.equal(result.length,2);assert.ok(result.every(Number.isFinite));
 const s=K.slabOf({x:0,y:0,w:80,d:40,r:4},0,28,p,8);
 assert.match(s.fill,/^M/);assert.match(s.top,/Z$/);assert.equal(s.shades.length,4);
});
test('direct upstream audit SDF detects an inside point and an outside point',()=>{
 const box=A.box([0,0,0],[10,10,10]);
 assert.ok(A.sdf(box,[5,5,5])<0);assert.ok(A.sdf(box,[25,25,25])>0);
});
test('actual upstream builder produces a bounded finite isometric scene',()=>{
 const model=anatomySceneModel(fixture);
 assert.equal(model.source.ok,true);assert.equal(model.audit.status,'PASS');assert.equal(model.mapped.length,4);
 assert.equal(model.audit.projected_bounds.ok,true);
 assert.equal(model.audit.missing_shapes,0);assert.equal(model.audit.discarded_constraints,0);
});
test('independent analytic bounding detector agrees no true intersections in fixture',()=>{
 const v=checkSceneAabbIndependently(fixture);assert.equal(v.ok,true);assert.deepEqual(v.problems,[]);
});
test('SVG generated from exact upstream shapes contains all stable semantic identities',()=>{
 const svg=renderAnatomySvg(fixture);
 for(const id of fixture.parts.map(p=>p.id))assert.ok(svg.includes(`data-part="${id}"`));
 assert.equal((svg.match(/class="part"/g)||[]).length,4);
 assert.match(svg,/ANALOGICAL/);assert.match(svg,/Pinned Anatomy geometry/);
 assert.equal(svg,renderAnatomySvg(fixture));
});
test('HTML has model-derived observables and no active third-party script',()=>{
 const h=renderAnatomyHtml(fixture);
 assert.ok(h.includes('AWAITING_HUMAN'));
 assert.ok(h.includes('Evidence and model observables'));
 assert.ok(!h.includes('<script src'));
 assert.ok(h.includes('No real authorization'));
});
test('source-independent fail-closed policies refuse physical and formal reinterpretation',()=>{
 for(const representation of ['PHYSICAL','FORMAL']) {
   const s=clone(fixture);s.representation=representation;
   assert.throws(()=>renderAnatomySvg(s),/ANALOGICAL scenes only/);
 }
});
test('source-independent renderer escapes malicious part labels',()=>{
 const s=clone(fixture);s.parts[0].label='x<script>alert(1)</script> & "hack"';
 const svg=renderAnatomySvg(s);
 assert.ok(svg.includes('&lt;script&gt;'));
 assert.ok(!svg.includes('<script>'));
});
test('geometry conflicts produce separate analytic FAIL even if sampled depth reports PASS',()=>{
 const s=clone(fixture);s.parts[1].x=s.parts[0].x+2;
 const independent=checkSceneAabbIndependently(s);
 assert.equal(independent.ok,false);
 assert.equal(independent.problems[0].kind,'AABB_INTERSECTION');
});

test('source-lock verifier rejects a one-byte tampering of vendored Anatomy code',()=>{
 const folder=mkdtempSync(join(tmpdir(),'fabvisual-tamper-'));
 try{
   const src=new URL('../vendor/anatomy/',import.meta.url);
   cpSync(src,folder,{recursive:true});
   appendFileSync(join(folder,'kit/iso-kit.mjs'),'\n// unexpected patch\n');
   const report=verifyAnatomyBlobs(folder);
   assert.equal(report.ok,false);
   assert.equal(report.results.find(x=>x.file==='kit/iso-kit.mjs').ok,false);
 }finally{rmSync(folder,{recursive:true,force:true});}
});
