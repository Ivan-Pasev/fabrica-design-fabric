/**
 * Ω11M: first-party, zero-dependency, pure local visual project contract.
 *
 * Browser-embeddable functions deliberately have no closure dependencies.
 * ZIP uses STORE and CRC32 for transport error detection, NOT signatures.
 * There is no scientific, hardware, host or release authorization.
 */

export function forkVisualScene(scene,slug,sourceDigest){
  const fail=x=>{throw Error('VISUAL_FORK_REJECT: '+x)};
  if(!scene||scene.schema!=='fab.scene.v0.2'||typeof scene.id!=='string'||
     !scene.model||!scene.claim||!Array.isArray(scene.parts))fail('valid original SceneIR required');
  if(typeof slug!=='string'||!/^[a-z0-9][a-z0-9-]{0,39}$/.test(slug)||
      slug.endsWith('-'))fail('slug must be 1-40 lowercase letters, digits or internal hyphens');
  if(typeof sourceDigest!=='string'||!/^sha256:[0-9a-f]{64}$/.test(sourceDigest))
    fail('canonical original source SHA-256 required');
  if(scene.fork||scene.id.includes('--fork-'))fail('nested fork not admitted without new source review');
  if(scene.claim.status!=='EXPLANATORY'&&scene.model.synthetic===true)
    fail('synthetic source claim escalated');
  if(scene.parts.length>300||(scene.links||[]).length>800||(scene.observables||[]).length>300)
    fail('scene bounded size exceeded');
  const original=JSON.parse(JSON.stringify(scene));
  const copy=JSON.parse(JSON.stringify(scene));
  copy.id=scene.id+'--fork-'+slug;
  copy.model.revision=scene.model.revision+'+visual-fork.'+slug;
  copy.fork={
    schema:'fab.visual.template-fork.v1',
    sourceSceneId:scene.id,
    sourceModelId:scene.model.id,
    sourceModelRevision:scene.model.revision,
    sourceDigest,
    visualRevision:slug,
    scope:'DERIVED_VISUAL_SCENE_NOT_MODEL_AUTHORITY',
    publisherSignature:'NOT_PRESENT',
    empiricalStatus:'NOT_RUN',hostAuthorization:'NOT_RUN',release:'HOLD'
  };
  if(JSON.stringify(original)!==JSON.stringify(scene))fail('input mutation');
  return copy;
}

