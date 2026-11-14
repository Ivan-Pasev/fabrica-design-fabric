/**
 * Ω11K: offline browser-only presentation editor.
 * This is independently downloadable source editing, not an authorization
 * interface, geometry certification, peer-reviewed model edit or cloud sync.
 *
 * Pure function body is embedded into the generated standalone HTML.
 */
export function studioEditorClient(importGraphAgainstSource){
  'use strict';
  const data=JSON.parse(document.getElementById('fab-studio-data').textContent);
  const base=structuredClone(data.scene);
  const stage=document.getElementById('stage');
  const msg=document.getElementById('edit-status');
  const comp=document.getElementById('edit-part');
  const from=document.getElementById('edit-from');
  const to=document.getElementById('edit-to');
  const flow=document.getElementById('edit-flow');
  const fieldIds=['edit-x','edit-y','edit-w','edit-h'];
  const fields=fieldIds.map(id=>document.getElementById(id));
  const undo=document.getElementById('edit-undo'),redo=document.getElementById('edit-redo');
  const importFile=document.getElementById('graph-import-file');
  const importFormat=document.getElementById('graph-import-format');
  const limitedKinds=new Set(['signal','energy','material','control','information','dependency','mechanical']);
  let timeline=[structuredClone(base)],index=0,dirty=false;
  const snapshot=()=>timeline[index];
  const selectOption=(parent,value,label)=>{
    const item=document.createElement('option');item.value=value;item.textContent=label;
    parent.appendChild(item);
  };
  for(const p of base.parts){
    for(const sel of [comp,from,to])selectOption(sel,p.id,p.label+' ('+p.id+')');
  }
  for(const kind of limitedKinds)selectOption(flow,kind,kind);
  flow.value='control';
  to.selectedIndex=Math.min(1,base.parts.length-1);
  const copy=x=>structuredClone(x);
  function checkLocal(scene){
    if(!scene||scene.parts.length!==base.parts.length||scene.parts.length>300||
       !Array.isArray(scene.links)||scene.links.length>800)throw Error('Invalid bounded edited scene');
    const known=new Map(base.parts.map(p=>[p.id,p]));
    const ids=new Set();
    for(const p of scene.parts){
      if(!known.has(p.id)||ids.has(p.id))throw Error('Component identity cannot change');
      ids.add(p.id);
      for(const k of ['x','y','w','h']){
        if(typeof p[k]!=='number'||!Number.isFinite(p[k]))throw Error('Invalid finite layout geometry');
      }
      if(p.w<=0||p.h<=0||p.w>100000||p.h>100000||Math.abs(p.x)>1e6||Math.abs(p.y)>1e6)
        throw Error('Layout dimensions outside safe bounds');
      const old=known.get(p.id);
      if(p.status!==old.status||p.parent!==old.parent||JSON.stringify(p.ports||[])!==JSON.stringify(old.ports||[]))
        throw Error('Model status, hierarchy and typed ports cannot change');
    }
    for(const link of scene.links){
      if(!known.has(link.from)||!known.has(link.to)||!limitedKinds.has(link.flow))
        throw Error('Unknown flow or endpoint');
      for(const [pid,part] of [[link.from,known.get(link.from)],[link.to,known.get(link.to)]]){
        if(part.ports?.length && !part.ports.some(x=>x.flow===link.flow))
          throw Error('Node '+pid+' lacks matching typed flow port');
      }
    }
    if(JSON.stringify(scene.model)!==JSON.stringify(base.model)||
       JSON.stringify(scene.observables||[])!==JSON.stringify(base.observables||[])||
       JSON.stringify(scene.claim)!==JSON.stringify(base.claim))
      throw Error('Scientific/authorization model data cannot change');
  }
  function edited(svgMode){
    const s=snapshot();
    const ns='http://www.w3.org/2000/svg',el=(name,attrs={})=>{
      const x=document.createElementNS(ns,name);
      for(const [k,v] of Object.entries(attrs))x.setAttribute(k,String(v));
      return x;
    };
    const root=el('svg',{xmlns:ns,viewBox:'0 0 1100 690',width:1100,height:690,role:'img','aria-label':'Edited local reference diagram - not source-certified geometry'});
    const styles=el('style');styles.textContent='.edge{stroke:#7386a1;stroke-width:2;fill:none}.part rect{fill:#e7eef8;stroke:#617c9a;stroke-width:2}.part text{font:600 14px sans-serif;fill:#1c3550}.part[data-status="BLOCKED"] rect{fill:#ffe5e3;stroke:#b74242}.part[data-selected="true"] rect{stroke:#bf6500;stroke-width:4}';
    root.appendChild(styles);
    const title=el('title');title.textContent=s.id+' — derived local preview';root.appendChild(title);
    const mapping=new Map(s.parts.map(p=>[p.id,p]));
    for(const [i,l] of s.links.entries()){
      const a=mapping.get(l.from),b=mapping.get(l.to);
      const p=el('path',{class:'edge','data-flow':l.flow,'data-edge':i,
        d:'M'+(a.x+a.w/2)+' '+(a.y+a.h/2)+' L'+(b.x+b.w/2)+' '+(b.y+b.h/2)});
      const t=el('title');t.textContent=l.from+' to '+l.to+' ('+l.flow+')';p.appendChild(t);root.appendChild(p);
    }
    for(const p of s.parts){
      const g=el('g',{class:'part node','data-part':p.id,'data-status':p.status||'NEUTRAL',role:'group','aria-label':p.label});
      const rect=el('rect',{x:p.x,y:p.y,width:p.w,height:p.h,rx:11});
      const label=el('text',{x:p.x+p.w/2,y:p.y+p.h/2+4,'text-anchor':'middle'});
      label.textContent=p.label;
      const title=el('title');title.textContent=p.label+' / '+(p.status||'NEUTRAL');
      g.append(rect,label,title);root.appendChild(g);
    }
    return root;
  }
  function updateStatus(message){
    msg.textContent=message+' · VISUAL EDIT ONLY · original source/model unchanged · release HOLD';
    document.getElementById('edit-history').textContent=
      'Local snapshots '+(index+1)+' / '+timeline.length;
    undo.disabled=index===0;redo.disabled=index>=timeline.length-1;
    dirty=JSON.stringify(snapshot())!==JSON.stringify(base);
    const unverifiedIsometric=[...document.querySelectorAll('button[data-view]')]
      .filter(btn=>btn.dataset.view!=='2d');
    for(const btn of unverifiedIsometric)btn.disabled=dirty||!data.iso;
    document.getElementById('edit-mode').textContent=dirty?
      'Edited reference: Anatomy 3D disabled until validated recompile':'Original source view';
  }
  function drawCurrent(){
    const scene=snapshot();
    if(dirty){
      document.querySelector('button[data-view="2d"]').click();
      stage.replaceChildren(edited());
    }else{
      document.querySelector('button[data-view="2d"]').click();
    }
    const box=scene.parts.find(p=>p.id===comp.value)||scene.parts[0];
    for(const [i,key] of ['x','y','w','h'].entries())fields[i].value=String(box[key]);
    document.getElementById('scene-state').textContent=dirty?
      'Derived local presentation · no source Anatomy proof · release HOLD':
      'Original validated scene · release HOLD';
  }
  function commit(value,statement){
    checkLocal(value);
    if(index+1<timeline.length)timeline=timeline.slice(0,index+1);
    timeline.push(copy(value));
    if(timeline.length>33)timeline.shift();
    index=timeline.length-1;
    dirty=JSON.stringify(snapshot())!==JSON.stringify(base);
    drawCurrent();updateStatus(statement);
  }
  comp.addEventListener('change',()=>{
    const p=snapshot().parts.find(x=>x.id===comp.value);
    if(p)for(const [i,key] of ['x','y','w','h'].entries())fields[i].value=String(p[key]);
  });
  document.getElementById('edit-apply').addEventListener('click',()=>{
    try{
      const s=copy(snapshot()),p=s.parts.find(x=>x.id===comp.value);
      if(!p)throw Error('Choose a source component');
      for(const [i,key] of ['x','y','w','h'].entries())p[key]=Number(fields[i].value);
      s.visualEdit={schema:'fab.visual.visual-edit.v1',sourceDigest:data.sourceDigest,
        provenance:'DERIVED_PRESENTATION_ONLY_NOT_MODEL_AUTHORITY',
        operation:'component_geometry',partId:p.id,release:'HOLD'};
      commit(s,'Updated '+p.id+' layout');
    }catch(e){updateStatus('REJECTED: '+e.message);}
  });
  document.getElementById('edit-add-link').addEventListener('click',()=>{
    try{
      if(from.value===to.value)throw Error('Choose distinct source components');
      const s=copy(snapshot()),link={from:from.value,to:to.value,flow:flow.value};
      if(s.links.some(e=>JSON.stringify([e.from,e.to,e.flow])===JSON.stringify([link.from,link.to,link.flow])))
        throw Error('Duplicate directed source link');
      s.links.push(link);
      s.visualEdit={schema:'fab.visual.visual-edit.v1',sourceDigest:data.sourceDigest,
        provenance:'DERIVED_PRESENTATION_ONLY_NOT_MODEL_AUTHORITY',
        operation:'connection_layout',release:'HOLD'};
      commit(s,'Created illustrative '+link.flow+' connection');
    }catch(e){updateStatus('REJECTED: '+e.message);}
  });
  undo.addEventListener('click',()=>{
    if(index>0){index--;dirty=JSON.stringify(snapshot())!==JSON.stringify(base);drawCurrent();updateStatus('Undo');}
  });
  redo.addEventListener('click',()=>{
    if(index<timeline.length-1){index++;dirty=JSON.stringify(snapshot())!==JSON.stringify(base);drawCurrent();updateStatus('Redo');}
  });
  async function importFileAction(){
    const file=importFile.files?.[0];if(!file)return;
    try{
      if(file.size>2000000)throw Error('Graph file exceeds 2 MB');
      const format=importFormat.value;
      const x=JSON.parse(await file.text());
      const imported=importGraphAgainstSource(x,format,base,data.sourceDigest);
      const result=imported.scene;
      checkLocal(result);
      if(JSON.stringify(result)===JSON.stringify(base)){
        updateStatus('Imported unmodified '+format+' graph');
        return;
      }
      commit(result,'Imported '+format+' derivative ('+imported.report.changed_parts.length+' moved/relabeled parts)');
    }catch(e){updateStatus('IMPORT REJECTED: '+e.message);}
    finally{importFile.value='';}
  }
  importFile.addEventListener('change',importFileAction);
  function safeDownload(kind,content,extension,mime){
    const blob=new Blob([content],{type:mime+';charset=utf-8'});
    const url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download='fab-visual-edited-'+kind+'.'+extension;
    document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),3000);
    updateStatus('Exported current edited '+kind);
  }
  function derivedGraph(kind){
    const s=snapshot();
    const obj={schema:'fab.visual.interchange.v1',
      target:kind==='reactflow'?'xyflow.reactflow.nodes-edges.v1':'cytoscape.elements.v1',
      scene_id:s.id,representation:s.representation,
      source_model:{id:s.model.id,revision:s.model.revision,authority:s.model.authority},
      source_digest:data.sourceDigest,source_claim:s.claim,release:'HOLD',
      semantic_boundary:'DERIVED_PRESENTATION_NOT_SOURCE_AUTHORITY',
      lossy_fields:['model_execution','physical_depth','gpu_presented_frame'],
      observables:s.observables||[]};
    if(kind==='reactflow'){
      obj.nodes=s.parts.map(p=>({id:p.id,type:'default',
        position:{x:p.x,y:p.y},style:{width:p.w,height:p.h},
        data:{label:p.label,status:p.status||'NEUTRAL',parent:p.parent||null,
          ports:p.ports||[],semantic_id:p.id}}));
      obj.edges=s.links.map((e,i)=>({id:'flow-'+i,source:e.from,target:e.to,
        label:e.flow,type:'smoothstep',data:{flow:e.flow,
          fromPort:e.fromPort??null,toPort:e.toPort??null,
          evidence:'DERIVED_GRAPH_NOT_SOURCE_AUTHORITY'}}));
    }else{
      obj.elements={nodes:s.parts.map(p=>({data:{id:p.id,label:p.label,
        status:p.status||'NEUTRAL',...(p.parent?{parent:p.parent}:{})},
        position:{x:p.x+p.w/2,y:p.y+p.h/2},classes:'fab-semantic-part'})),
        edges:s.links.map((e,i)=>({data:{id:'flow-'+i,source:e.from,target:e.to,
          flow:e.flow,fromPort:e.fromPort??null,toPort:e.toPort??null},
          classes:'fab-scene-link'}))};
      obj.layout={name:'preset'};
    }
    return JSON.stringify(obj,null,2)+'\n';
  }
  document.addEventListener('click',event=>{
    const b=event.target.closest('button[data-export]');
    if(!b||!dirty)return;
    const kind=b.dataset.export;
    event.preventDefault();event.stopImmediatePropagation();
    if(kind==='scene')safeDownload(kind,JSON.stringify(snapshot(),null,2)+'\n','json','application/json');
    else if(kind==='svg')safeDownload(kind,edited().outerHTML,'svg','image/svg+xml');
    else if(kind==='reactflow'||kind==='cytoscape')safeDownload(kind,derivedGraph(kind),'json','application/json');
    else updateStatus('Export '+kind+' requires CLI recompile; refusing stale original output');
  },true);
  comp.dispatchEvent(new Event('change'));
  updateStatus('Original scene loaded. Make a local visual edit.');
}
