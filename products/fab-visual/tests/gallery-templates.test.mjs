import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {assertScene} from '../src/visual/contract.mjs';
import {sha256,canonicalJSON} from '../src/visual/provenance.mjs';
import {DOMAIN_TEMPLATE_CATALOG,validateDomainTemplate,loadDomainTemplates,buildGalleryBundle} from '../src/visual/gallery.mjs';

const root=fileURLToPath(new URL('../',import.meta.url));
const data=()=>loadDomainTemplates();
const clone=x=>structuredClone(x);
const expectReject=(value,catalog,pattern=/DOMAIN_TEMPLATE_HOLD/) =>
  assert.throws(()=>validateDomainTemplate(value,catalog),pattern);
test('exactly three independent first-party synthetic domain packs',()=>{
 const all=data();
 assert.equal(all.length,3);
 assert.deepEqual(all.map(x=>x.key),['energy','laboratory','agents']);
 assert.equal(new Set(all.map(x=>x.scene.id)).size,3);
 assert.deepEqual(all.map(x=>x.scene.parts.length),[6,7,7]);
 assert.deepEqual(all.map(x=>x.scene.links.length),[7,8,7]);
});
test('all three SceneIR source contracts and typed flow ports validate',()=>{
 for(const x of data()){
   assert.doesNotThrow(()=>assertScene(x.scene));
   const mapping=new Map(x.scene.parts.map(p=>[p.id,p]));
   for(const link of x.scene.links){
     assert.ok(mapping.get(link.from).ports.some(p=>p.id===link.fromPort&&p.flow===link.flow));
     assert.ok(mapping.get(link.to).ports.some(p=>p.id===link.toPort&&p.flow===link.flow));
   }
   assert.equal(x.scene.claim.status,'EXPLANATORY');
   assert.equal(x.scene.representation,'ANALOGICAL');
   assert.equal(x.scene.template.origin,'FIRST_PARTY_SYNTHETIC');
   assert.equal(x.scene.audit.scientific_admission,'NOT_RUN');
   assert.equal(x.scene.audit.real_host_verification,'NOT_RUN');
 }
});
test('all numeric observables are synthetic, unit-labelled and never real telemetry',()=>{
 for(const x of data()){
   assert.equal(x.scene.template.source_status,'NOT_MEASURED');
   assert.equal(x.scene.template.real_hardware_or_host_attestation,'NOT_RUN');
   assert.ok(x.scene.model.authority.includes('no external measurements or authorization'));
   for(const o of x.scene.observables){
     assert.equal(o.source,x.scene.model.authority);
     assert.equal(o.evidence,'NOT_RUN');
     if(typeof o.value==='number')assert.ok(o.unit&&o.unit.trim());
   }
 }
});
test('explicit energy fixture never includes false grid-performance or LCOE claims',()=>{
 const s=data()[0].scene;
 assert.equal(s.observables.find(x=>x.id==='site_export_power').value,'NOT_CALCULATED');
 assert.equal(s.observables.find(x=>x.id==='battery_soc').value,'NOT_MEASURED');
 assert.match(s.claim.interpretation,/no production energy yield|no production energy yield/i);
});
test('laboratory template does not claim measured pressure/dose or calibration',()=>{
 const s=data()[1].scene;
 assert.equal(s.observables.find(x=>x.id==='pressure_reading').value,'NOT_MEASURED');
 assert.equal(s.observables.find(x=>x.id==='dose_or_exposure').value,'NOT_ASSESSED');
 assert.equal(s.observables.find(x=>x.id==='metrology_calibrated').value,false);
});
test('agent template retains blocked external execution and no fake human approval',()=>{
 const s=data()[2].scene;
 assert.equal(s.parts.find(x=>x.id==='execution').status,'BLOCKED');
 assert.equal(s.observables.find(x=>x.id==='approval_granted').value,false);
 assert.equal(s.observables.find(x=>x.id==='external_execution_enabled').value,false);
});
test('template validator rejects forged source authority and empirical admission',()=>{
 const x=data()[0],a=clone(x.scene);a.model.authority='real laboratory cert';
 expectReject(a,x,/DOMAIN_TEMPLATE_HOLD/);
 const b=clone(x.scene);b.audit.scientific_admission='PASS';
 expectReject(b,x);
 const c=clone(x.scene);c.template.real_hardware_or_host_attestation='PASS';
 expectReject(c,x);
});
test('template validator refuses real measurements and unlabelled unit values',()=>{
 const x=data()[1],a=clone(x.scene);a.observables[0].source='live medical records';
 expectReject(a,x);
 const b=clone(x.scene);b.observables[0].evidence='PASS';
 expectReject(b,x);
 const c=clone(x.scene);c.observables[0].unit='';
 expectReject(c,x,/explicit unit or 1 for dimensionless/);
});
test('template validator refuses wrong source profile or arbitrary domain classification',()=>{
 const x=data()[2],a=clone(x.scene);a.model.source_profile='LIVE_PRODUCTION';
 expectReject(a,x);
 const b=clone(x.scene);b.template.domain='energy';
 expectReject(b,x);
});
test('template validator rejects duplicate node IDs and invalid links',()=>{
 const x=data()[0],a=clone(x.scene);a.parts[1].id=a.parts[0].id;
 expectReject(a,x,/duplicate/);
 const b=clone(x.scene);b.links[0].to='not-a-real-component';
 expectReject(b,x,/missing endpoint/);
 const c=clone(x.scene);c.links[1].toPort='dispatch';
 expectReject(c,x,/unresolved/);
});
test('template validator rejects unsupported source registries and invalid types',()=>{
 const a=data()[0],fake={...a,key:'other'};
 expectReject(a.scene,fake,/unknown fixed registry/);
 const b=clone(a.scene);b.representation='PHYSICAL';expectReject(b,a);
});
test('gallery produces exactly 3 studios, 3 scenes, 3 preview SVGs and local index/manifest',()=>{
 const {assets,manifest}=buildGalleryBundle();
 assert.equal(assets.length,11);
 assert.deepEqual(assets.map(x=>x.path).sort(),[
  'gallery.manifest.json','index.html',
  'previews/agents.svg','previews/energy.svg','previews/laboratory.svg',
  'scenes/agents.scene.json','scenes/energy.scene.json','scenes/laboratory.scene.json',
  'studios/agents.html','studios/energy.html','studios/laboratory.html'
 ].sort());
 assert.deepEqual(manifest.templates.map(x=>x.key),['energy','laboratory','agents']);
 assert.equal(manifest.release,'HOLD');
 assert.equal(manifest.external_resources_required,false);
 assert.equal(manifest.real_measurements,'NOT_PRESENT');
});
test('gallery content is standalone CSP, accessible search, categories and three links',()=>{
 const {assets}=buildGalleryBundle();
 const html=assets.find(x=>x.path==='index.html').content;
 assert.ok(html.startsWith('<!doctype html>'));
 assert.match(html,/Content-Security-Policy/);
 assert.match(html,/connect-src &#39;none&#39;/);
 assert.match(html,/id="template-search"/);
 assert.match(html,/id="template-category"/);
 assert.match(html,/id="gallery-count"/);
 assert.equal((html.match(/data-open-studio=/g)||[]).length,3);
 assert.equal((html.match(/data-gallery-card/g)||[]).length,4); // CSS/JS + 3 card attributes
 assert.doesNotMatch(html,/<script\s+src=/i);
 assert.doesNotMatch(html,/(?:src|href)=["']https?:\/\//i);
});
test('each Studio compiled in the gallery is editable with original claim boundary',()=>{
 const {assets,manifest}=buildGalleryBundle();
 for(const t of manifest.templates){
   const html=assets.find(x=>x.path===t.studio_path).content;
   assert.match(html,/id="edit-apply"/);
   assert.match(html,/id="edit-undo"/);
   assert.match(html,/id="graph-import-file"/);
   assert.match(html,/Release HOLD|release HOLD/);
   assert.equal(sha256(html),t.html_sha256);
   const json=assets.find(x=>x.path===t.scene_path).content;
   assert.equal(sha256(json),t.scene_sha256);
   assert.equal(assertScene(JSON.parse(json)).id,t.id);
   assert.equal(sha256(assets.find(x=>x.path===t.preview_path).content),t.svg_sha256);
 }
});
test('gallery outputs are byte-identical, source manifests stable and no in-memory mutation',()=>{
 const original=data(),before=original.map(x=>canonicalJSON(x.scene));
 const first=buildGalleryBundle(original),second=buildGalleryBundle(original);
 assert.deepEqual(first,second);
 assert.deepEqual(original.map(x=>canonicalJSON(x.scene)),before);
 assert.equal(first.manifest.output_html_sha256,sha256(first.assets.find(x=>x.path==='index.html').content));
});
test('gallery rejects unknown source index, duplicates and missing templates',()=>{
 const a=data();
 assert.throws(()=>buildGalleryBundle(a.slice(0,2)),/exactly 3/);
 const b=data();b[1].key='energy';
 assert.throws(()=>buildGalleryBundle(b),/duplicate or unregistered/);
});
test('gallery serialization escapes model label injection and does not execute remote scripts',()=>{
 const a=data();a[0].scene.parts[0].label='</script><img src=x onerror=alert(1)>';
 const o=buildGalleryBundle(a);
 const html=o.assets.find(x=>x.path==='index.html').content;
 assert.ok(!html.includes('<img src=x'));
 assert.ok(!html.includes('</script><img'));
 const studio=o.assets.find(x=>x.path==='studios/energy.html').content;
 assert.ok(!studio.includes('</script><img'));
 assert.ok(studio.includes('u003c'));
});
test('CLI gallery writes all usable static files plus independent source manifests',()=>{
 const dir=mkdtempSync(join(tmpdir(),'fabgallery-'));
 try{
   const out=join(dir,'gallery');
   const r=spawnSync(process.execPath,['bin/fab-visual.mjs','gallery',out],{cwd:root,encoding:'utf8'});
   assert.equal(r.status,0,r.stderr);
   const result=JSON.parse(r.stdout);
   assert.equal(result.release,'HOLD');
   assert.equal(result.files,11);
   assert.ok(existsSync(join(out,'index.html')));
   for(const key of ['energy','laboratory','agents']){
     assert.ok(existsSync(join(out,'studios',key+'.html')));
     assert.ok(existsSync(join(out,'scenes',key+'.scene.json')));
   }
   const manifest=JSON.parse(readFileSync(join(out,'gallery.manifest.json'),'utf8'));
   assert.equal(manifest.templates.length,3);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('CLI refuses source-tree as output to avoid overwriting source templates',()=>{
 const r=spawnSync(process.execPath,['bin/fab-visual.mjs','gallery','templates'],{cwd:root,encoding:'utf8'});
 assert.notEqual(r.status,0);
 assert.match(r.stderr,/cannot write inside source code/);
});