export function visualDiff(source,derived,sourceDigest){
  const fail=x=>{throw Error('VISUAL_DIFF_REJECT: '+x)};
  if(!source||!derived||!Array.isArray(source.parts)||!Array.isArray(derived.parts)||
     !source.model||!derived.model||!source.claim||!derived.claim)fail('two SceneIR scenes required');
  if(typeof sourceDigest!=='string'||!/^sha256:[0-9a-f]{64}$/.test(sourceDigest))fail('source digest required');
  const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  if(source.schema!=='fab.scene.v0.2'||derived.schema!==source.schema||
     source.representation!==derived.representation||
     !eq(source.claim,derived.claim)||!eq(source.observables||[],derived.observables||[])||
     !eq(source.audit||{},derived.audit||{}))
    fail('source claim, observables or representation mutation');
  const isFork=derived.fork!==undefined;
  if(!isFork){
    if(source.id!==derived.id||!eq(source.model,derived.model))fail('model authority drift');
  } else {
    const fork=derived.fork;
    if(fork.schema!=='fab.visual.template-fork.v1'||fork.sourceDigest!==sourceDigest||
       fork.sourceSceneId!==source.id||fork.sourceModelId!==source.model.id||
       fork.sourceModelRevision!==source.model.revision||
       fork.scope!=='DERIVED_VISUAL_SCENE_NOT_MODEL_AUTHORITY'||
       fork.release!=='HOLD'||fork.publisherSignature!=='NOT_PRESENT'||
       !/^[a-z0-9][a-z0-9-]{0,39}$/.test(fork.visualRevision)||
       derived.id!==source.id+'--fork-'+fork.visualRevision||
       derived.model.revision!==source.model.revision+'+visual-fork.'+fork.visualRevision||
       derived.model.id!==source.model.id||
       derived.model.authority!==source.model.authority)fail('fork provenance or authority drift');
    const origModel={...source.model};const forkModel={...derived.model};
    delete origModel.revision;delete forkModel.revision;
    if(!eq(origModel,forkModel))fail('fork model data mutation');
  }
  const a=new Map(source.parts.map(p=>[p.id,p])),b=new Map(derived.parts.map(p=>[p.id,p]));
  if(a.size!==source.parts.length||b.size!==derived.parts.length||a.size!==b.size)
    fail('missing/duplicate component identities');
  const moved=[],resized=[],relabeled=[];
  for(const p of source.parts){
    const q=b.get(p.id);
    if(!q)fail('new or deleted model component');
    const apart={...p},bpart={...q};
    for(const k of ['x','y','w','h','label']){delete apart[k];delete bpart[k];}
    if(!eq(apart,bpart))fail('unauthorized semantic/status/port mutation');
    for(const k of ['x','y','w','h']){
      if(typeof q[k]!=='number'||!Number.isFinite(q[k]))fail('nonfinite geometry');
    }
    if(q.w<=0||q.h<=0||q.w>100000||q.h>100000||
       Math.abs(q.x)>1000000||Math.abs(q.y)>1000000)fail('geometry outside model bounds');
    if(typeof q.label!=='string'||q.label.length>300)fail('invalid label');
    if(p.x!==q.x||p.y!==q.y)
      moved.push({id:p.id,from:{x:p.x,y:p.y},to:{x:q.x,y:q.y}});
    if(p.w!==q.w||p.h!==q.h)
      resized.push({id:p.id,from:{w:p.w,h:p.h},to:{w:q.w,h:q.h}});
    if(p.label!==q.label)relabeled.push({id:p.id,from:p.label,to:q.label});
  }
  const valid=new Set(['signal','energy','material','control','information','dependency','mechanical']);
  const key=l=>JSON.stringify([l.from,l.to,l.flow,l.fromPort??null,l.toPort??null]);
  const edgeMap=list=>{
    const counts=new Map();
    for(const e of list||[]){
      if(!a.has(e.from)||!a.has(e.to)||!valid.has(e.flow))fail('invalid or dangling graph link');
      for(const [nodeId,portId] of [[e.from,e.fromPort],[e.to,e.toPort]]){
        const ports=a.get(nodeId).ports||[];
        if(portId!=null&&!ports.some(p=>p.id===portId&&p.flow===e.flow))fail('invalid typed link port');
        if(ports.length&&!ports.some(p=>p.flow===e.flow))fail('node has no matching typed flow port');
      }
      const k=key(e);counts.set(k,(counts.get(k)||0)+1);
    }
    return counts;
  };
  const from=edgeMap(source.links),to=edgeMap(derived.links);
  const added=[],removed=[];
  for(const [k,n] of to){
    const delta=n-(from.get(k)||0);
    for(let i=0;i<delta;i++)added.push(JSON.parse(k));
  }
  for(const [k,n] of from){
    const delta=n-(to.get(k)||0);
    for(let i=0;i<delta;i++)removed.push(JSON.parse(k));
  }
  const sort=(l,r)=>JSON.stringify(l).localeCompare(JSON.stringify(r));
  added.sort(sort);removed.sort(sort);
  const changed=(moved.length||resized.length||relabeled.length||added.length||removed.length)>0;
  return {
    schema:'fab.visual.visual-diff.v1',
    sourceSceneId:source.id,derivedSceneId:derived.id,
    sourceDigest,representation:'VISUAL_LAYOUT_COMPARISON_ONLY',
    move:moved,resize:resized,relabel:relabeled,
    addedLinks:added.map(([from,to,flow,fromPort,toPort])=>({from,to,flow,fromPort,toPort})),
    removedLinks:removed.map(([from,to,flow,fromPort,toPort])=>({from,to,flow,fromPort,toPort})),
    changed,sourceAuthorityPreserved:true,originalClaimPreserved:true,
    publisherSignature:'NOT_PRESENT',physicalValidation:'NOT_RUN',
    hostAuthorization:'NOT_RUN',release:'HOLD'
  };
}

