/**
 * FAB.VISUAL Ω11J — dependency-free, loss-explicit graph interoperability.
 *
 * Output targets are DATA contracts only; no external runtime source is bundled:
 *   XYFlow / React Flow (MIT), Cytoscape.js (MIT), Mermaid (MIT), Graphviz DOT.
 *
 * A graph view cannot independently certify containment geometry, observable
 * agreement, execution policy, physical metrology or rendered depth.
 */
import {assertScene} from '../visual/contract.mjs';
import {canonicalJSON,sha256} from '../visual/provenance.mjs';

export const FORMATS=Object.freeze(['reactflow','cytoscape','mermaid','dot']);
const FLOWS=new Set(['signal','energy','material','control','information','dependency','mechanical']);
const encoded=value=>JSON.stringify(value,null,2)+'\n';
const center=part=>({x:part.x+part.w/2,y:part.y+part.h/2});
function bounded(scene) {
  assertScene(scene);
  if(scene.parts.length>300 || (scene.links||[]).length>800 ||
      (scene.observables||[]).length>300)
    throw Error('portable graph cap exceeded: 300 parts, 800 links, 300 observables');
  return scene;
}
function base(scene,target) {
  return {
    schema:'fab.visual.interchange.v1',
    target,
    scene_id:scene.id,
    representation:scene.representation,
    source_model:{id:scene.model.id,revision:scene.model.revision,authority:scene.model.authority},
    source_digest:'sha256:'+sha256(canonicalJSON(scene)),
    source_claim:scene.claim,
    release:'HOLD',
    semantic_boundary:'SCENEIR_GRAPH_PROJECTION_NOT_MODEL_OR_GEOMETRY_PROOF',
    lossy_fields:['physical_metric_depth','actual_source_execution','frame_presentation']
  };
}
function flowEdge(edge,i){
  if(!FLOWS.has(edge.flow))throw Error('unrecognized flow');
  return {
    id:'flow-'+i,
    source:edge.from,
    target:edge.to,
    flow:edge.flow,
    ...(edge.fromPort===undefined?{}:{fromPort:edge.fromPort}),
    ...(edge.toPort===undefined?{}:{toPort:edge.toPort})
  };
}
function reactflow(scene){
  const edges=(scene.links||[]).map((edge,i)=>{
    const e=flowEdge(edge,i);
    return {id:e.id,source:e.source,target:e.target,type:'smoothstep',
      label:e.flow,data:{flow:e.flow,fromPort:e.fromPort??null,toPort:e.toPort??null,
        evidence:'SCENEIR_SOURCE_DATA_ONLY'}};
  });
  const nodes=scene.parts.map(part=>({
    id:part.id,type:'default',
    position:{x:part.x,y:part.y},
    data:{label:part.label,status:part.status||'NEUTRAL',parent:part.parent||null,
      ports:part.ports||[],semantic_id:part.id},
    style:{width:part.w,height:part.h}
  }));
  return encoded({...base(scene,'xyflow.reactflow.nodes-edges.v1'),nodes,edges,
    observables:scene.observables||[]});
}
function cytoscape(scene){
  const nodes=scene.parts.map(p=>({
    data:{id:p.id,label:p.label,status:p.status||'NEUTRAL',
      ...(p.parent?{parent:p.parent}:{})},
    position:center(p),
    classes:'fab-semantic-part'
  }));
  const edges=(scene.links||[]).map((link,i)=>{
    const e=flowEdge(link,i);
    return {data:{id:e.id,source:e.source,target:e.target,flow:e.flow,
      fromPort:e.fromPort||null,toPort:e.toPort||null},classes:'fab-scene-link'};
  });
  return encoded({...base(scene,'cytoscape.elements.v1'),
    elements:{nodes,edges},layout:{name:'preset'},observables:scene.observables||[]});
}
function mermaidSafe(value) {
  // Double-quoted Mermaid labels; never let model text terminate the node
  // statement, embed a second graph line or become a directive.
  return String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;')
    .replace(/[\r\n\t\f\v\u2028\u2029[\]{}()|;#]/g,' ');
}
function mermaid(scene){
  const ids=new Map(scene.parts.map((p,i)=>[p.id,'n'+i]));
  const lines=['flowchart LR'];
  scene.parts.forEach((p,i)=>lines.push('  n'+i+'["'+mermaidSafe(p.label)+'"]'));
  (scene.links||[]).forEach(link=>{
    lines.push('  '+ids.get(link.from)+' -->|'+link.flow+'| '+ids.get(link.to));
  });
  // Machine-readable full source fields and evidence are provided by
  // the separate witness receipt, not by untrusted Mermaid comments.
  return lines.join('\n')+'\n';
}
function dotSafe(s){
  return '"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"')
    .replace(/[\r\n\t\v\f\u2028\u2029]/g,' ')
    .replace(/[\x00-\x1f\x7f]/g,' ')+'"';
}
function dot(scene){
  const ids=new Map(scene.parts.map((p,i)=>[p.id,'n'+i]));
  const lines=['digraph FabVisual {','  graph [rankdir=LR];','  node [shape=box];'];
  scene.parts.forEach((p,i)=>lines.push('  n'+i+' [label='+dotSafe(p.label)+'];'));
  (scene.links||[]).forEach(link=>
    lines.push('  '+ids.get(link.from)+' -> '+ids.get(link.to)+' [label='+dotSafe(link.flow)+'];'));
  lines.push('}');
  return lines.join('\n')+'\n';
}
export function exportInterchange(scene,format) {
  bounded(scene);
  if(!FORMATS.includes(format))throw Error('unknown interchange format: '+String(format));
  const text=({reactflow,cytoscape,mermaid,dot})[format](scene);
  const mediaType=(format==='reactflow'||format==='cytoscape')?'application/json':'text/plain';
  const extension=(format==='reactflow'||format==='cytoscape')?'json':format==='mermaid'?'mmd':'dot';
  const receipt={
    schema:'fab.visual.interchange-witness.v1',
    source_digest:'sha256:'+sha256(canonicalJSON(scene)),
    output_digest:'sha256:'+sha256(text),
    target:format,
    representation:scene.representation,
    claim:scene.claim,
    no_external_code_executed:true,
    output_scope:'GRAPH_PROJECTION_NOT_SCIENTIFIC_OR_AUTHORIZATION_PROOF',
    release:'HOLD'
  };
  return {format,mediaType,extension,text,receipt};
}
