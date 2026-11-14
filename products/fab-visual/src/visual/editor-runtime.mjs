/**
 * Ω11K: offline browser-only presentation editor.
 * This is independently downloadable source editing, not an authorization
 * interface, geometry certification, peer-reviewed model edit or cloud sync.
 *
 * Pure function body is embedded into the generated standalone HTML.
 */
export function studioEditorClient(importGraphAgainstSource,visualDiff,forkVisualScene,zipStore,projectFiles){
  'use strict';
  const data=JSON.parse(document.getElementById('fab-studio-data').textContent);
  const base=structuredClone(data.scene);
  const stage=document.getElementById('stage');
  const msg=document.getElementById('edit-status');
  const comp=document.getElementById('edit-part');
  const from=document.getElementById('edit-from');
  const to=document.getElementById('edit-to');
  const flow=document.getElementById('edit-flow');
  const linkSelect=document.getElementById('edit-link-select');
  const removeLink=document.getElementById('edit-remove-link');
  const canvasConnect=document.getElementById('edit-canvas-connect');
  const canvasStatus=document.getElementById('edit-canvas-status');
  const forkSlug=document.getElementById('edit-fork-slug');
  const diffToggle=document.getElementById('edit-diff-toggle');
  const diffPanel=document.getElementById('edit-diff');
  const revision=document.getElementById('edit-revision');
  let connectMode=false,connectorOrigin=null;
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
  function edited(s=snapshot()){
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
  function refreshLinkChoices(){
    const selected=linkSelect.value;
    linkSelect.replaceChildren();
    for(const [i,edge] of snapshot().links.entries())
      selectOption(linkSelect,String(i),edge.from+' → '+edge.to+' ('+edge.flow+')');
    if([...linkSelect.options].some(option=>option.value===selected))linkSelect.value=selected;
    removeLink.disabled=linkSelect.options.length===0;
  }
  function syncRevisionChoices(){
    const wanted=String(index);
    revision.replaceChildren();
    for(const [i,s] of timeline.entries()){
      const suffix=i===index?' (current)':'';
      selectOption(revision,String(i),'Snapshot '+(i+1)+suffix);
    }
    revision.value=wanted;
  }
  function element(tag,className,value){
    const node=document.createElement(tag);
    if(className)node.className=className;
    if(value!==undefined)node.textContent=value;
    return node;
  }
  function presentDiff(){
    if(diffPanel.hidden)return;
    const ordinal=Number(revision.value);
    const proposed=timeline[ordinal]||snapshot();
    const report=visualDiff(base,proposed,data.sourceDigest);
    diffPanel.replaceChildren();
    diffPanel.appendChild(element('h4','', 'Source versus revision '+(ordinal+1)+' · VISUAL ONLY'));
    const summary=element('p','',
      report.move.length+' moved · '+report.resize.length+' resized · '+
      report.addedLinks.length+' added links · '+report.removedLinks.length+
      ' removed links · RELEASE HOLD');
    diffPanel.appendChild(summary);
    const pair=element('div','diff-pair');
    for(const [caption,sc] of [['Original source',base],['Selected local revision',proposed]]){
      const figure=element('figure','diff-panel');
      figure.appendChild(element('figcaption','',caption));
      figure.appendChild(edited(sc));
      pair.appendChild(figure);
    }
    diffPanel.appendChild(pair);
    const descriptions=[];
    for(const move of report.move)descriptions.push(move.id+' moved from ('+move.from.x+','+move.from.y+') to ('+move.to.x+','+move.to.y+')');
    for(const v of report.resize)descriptions.push(v.id+' resized from '+v.from.w+'×'+v.from.h+' to '+v.to.w+'×'+v.to.h);
    for(const link of report.addedLinks)descriptions.push('Added '+link.flow+': '+link.from+' → '+link.to);
    for(const link of report.removedLinks)descriptions.push('Removed '+link.flow+': '+link.from+' → '+link.to);
    const list=element('ul','diff-list');
    for(const row of (descriptions.length?descriptions:['No presentation changes in this snapshot'])){
      list.appendChild(element('li','',row));
    }
    diffPanel.appendChild(list);
    diffPanel.appendChild(element('p','','Model authority and original claim unchanged · no empirical validation · publisher signature NOT PRESENT'));
  }
  function syncCanvasTargets(){
    for(const item of stage.querySelectorAll('[data-part],path[data-edge]')){
      if(!item.hasAttribute('tabindex'))item.setAttribute('tabindex','0');
      if(!item.hasAttribute('role')||item.getAttribute('role')==='group')item.setAttribute('role','button');
      if(item.matches('path[data-edge]'))item.setAttribute('aria-label','Inspect illustrative connection '+item.getAttribute('data-edge'));
    }
  }
  function highlightSelectedLink(){
    const selected=linkSelect.value;
    for(const p of stage.querySelectorAll('path[data-edge]'))
      p.setAttribute('data-edit-selected',p.getAttribute('data-edge')===selected?'true':'false');
  }
  function updateStatus(message){
    msg.textContent=message+' · VISUAL EDIT ONLY · original source/model unchanged · release HOLD';
    document.getElementById('edit-history').textContent=
      'Local snapshots '+(index+1)+' / '+timeline.length;
    undo.disabled=index===0;redo.disabled=index>=timeline.length-1;
    refreshLinkChoices();
    syncRevisionChoices();
    syncCanvasTargets();
    highlightSelectedLink();
    dirty=JSON.stringify(snapshot())!==JSON.stringify(base);
    const unverifiedIsometric=[...document.querySelectorAll('button[data-view]')]
      .filter(btn=>btn.dataset.view!=='2d');
    for(const btn of unverifiedIsometric)btn.disabled=dirty||!data.iso;
    presentDiff();
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
    syncCanvasTargets();
    highlightSelectedLink();
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
  removeLink.addEventListener('click',()=>{
    try{
      const ordinal=Number(linkSelect.value);
      if(!Number.isInteger(ordinal)||ordinal<0||ordinal>=snapshot().links.length)
        throw Error('Choose an existing illustrative connection');
      const s=copy(snapshot()),removed=s.links.splice(ordinal,1)[0];
      s.visualEdit={schema:'fab.visual.visual-edit.v1',sourceDigest:data.sourceDigest,
        provenance:'DERIVED_PRESENTATION_ONLY_NOT_MODEL_AUTHORITY',
        operation:'connection_removal',link:{from:removed.from,to:removed.to,flow:removed.flow},release:'HOLD'};
      commit(s,'Removed illustrative '+removed.flow+' connection');
    }catch(e){updateStatus('REJECTED: '+e.message);}
  });
  function cancelCanvas(){
    connectMode=false;connectorOrigin=null;canvasConnect.setAttribute('aria-pressed','false');
    for(const node of stage.querySelectorAll('[data-connect-selected]'))
      node.removeAttribute('data-connect-selected');
  }
  canvasConnect.addEventListener('click',()=>{
    if(connectMode){cancelCanvas();canvasStatus.textContent='Canvas connection cancelled';}
    else {
      connectMode=true;connectorOrigin=null;canvasConnect.setAttribute('aria-pressed','true');
      canvasStatus.textContent='Select source component by pointer, Enter or Space';
    }
  });
  function chooseCanvasTarget(element){
    const target=element.closest('[data-part]');
    if(!target)return;
    const id=target.getAttribute('data-part');
    if(!base.parts.some(part=>part.id===id))return;
    if(!connectMode){
      comp.value=id;comp.dispatchEvent(new Event('change'));
      canvasStatus.textContent='Selected source component '+id+'; activate connector mode to connect';
      return;
    }
    if(!connectorOrigin){
      connectorOrigin=id;from.value=id;
      target.setAttribute('data-connect-selected','true');
      canvasStatus.textContent='From '+id+': select target source component';
      return;
    }
    if(id===connectorOrigin){
      canvasStatus.textContent='Select a DIFFERENT target component';
      return;
    }
    const origin=base.parts.find(p=>p.id===connectorOrigin),dest=base.parts.find(p=>p.id===id);
    const common=[...limitedKinds].filter(kind=>
      origin.ports?.some(p=>p.flow===kind)&&dest.ports?.some(p=>p.flow===kind));
    if(!common.length){
      canvasStatus.textContent='REJECTED: no compatible typed flow ports for '+connectorOrigin+' → '+id;
      return;
    }
    const fromId=connectorOrigin;
    from.value=fromId;to.value=id;flow.value=common[0];
    cancelCanvas();
    document.getElementById('edit-add-link').click();
    canvasStatus.textContent='Illustrative '+common[0]+' connector selected: '+fromId+' → '+id;
  }
  function handleCanvasElement(target){
    if(!(target instanceof Element))return;
    const path=target.closest('path[data-edge]');
    if(path){
      const ordinal=Number(path.getAttribute('data-edge'));
      if(Number.isInteger(ordinal)&&ordinal>=0&&ordinal<snapshot().links.length){
        linkSelect.value=String(ordinal);
        highlightSelectedLink();
        const l=snapshot().links[ordinal];
        canvasStatus.textContent='Selected illustrative '+l.flow+' connection '+l.from+' → '+l.to+
          ' · use Remove selected connection to edit';
      }
      return;
    }
    if(target.closest('[data-part]'))chooseCanvasTarget(target);
  }
  stage.addEventListener('click',e=>handleCanvasElement(e.target));
  stage.addEventListener('keydown',e=>{
    if(e.key!=='Enter'&&e.key!==' ')return;
    if(e.target instanceof Element&&e.target.closest('[data-part],path[data-edge]')){
      e.preventDefault();handleCanvasElement(e.target);
    }
  });
  linkSelect.addEventListener('change',highlightSelectedLink);
  new MutationObserver(syncCanvasTargets).observe(stage,{childList:true,subtree:true});
  diffToggle.addEventListener('click',()=>{
    diffPanel.hidden=!diffPanel.hidden;
    diffToggle.setAttribute('aria-expanded',String(!diffPanel.hidden));
    presentDiff();
  });
  revision.addEventListener('change',presentDiff);
  document.getElementById('edit-fork').addEventListener('click',()=>{
    try{
      visualDiff(base,snapshot(),data.sourceDigest);
      const fork=forkVisualScene(snapshot(),forkSlug.value,data.sourceDigest);
      const checked=visualDiff(base,fork,data.sourceDigest);
      if(!checked.sourceAuthorityPreserved)throw Error('source model authority changed');
      safeDownload('fork',JSON.stringify(fork,null,2)+'\n','json','application/json');
      canvasStatus.textContent='Exported visual-only fork: '+fork.id+' · source unmodified · HOLD';
    }catch(e){updateStatus('FORK REJECTED: '+e.message);}
  });
  document.getElementById('edit-project').addEventListener('click',()=>{
    try{
      const bundle=projectFiles(base,snapshot(),timeline,data.sourceDigest,
         forkSlug.value,visualDiff,forkVisualScene);
      const zip=zipStore(bundle.files);
      safeDownload('project',zip,'zip','application/zip');
      canvasStatus.textContent='Downloaded portable ZIP with original, fork, typed diff, timeline and manifest · HOLD';
    }catch(e){updateStatus('PROJECT REJECTED: '+e.message);}
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
    if(!b||(!dirty&&b.dataset.export!=='lineage'))return;
    const kind=b.dataset.export;
    event.preventDefault();event.stopImmediatePropagation();
    if(kind==='lineage'){
      const history={schema:'fab.visual.local-edit-history.v1',
        sourceDigest:data.sourceDigest,sourceSceneId:base.id,
        modelAuthority:base.model.authority,
        mode:'LOCAL_VISUAL_PRESENTATION_ONLY_NOT_AUTHORITY',
        currentOrdinal:index,
        snapshots:timeline.map((x,i)=>({ordinal:i,scene:x})),
        publisherSignature:'NOT_PRESENT',gpuPresentedFrame:'NOT_ADMITTED',
        realWorldValidity:'NOT_RUN',release:'HOLD'};
      safeDownload('lineage',JSON.stringify(history,null,2)+'\n','json','application/json');
    }
    else if(kind==='scene')safeDownload(kind,JSON.stringify(snapshot(),null,2)+'\n','json','application/json');
    else if(kind==='svg')safeDownload(kind,edited().outerHTML,'svg','image/svg+xml');
    else if(kind==='reactflow'||kind==='cytoscape')safeDownload(kind,derivedGraph(kind),'json','application/json');
    else updateStatus('Export '+kind+' requires CLI recompile; refusing stale original output');
  },true);
  comp.dispatchEvent(new Event('change'));
  updateStatus('Original scene loaded. Make a local visual edit.');
}