export function zipStore(files){
  const fail=s=>{throw Error('PROJECT_ZIP_REJECT: '+s)};
  if(!Array.isArray(files)||files.length<2||files.length>40)fail('between 2 and 40 files required');
  const enc=new TextEncoder(),stamped=[],used=new Set();
  for(const entry of files){
    if(!entry||typeof entry.path!=='string'||entry.path.length>150||
       !/^[a-z0-9][a-z0-9._/-]*$/.test(entry.path)||
       entry.path.startsWith('/')||entry.path.split('/').some(x=>x==='..'||x==='.'||!x)||
       used.has(entry.path))fail('unsafe, duplicate or invalid ZIP path');
    used.add(entry.path);
    if(typeof entry.content!=='string')fail('UTF-8 text-only archive supported');
    const body=enc.encode(entry.content),name=enc.encode(entry.path);
    if(body.length>3000000||name.length>150)fail('individual entry too large');
    stamped.push({name,body});
  }
  const total=stamped.reduce((n,x)=>n+x.body.length,0);
  if(total>12000000)fail('archive exceeds 12MB');
  const crc32=bytes=>{
    let crc=0xFFFFFFFF;
    for(const b of bytes){
      crc^=b;
      for(let j=0;j<8;j++)crc=(crc>>>1)^((crc&1)?0xEDB88320:0);
    }
    return (crc^0xFFFFFFFF)>>>0;
  };
  let len=22,offset=0,centerBytes=0;
  for(const e of stamped){
    e.crc=crc32(e.body);
    e.offset=offset;
    const size=30+e.name.length+e.body.length;
    offset+=size;centerBytes+=46+e.name.length;len+=size+46+e.name.length;
  }
  const buf=new Uint8Array(len),view=new DataView(buf.buffer);
  let pos=0;
  const put16=v=>{view.setUint16(pos,v,true);pos+=2;};
  const put32=v=>{view.setUint32(pos,v,true);pos+=4;};
  const copy=bytes=>{buf.set(bytes,pos);pos+=bytes.length;};
  for(const e of stamped){
    put32(0x04034b50);put16(20);put16(0x0800);put16(0);
    put16(0);put16(0);put32(e.crc);put32(e.body.length);put32(e.body.length);
    put16(e.name.length);put16(0);copy(e.name);copy(e.body);
  }
  const cdStart=pos;
  for(const e of stamped){
    put32(0x02014b50);put16(20);put16(20);put16(0x0800);
    put16(0);put16(0);put16(0);put32(e.crc);put32(e.body.length);
    put32(e.body.length);put16(e.name.length);put16(0);
    put16(0);put16(0);put16(0);put32(0);put32(e.offset);copy(e.name);
  }
  const cdSize=pos-cdStart;
  put32(0x06054b50);put16(0);put16(0);put16(stamped.length);put16(stamped.length);
  put32(cdSize);put32(cdStart);put16(0);
  if(pos!==buf.length)fail('internal ZIP length discrepancy');
  return buf;
}

export function projectFiles(source,current,history,sourceDigest,slug,diffFn,forkFn){
  const fail=s=>{throw Error('PROJECT_BUNDLE_REJECT: '+s)};
  if(typeof diffFn!=='function'||typeof forkFn!=='function')fail('pure contract dependencies required');
  const report=diffFn(source,current,sourceDigest);
  if(!report.sourceAuthorityPreserved||!report.originalClaimPreserved)fail('model changes not allowed');
  const fork=forkFn(current,slug,sourceDigest);
  // If visualEdit metadata exists it is retained, but cannot create authority.
  const roundtrip=diffFn(source,fork,sourceDigest);
  const historySafe=Array.isArray(history)&&history.length<=33&&history.length>=1?history:null;
  if(!historySafe)fail('1-33 local visual snapshots required');
  for(const h of historySafe)diffFn(source,h,sourceDigest);
  const pretty=x=>JSON.stringify(x,null,2)+'\n';
  const manifest={
    schema:'fab.visual.portable-project.v1',
    originalSceneId:source.id,originalModelRevision:source.model.revision,
    forkSceneId:fork.id,derivedRevision:fork.model.revision,
    sourceDigest,slug,historyLength:history.length,
    sourceAuthorityPreserved:true,claimPreserved:true,
    archives:'ZIP_STORE_CRC32_NOT_CRYPTOGRAPHIC_AUTHENTICATION',
    templateSourceSignature:'NOT_PRESENT',hostAuthorization:'NOT_RUN',
    physicalCertification:'NOT_RUN',networkRequired:false,
    release:'HOLD'
  };
  const files=[
    {path:'manifest.json',content:pretty(manifest)},
    {path:'source/original.scene.json',content:pretty(source)},
    {path:'derived/fork.scene.json',content:pretty(fork)},
    {path:'evidence/visual-diff.json',content:pretty(roundtrip)},
    {path:'evidence/edit-history.json',content:pretty({
      schema:'fab.visual.local-edit-history.v1',sourceDigest,
      snapshots:history.map((s,i)=>({ordinal:i,scene:s})),
      publisherSignature:'NOT_PRESENT',release:'HOLD'})},
    {path:'README.txt',content:
      'FAB.VISUAL portable visual project (offline)\n'+
      'Original source remains unchanged. Derived scene is a VISUAL fork.\n'+
      'SHA-256 source digest is content correspondence, NOT publisher authentication.\n'+
      'ZIP uses CRC32 only for transport integrity; no signature, no GPU proof.\n'+
      'No real agent permission, scientific/physical validation or production release.\n'+
      'RELEASE HOLD.\n'}
  ];
  return {files,manifest,report};
}
