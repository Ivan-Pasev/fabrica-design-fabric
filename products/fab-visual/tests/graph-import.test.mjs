import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {exportInterchange} from '../src/adapters/interchange.mjs';
import {importInterchange,importGraphAgainstSource} from '../src/adapters/graph-import.mjs';
import {sha256,canonicalJSON} from '../src/visual/provenance.mjs';

const source=JSON.parse(readFileSync(new URL('../fixtures/policy-scene.json',import.meta.url),'utf8'));
const copy=x=>structuredClone(x);
const digest='sha256:'+sha256(canonicalJSON(source));
const envelope=format=>JSON.parse(exportInterchange(source,format).text);
const change=(format,modify)=>{
  const v=envelope(format);modify(v);
  return importInterchange(v,format,source);
};
for(const format of ['reactflow','cytoscape']){
  test(format+' exact export/import retains SceneIR without altering authority',()=>{
    const a=importInterchange(envelope(format),format,source);
    assert.deepEqual(a.scene,source);
    assert.deepEqual(a.report.changed_parts,[]);
    assert.equal(a.report.edge_changed,false);
    assert.equal(a.report.authenticated_source,'NOT_ESTABLISHED_SELF_REPORTED_DIGEST_ONLY');
    assert.equal(a.receipt.release,'HOLD');
    assert.equal(a.receipt.outputDigest,'sha256:'+sha256(canonicalJSON(source)));
    assert.deepEqual(source,copy(source));
  });
  test(format+' changing visual geometry adds explicit derivative provenance',()=>{
    const a=change(format,v=>{
      if(format==='reactflow'){v.nodes[0].position.x+=10;v.nodes[0].style.width+=5;}
      else {v.elements.nodes[0].position.x+=10;}
    });
    assert.equal(a.scene.parts[0].x,50);
    assert.equal(a.scene.parts[0].w,format==='reactflow'?185:180);
    assert.equal(a.scene.model.authority,source.model.authority);
    assert.deepEqual(a.scene.observables,source.observables);
    assert.deepEqual(a.scene.claim,source.claim);
    assert.equal(a.scene.visualEdit.sourceDigest,digest);
    assert.equal(a.scene.visualEdit.release,'HOLD');
    assert.deepEqual(a.report.changed_parts,['intake']);
  });
  test(format+' import can add typed graph link but cannot add arbitrary nodes',()=>{
    const v=envelope(format);
    if(format==='reactflow')v.edges.push({id:'flow-new',source:'intake',target:'human',data:{flow:'control'}});
    else v.elements.edges.push({data:{id:'flow-new',source:'intake',target:'human',flow:'control'}});
    const x=importInterchange(v,format,source);
    assert.equal(x.scene.links.length,4);
    assert.equal(x.report.edge_changed,true);
    assert.equal(x.scene.visualEdit.provenance,'DERIVED_PRESENTATION_ONLY_NOT_MODEL_AUTHORITY');
  });
  test(format+' rejects changed source model identity, claim and release',()=>{
    for(const [key,value] of [['scene_id','attacker'],['source_digest','sha256:'+'0'.repeat(64)],['representation','PHYSICAL'],['release','ALLOW']]){
      const v=envelope(format);v[key]=value;
      assert.throws(()=>importInterchange(v,format,source),/GRAPH_IMPORT_REJECT/);
    }
    const v=envelope(format);v.source_model.authority='attacker';
    assert.throws(()=>importInterchange(v,format,source),/model authority mismatch/);
    const x=envelope(format);x.source_claim.status='CERTIFIED';
    assert.throws(()=>importInterchange(x,format,source),/claim or release mutation/);
  });
  test(format+' rejects status/parent privilege tampering',()=>{
    const v=envelope(format),n=format==='reactflow'?v.nodes[0].data:v.elements.nodes[0].data;
    n.status='RELEASED';
    assert.throws(()=>importInterchange(v,format,source),/authorization\/status mutation/);
    n.status='NEUTRAL';n.parent='release';
    assert.throws(()=>importInterchange(v,format,source),/hierarchy changed/);
  });
  test(format+' rejects duplicate identities and dangling target',()=>{
    const v=envelope(format);
    const nodes=format==='reactflow'?v.nodes:v.elements.nodes;
    if(format==='reactflow')nodes[1].id='intake';
    else nodes[1].data.id='intake';
    assert.throws(()=>importInterchange(v,format,source),/duplicate or missing model component identity/);
    const t=envelope(format),edges=format==='reactflow'?t.edges:t.elements.edges;
    if(format==='reactflow')edges[0].target='missing';
    else edges[0].data.target='missing';
    assert.throws(()=>importInterchange(t,format,source),/endpoints or flow type/);
  });
  test(format+' rejects forged flow, invalid port, duplicate edge and values',()=>{
    const v=envelope(format),edges=format==='reactflow'?v.edges:v.elements.edges;
    edges[0].data.flow='authorization_magic';
    assert.throws(()=>importInterchange(v,format,source),/flow type/);
    const z=envelope(format),ed=format==='reactflow'?z.edges:z.elements.edges;
    ed[0].data.fromPort='unknown';
    assert.throws(()=>importInterchange(z,format,source),/unverified fromPort/);
    const w=envelope(format),e=format==='reactflow'?w.edges:w.elements.edges;
    e.push(structuredClone(e[0]));
    assert.throws(()=>importInterchange(w,format,source),/duplicate graph edge/);
    const bad=envelope(format),nodes=format==='reactflow'?bad.nodes:bad.elements.nodes;
    nodes[0].position.x=Infinity;
    assert.throws(()=>importInterchange(bad,format,source),/nonfinite\/invalid node position/);
  });
}
test('importer refuses unversioned raw graph without explicit source authority',()=>{
  assert.throws(()=>importInterchange({nodes:[],edges:[]},'reactflow',source),/trusted interchange envelope/);
  assert.throws(()=>importInterchange({},'cytoscape',source),/trusted interchange envelope/);
});
test('importer rejects unsupported graph and missing digest',()=>{
  assert.throws(()=>importInterchange({},'mermaid',source),/supported imports/);
  assert.throws(()=>importGraphAgainstSource(envelope('reactflow'),'reactflow',source,undefined),/source digest missing/);
});
test('script-admissible scene imports preserve no network or host privileges',()=>{
  const v=envelope('reactflow');
  v.nodes[0].data.label='</script><img src=x onerror=alert(1)>';
  const a=importInterchange(v,'reactflow',source);
  assert.equal(a.scene.parts[0].label,'</script><img src=x onerror=alert(1)>');
  assert.equal(a.report.preserved_authority,true);
  assert.equal(a.receipt.sourceAuthorityTransferred,false);
  assert.equal(a.receipt.release,'HOLD');
});
test('importer exactly limits graph size',()=>{
  const v=envelope('reactflow');
  for(let i=0;i<810;i++)v.edges.push({id:'f'+i,source:'intake',target:'human',data:{flow:'control'}});
  assert.throws(()=>importInterchange(v,'reactflow',source),/excessive graph elements/);
});
test('model observables cannot silently become unverified results',()=>{
  const v=envelope('cytoscape');
  v.observables[0].value='RELEASED';
  assert.throws(()=>importInterchange(v,'cytoscape',source),/source observables mismatch/);
});
