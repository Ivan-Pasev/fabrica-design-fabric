import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {renderStudio} from '../src/visual/studio.mjs';
import {exportInterchange,FORMATS} from '../src/adapters/interchange.mjs';
import {sha256,canonicalJSON} from '../src/visual/provenance.mjs';

const original=JSON.parse(readFileSync(new URL('../fixtures/policy-scene.json',import.meta.url),'utf8'));
const cp=()=>structuredClone(original);
const root=fileURLToPath(new URL('../',import.meta.url));
function temp(fn){
  const dir=mkdtempSync(join(tmpdir(),'fabvisual-studio-'));
  try{return fn(dir)}finally{rmSync(dir,{force:true,recursive:true})}
}
function assertHostHold(value){
  assert.equal(value.release,'HOLD');
  assert.doesNotMatch(JSON.stringify(value),/ELIGIBLE_FOR_AUTHORIZED_RELEASE/);
}

test('four explicit data-interchange formats; none executes external code',()=>{
  assert.deepEqual(FORMATS,['reactflow','cytoscape','mermaid','dot']);
  for(const name of FORMATS){
    const v=exportInterchange(cp(),name);
    assert.equal(v.format,name);
    assertHostHold(v.receipt);
    assert.equal(v.receipt.no_external_code_executed,true);
    assert.equal(v.receipt.source_digest,'sha256:'+sha256(canonicalJSON(original)));
    assert.equal(v.receipt.output_digest,'sha256:'+sha256(v.text));
  }
});
test('XYFlow graph retains 4 models, 3 flow edges, ports, coordinates and claims',()=>{
  const g=JSON.parse(exportInterchange(cp(),'reactflow').text);
  assert.equal(g.nodes.length,4);assert.equal(g.edges.length,3);
  assert.equal(g.nodes[0].data.label,'Intake');
  assert.equal(g.nodes[0].position.x,40);
  assert.equal(g.nodes[0].style.width,180);
  assert.equal(g.nodes[3].data.status,'BLOCKED');
  assert.equal(g.edges[1].source,'policy');assert.equal(g.edges[1].target,'human');
  assert.equal(g.edges[1].data.flow,'control');
  assert.equal(g.edges[1].data.fromPort,'out');
  assert.equal(g.source_model.authority,original.model.authority);
  assertHostHold(g);
});
test('Cytoscape graph retains stable IDs and real 2D positions, not metrology',()=>{
  const g=JSON.parse(exportInterchange(cp(),'cytoscape').text);
  assert.equal(g.elements.nodes.length,4);
  assert.deepEqual(g.elements.nodes[0].position,{x:130,y:162.5});
  assert.deepEqual(g.elements.edges.map(x=>x.data.source),['intake','policy','human']);
  assert.equal(g.layout.name,'preset');
  assert.match(g.semantic_boundary,/NOT_MODEL_OR_GEOMETRY_PROOF/);
  assertHostHold(g);
});
test('Mermaid graph binds stable internal IDs rather than attacker model identifiers',()=>{
  const s=cp();s.parts[0].id='malicious";\nflowchart TB';
  s.links[0].from=s.parts[0].id;
  const graph=exportInterchange(s,'mermaid').text;
  assert.match(graph,/^flowchart LR\n/);
  assert.match(graph,/n0 -->\|control\| n1/);
  assert.doesNotMatch(graph,/malicious/);
  assert.equal((graph.match(/^flowchart /gm)||[]).length,1);
});
test('Graphviz DOT format is structurally safe and preserves flow labels',()=>{
  const out=exportInterchange(cp(),'dot').text;
  assert.match(out,/^digraph FabVisual \{/);
  assert.match(out,/n0 -> n1 \[label="control"\]/);
  assert.match(out,/n3 \[label="Release"\]/);
  assert.equal((out.match(/^digraph /gm)||[]).length,1);
});
test('XML / script / newline injection cannot introduce extra Mermaid or DOT directives',()=>{
  const s=cp();
  const danger='A"]\nflowchart TB\n</script><img src=x onerror=alert(1)>\n#"';
  s.parts[0].label=danger;
  for(const f of ['mermaid','dot']){
    const text=exportInterchange(s,f).text;
    assert.equal((text.match(/flowchart TB/g)||[]).length,0);
    assert.doesNotMatch(text,/<script|<img/i);
    assert.doesNotMatch(text,/onerror\s*=/);
  }
});
test('repeated formats are canonical and input stays untouched',()=>{
  const s=cp(),before=canonicalJSON(s);
  for(const format of FORMATS){
    const one=exportInterchange(s,format),two=exportInterchange(s,format);
    assert.equal(one.text,two.text);
    assert.deepEqual(one.receipt,two.receipt);
  }
  assert.equal(canonicalJSON(s),before);
});
test('wrong interchange format rejected',()=>{
  assert.throws(()=>exportInterchange(cp(),'code-execution'),/unknown interchange/);
});
test('invalid scene and impossible coordinates rejected by existing contract',()=>{
  const s=cp();s.parts[0].x=Infinity;
  assert.throws(()=>exportInterchange(s,'reactflow'),/finite number required/);
  assert.throws(()=>renderStudio(s),/finite number required/);
});
test('upstream source model and scientific source cannot be overwritten by graph flags',()=>{
  const g=JSON.parse(exportInterchange(cp(),'reactflow').text);
  assert.equal(g.representation,'ANALOGICAL');
  assert.equal(g.source_claim.status,'EXPLANATORY');
  assert.equal(g.release,'HOLD');
  assert.match(g.semantic_boundary,/NOT_MODEL_OR_GEOMETRY_PROOF/);
});
test('interactive Studio contains actual reference, pinned isometric and inspector controls',()=>{
  const result=renderStudio(cp());
  assert.deepEqual(result.metadata.views,['2d','isometric','compare']);
  assert.equal(result.metadata.isoStatus,'PASS_BOUNDED_SAMPLED_ANATOMY');
  assert.ok(result.html.includes('data-view="isometric"'));
  assert.ok(result.html.includes('data-view="compare"'));
  assert.ok(result.html.includes('id="part-list"'));
  assert.ok(result.html.includes('id="flow-filter"'));
  assert.ok(result.html.includes('data-export="reactflow"'));
  assert.ok(result.html.includes('data-export="mermaid"'));
  assert.ok(result.html.includes('class="part node'));
  assert.ok(result.html.includes('Pinned Anatomy'));
  assertHostHold(result.metadata);
});
test('Studio has local-only CSP and no third-party scripts or network import',()=>{
  const result=renderStudio(cp());
  assert.match(result.html,/Content-Security-Policy/);
  assert.match(result.html,/connect-src &#39;none&#39;/);
  assert.doesNotMatch(result.html,/<script\s+src=/i);
  assert.doesNotMatch(result.html,/<link\s+href=.*https?:/i);
  assert.equal(result.metadata.activeHostAuthorization,'NOT_RUN');
  assert.equal(result.metadata.realRendererFrame,'NOT_ADMITTED');
  assert.equal(result.metadata.scientificCertification,'NOT_RUN');
});
test('Studio safely preserves malicious model content in script JSON but never as HTML',()=>{
  const s=cp();
  const attack='</script><img src=x onerror=alert(1)> & "bad"';
  s.parts[1].label=attack;
  const result=renderStudio(s);
  assert.ok(!result.html.includes('</script><img'));
  assert.ok(!result.html.includes('<img src=x'));
  assert.ok(result.html.includes('&lt;img'));
  const match=result.html.match(/<script type="application\/json" id="fab-studio-data">([\s\S]*?)<\/script>/);
  assert.ok(match);
  const bundle=JSON.parse(match[1]);
  assert.equal(bundle.scene.parts[1].label,attack);
  assert.equal(bundle.release,'HOLD');
});
test('Studio no false isometric renderer for PHYSICAL and FORMAL scenes',()=>{
  for(const representation of ['PHYSICAL','FORMAL']){
    const s=cp();s.representation=representation;
    const x=renderStudio(s);
    assert.deepEqual(x.metadata.views,['2d']);
    assert.equal(x.metadata.isoStatus,'NOT_RUN');
    assert.match(x.html,/aria-disabled="true"/);
    assert.equal(x.metadata.realRendererFrame,'NOT_ADMITTED');
  }
});
test('Studio output deterministic and source witness is correctly hashed',()=>{
  const s=cp(),a=renderStudio(s),b=renderStudio(s);
  assert.equal(a.html,b.html);
  assert.deepEqual(a.metadata,b.metadata);
  assert.equal(a.metadata.outputDigest,'sha256:'+sha256(a.html));
  assert.equal(a.metadata.sourceDigest,'sha256:'+sha256(canonicalJSON(s)));
  assert.equal(a.metadata.claim,'MODEL_DERIVED_INTERACTIVE_VIEW_NOT_PROOF');
});
test('Studio oversized input is rejected, not silently rendered',()=>{
  const scene=cp();
  scene.parts=Array.from({length:301},(_,i)=>({...scene.parts[0],id:'part'+i,x:i*3}));
  scene.links=[];scene.observables=[];
  assert.throws(()=>renderStudio(scene),/studio cap/);
  assert.throws(()=>exportInterchange(scene,'cytoscape'),/portable graph cap/);
});
test('CLI studio produces real standalone HTML and evidence witness with release HOLD',()=>{
  temp(dir=>{
    const inFile=join(dir,'scene.json'),out=join(dir,'studio.html');
    writeFileSync(inFile,JSON.stringify(cp()));
    const run=spawnSync(process.execPath,['bin/fab-visual.mjs','studio',inFile,out],{cwd:root,encoding:'utf8'});
    assert.equal(run.status,0,run.stderr);
    assert.match(readFileSync(out,'utf8'),/data-view="compare"/);
    const receipt=JSON.parse(readFileSync(out+'.witness.json','utf8'));
    assertHostHold(receipt);
    assert.equal(receipt.views.length,3);
  });
});
test('CLI all four interchange formats produce correct MIME extensions and digest receipts',()=>{
  temp(dir=>{
    const input=join(dir,'scene.json');writeFileSync(input,JSON.stringify(cp()));
    for(const format of FORMATS){
      const extension=format==='reactflow'||format==='cytoscape'?'json':format==='mermaid'?'mmd':'dot';
      const output=join(dir,format+'.'+extension);
      const run=spawnSync(process.execPath,['bin/fab-visual.mjs','interchange',input,format,output],{cwd:root,encoding:'utf8'});
      assert.equal(run.status,0,format+' '+run.stderr);
      const text=readFileSync(output,'utf8');
      const witness=JSON.parse(readFileSync(output+'.witness.json','utf8'));
      assert.equal(witness.output_digest,'sha256:'+sha256(text));
      assertHostHold(witness);
    }
  });
});
test('CLI refuses in-place source overwrite and wrong export extension',()=>{
  temp(dir=>{
    const input=join(dir,'scene.json');writeFileSync(input,JSON.stringify(cp()));
    for(const cmd of [['studio',input,input],['interchange',input,'dot',input]]){
      const run=spawnSync(process.execPath,['bin/fab-visual.mjs',...cmd],{cwd:root,encoding:'utf8'});
      assert.notEqual(run.status,0);
      assert.ok(readFileSync(input,'utf8').includes('fab.scene.v0.2'));
    }
    const bad=spawnSync(process.execPath,['bin/fab-visual.mjs','interchange',input,'dot',join(dir,'wrong.json')],{cwd:root,encoding:'utf8'});
    assert.notEqual(bad.status,0);
    assert.match(bad.stderr,/expected .dot/);
  });
});
