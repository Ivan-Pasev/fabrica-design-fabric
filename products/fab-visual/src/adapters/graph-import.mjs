/**
 * FAB.VISUAL Ω11K — strict, source-anchored graph import.
 * The pure inner function is portable into the offline Studio browser; the
 * Node wrapper additionally enforces the native SceneIR contract and SHA256.
 *
 * Only imported graph presentation changes are admitted, not changes to model
 * identity, status/approval, source authority, scientific evidence or release.
 */
import {assertScene} from '../visual/contract.mjs';
import {canonicalJSON,sha256} from '../visual/provenance.mjs';

export function importGraphAgainstSource(envelope,format,sourceScene,expectedSourceDigest){
  const err=s=>{throw new Error('GRAPH_IMPORT_REJECT: '+s)};
  const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
  const str=x=>typeof x==='string'&&x.length>0&&x.length<=300;
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const positive=x=>finite(x)&&x>0&&x<=100000;
  const point=x=>finite(x)&&Math.abs(x)<=1000000;
  const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  if(!['reactflow','cytoscape'].includes(format))err('supported imports: reactflow and cytoscape');
  if(!object(sourceScene)||!Array.isArray(sourceScene.parts)||!(sourceScene.links===undefined||Array.isArray(sourceScene.links))||!object(sourceScene.model))err('validated seed scene required');
  if(sourceScene.parts.length>300||(sourceScene.links||[]).length>800)err('bounded source scene exceeded');
  if(!str(expectedSourceDigest)||!/^sha256:[0-9a-f]{64}$/.test(expectedSourceDigest))err('source digest missing');
  if(!object(envelope)||envelope.schema!=='fab.visual.interchange.v1')err('trusted interchange envelope required; arbitrary external JSON not admitted');
  if(envelope.target!==(format==='reactflow'?'xyflow.reactflow.nodes-edges.v1':'cytoscape.elements.v1'))err('interchange target mismatch');
  if(envelope.source_digest!==expectedSourceDigest)err('source digest mismatch');
  if(envelope.scene_id!==sourceScene.id||envelope.representation!==sourceScene.representation)err('source scene identity mismatch');
  if(!object(envelope.source_model)||!eq(envelope.source_model,{id:sourceScene.model.id,revision:sourceScene.model.revision,authority:sourceScene.model.authority}))err('model authority mismatch');
  if(!eq(envelope.source_claim,sourceScene.claim)||envelope.release!=='HOLD')err('claim or release mutation rejected');
  if(!Array.isArray(envelope.observables)||!eq(envelope.observables,sourceScene.observables||[]))err('source observables mismatch');
  const nodes=format==='reactflow'?envelope.nodes:envelope.elements?.nodes;
  const edges=format==='reactflow'?envelope.edges:envelope.elements?.edges;
  if(!Array.isArray(nodes)||!Array.isArray(edges)||nodes.length!==sourceScene.parts.length||edges.length>800)err('missing or excessive graph elements');
  const known=new Map(sourceScene.parts.map(p=>[p.id,p]));
  if(known.size!==sourceScene.parts.length)err('duplicate source IDs');
  const seen=new Set(),parts=[],changedParts=[],changeTypes=new Set();
  for(const entry of nodes){
    const x=format==='reactflow'?entry:entry?.data;
    const id=x?.id;
    if(!str(id)||!known.has(id)||seen.has(id))err('new, duplicate or missing model component identity');
    seen.add(id);
    const original=known.get(id),rawData=format==='reactflow'?entry.data:entry.data;
    if(!object(rawData))err('node attributes missing');
    const parent=rawData.parent??null;
    if(parent!==(original.parent??null))err('parent graph hierarchy changed');
    if((rawData.status??'NEUTRAL')!==(original.status??'NEUTRAL'))err('node authorization/status mutation');
    if(format==='reactflow'){
      if(!eq(rawData.ports||[],original.ports||[]))err('typed model ports changed');
      if(rawData.semantic_id!==id)err('semantic node identity mismatch');
    }
    const p=format==='reactflow'?entry.position:entry.position;
    if(!object(p)||!point(p.x)||!point(p.y))err('nonfinite/invalid node position');
    let w=original.w,h=original.h;
    if(format==='reactflow'){
      if(!object(entry.style)||!positive(entry.style.width)||!positive(entry.style.height))err('invalid node dimensions');
      w=entry.style.width;h=entry.style.height;
    }
    const xcoord=format==='reactflow'?p.x:p.x-w/2,ycoord=format==='reactflow'?p.y:p.y-h/2;
    if(!point(xcoord)||!point(ycoord)||!positive(w)||!positive(h))err('node geometry outside bounds');
    if(!str(rawData.label))err('nonempty bounded model label required');
    const next={...original,x:xcoord,y:ycoord,w,h,label:rawData.label};
    for(const key of ['x','y','w','h','label'])if(next[key]!==original[key])changeTypes.add(key);
    if(!eq([next.x,next.y,next.w,next.h,next.label],[original.x,original.y,original.w,original.h,original.label]))changedParts.push(id);
    parts.push(next);
  }
  if(seen.size!==known.size)err('missing source model node');
  // Preserve source part order rather than downstream editor collection order.
  const order=new Map(parts.map(p=>[p.id,p]));
  const ordered=sourceScene.parts.map(p=>order.get(p.id));
  const flowKinds=new Set(['signal','energy','material','control','information','dependency','mechanical']);
  const newLinks=[],edgeIds=new Set();
  for(const [i,entry] of edges.entries()){
    const d=format==='reactflow'?entry?.data:entry?.data;
    const eid=format==='reactflow'?entry?.id:d?.id;
    if(!str(eid)||edgeIds.has(eid))err('missing or duplicate graph edge identity');
    edgeIds.add(eid);
    const from=format==='reactflow'?entry?.source:d?.source;
    const to=format==='reactflow'?entry?.target:d?.target;
    const flow=d?.flow;
    if(!known.has(from)||!known.has(to)||!flowKinds.has(flow))err('invalid graph endpoints or flow type');
    const fp=d?.fromPort??null,tp=d?.toPort??null;
    const a=known.get(from),b=known.get(to);
    if(fp!==null&&(!str(fp)||!a.ports?.some(p=>p.id===fp&&p.flow===flow)))err('unverified fromPort');
    if(tp!==null&&(!str(tp)||!b.ports?.some(p=>p.id===tp&&p.flow===flow)))err('unverified toPort');
    const link={from,to,flow,...(fp===null?{}:{fromPort:fp}),...(tp===null?{}:{toPort:tp})};
    newLinks.push(link);
  }
  const edgeChanged=!eq(newLinks,sourceScene.links||[]);
  const changed=changedParts.length>0||edgeChanged;
  const result={
    ...sourceScene,
    parts:ordered,
    links:newLinks,
    ...(changed?{visualEdit:{
      schema:'fab.visual.visual-edit.v1',
      sourceDigest:expectedSourceDigest,
      provenance:'DERIVED_PRESENTATION_ONLY_NOT_MODEL_AUTHORITY',
      format,
      changedParts,
      edgeChanged,
      changedKeys:[...changeTypes].sort(),
      release:'HOLD'
    }}:{})
  };
  const report={
    schema:'fab.visual.graph-import-report.v1',
    source_digest:expectedSourceDigest,
    result:'VALIDATED_DERIVED_SCENE',
    authenticated_source:'NOT_ESTABLISHED_SELF_REPORTED_DIGEST_ONLY',
    origin:'EXPLICIT_VALIDATED_SOURCE_SCENE',
    format,changed_parts:changedParts,edge_changed:edgeChanged,
    preserved_authority:true,geometry_units:'VISUAL_LAYOUT_ONLY',
    lost_fields:format==='cytoscape'?['node_width_height_updates_not_encoded_in_cytoscape_v1']:[],
    rejected_semantics:['authorization_changes','scientific_certification','upstream_model_revision_changes','new_or_deleted_source_nodes'],
    release:'HOLD'
  };
  return {scene:result,report};
}

export function importInterchange(input,format,sourceScene){
  assertScene(sourceScene);
  const digest='sha256:'+sha256(canonicalJSON(sourceScene));
  const value=typeof input==='string'?JSON.parse(input):input;
  const outcome=importGraphAgainstSource(value,format,sourceScene,digest);
  assertScene(outcome.scene);
  return {
    ...outcome,
    receipt:{
      schema:'fab.visual.graph-import-witness.v1',
      sourceDigest:digest,
      outputDigest:'sha256:'+sha256(canonicalJSON(outcome.scene)),
      result:outcome.report.result,
      importedFormat:format,
      sourceAuthorityTransferred:false,
      release:'HOLD'
    }
  };
}
