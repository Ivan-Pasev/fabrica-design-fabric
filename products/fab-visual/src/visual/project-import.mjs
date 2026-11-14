/**
 * Ω11N — defensively open only our exact six-file ZIP STORE project schema.
 * These browser-embeddable functions have no runtime imports or external I/O.
 * No decompression, data descriptors, arbitrary paths, or publisher trust.
 */
export function parseProjectZip(bytes){
  const fail=s=>{throw Error('PROJECT_IMPORT_REJECT: '+s)};
  const raw=bytes instanceof Uint8Array?bytes:bytes instanceof ArrayBuffer?new Uint8Array(bytes):null;
  if(!raw||raw.byteLength<22||raw.byteLength>12000000)fail('ZIP byte bounds');
  const data=new DataView(raw.buffer,raw.byteOffset,raw.byteLength),read16=x=>data.getUint16(x,true),
    read32=x=>data.getUint32(x,true),length=raw.length;
  const must=(p,n)=>Number.isSafeInteger(p)&&p>=0&&Number.isSafeInteger(n)&&n>=0&&p+n<=length;
  const exact=new Set(['manifest.json','source/original.scene.json','derived/fork.scene.json',
    'evidence/visual-diff.json','evidence/edit-history.json','readme.txt']);
  const eocd=length-22;
  if(!must(eocd,22)||read32(eocd)!==0x06054b50||
     read16(eocd+4)!==0||read16(eocd+6)!==0||read16(eocd+8)!==6||
     read16(eocd+10)!==6||read16(eocd+20)!==0)fail('strict six-entry ZIP EOCD expected');
  const centralSize=read32(eocd+12),centralStart=read32(eocd+16);
  if(!must(centralStart,centralSize)||centralStart+centralSize!==eocd)fail('central directory position');
  const decoder=new TextDecoder('utf-8',{fatal:true}),files=new Map();
  const crc32=arr=>{
    let c=0xFFFFFFFF;
    for(const b of arr){
      c^=b;
      for(let n=0;n<8;n++)c=(c>>>1)^((c&1)?0xEDB88320:0);
    }
    return (c^0xFFFFFFFF)>>>0;
  };
  let cp=centralStart,localEnd=0,sum=0;
  for(let i=0;i<6;i++){
    if(!must(cp,46)||read32(cp)!==0x02014b50)fail('missing central file header');
    const made=read16(cp+4),need=read16(cp+6),flags=read16(cp+8),method=read16(cp+10),
      time=read16(cp+12),date=read16(cp+14),crc=read32(cp+16),
      compressed=read32(cp+20),uncompressed=read32(cp+24),nlen=read16(cp+28),
      extra=read16(cp+30),comment=read16(cp+32),disk=read16(cp+34),
      internal=read16(cp+36),external=read32(cp+38),localOffset=read32(cp+42);
    if(made!==20||need!==20||flags!==0x0800||method!==0||time!==0||date!==0||
       compressed!==uncompressed||uncompressed>3000000||nlen===0||nlen>150||
       extra!==0||comment!==0||disk!==0||internal!==0||external!==0)
      fail('unsupported compression, flags, entry metadata, size or ZIP version');
    if(!must(cp+46,nlen))fail('central filename overflow');
    let name;
    try{name=decoder.decode(raw.subarray(cp+46,cp+46+nlen));}catch{fail('invalid UTF-8 filename');}
    if(!exact.has(name)||files.has(name)||name.split('/').some(x=>!x||x==='.'||x==='..'))
      fail('unexpected, duplicate or unsafe member');
    cp+=46+nlen;
    if(localOffset!==localEnd||!must(localOffset,30)||read32(localOffset)!==0x04034b50)
      fail('noncontiguous/invalid local ZIP entry');
    if(read16(localOffset+4)!==need||read16(localOffset+6)!==flags||
       read16(localOffset+8)!==method||read16(localOffset+10)!==time||
       read16(localOffset+12)!==date||read32(localOffset+14)!==crc||
       read32(localOffset+18)!==compressed||read32(localOffset+22)!==uncompressed||
       read16(localOffset+26)!==nlen||read16(localOffset+28)!==0)
      fail('local-vs-central header mismatch');
    const dataStart=localOffset+30+nlen;
    if(dataStart+uncompressed>centralStart||!must(dataStart,uncompressed))
      fail('payload out of bounds');
    const localName=raw.subarray(localOffset+30,dataStart);
    if(!localName.every((b,j)=>b===raw[cp-nlen+j]))fail('local/central filename mismatch');
    const body=raw.subarray(dataStart,dataStart+uncompressed);
    if(crc32(body)!==crc)fail('CRC32 payload mismatch');
    let content;
    try{content=decoder.decode(body)}catch{fail('invalid UTF-8 content');}
    if(content.includes('\0'))fail('binary or NUL in UTF-8-only project');
    files.set(name,content);
    sum+=uncompressed;localEnd=dataStart+uncompressed;
  }
  if(cp!==eocd||localEnd!==centralStart||files.size!==6||sum>12000000)
    fail('noncanonical directory, file count or archive size');
  return files;
}

export async function canonicalProjectDigest(scene){
  const fail=x=>{throw Error('PROJECT_DIGEST_REJECT: '+x)};
  if(!globalThis.crypto?.subtle?.digest)fail('secure SHA-256 implementation unavailable; deny import');
  function canonicalize(v){
    if(Array.isArray(v))return v.map(canonicalize);
    if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonicalize(v[k])]));
    if(typeof v==='number'&&!Number.isFinite(v))fail('nonfinite canonical scene');
    return v;
  }
  const input=new TextEncoder().encode(JSON.stringify(canonicalize(scene)));
  const raw=new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256',input));
  return 'sha256:'+Array.from(raw,x=>x.toString(16).padStart(2,'0')).join('');
}

export async function admitProjectArchive(bytes,expectedSource,expectedDigest,
  visualDiff,forkVisualScene,projectFiles,canonicalProjectDigest,parseProjectZip){
  const fail=s=>{throw Error('PROJECT_ADMISSION_HOLD: '+s)};
  if(typeof visualDiff!=='function'||typeof forkVisualScene!=='function'||
     typeof projectFiles!=='function'||typeof canonicalProjectDigest!=='function'||
     typeof parseProjectZip!=='function')
    fail('required source-checked contracts unavailable');
  if(!expectedSource||typeof expectedDigest!=='string'||!/^sha256:[0-9a-f]{64}$/.test(expectedDigest))
    fail('original trusted Studio anchor required');
  const entries=parseProjectZip(bytes);
  const parse=name=>{let o;try{o=JSON.parse(entries.get(name))}catch{fail('invalid JSON '+name)}
    if(!o||typeof o!=='object'||Array.isArray(o))fail('invalid JSON object '+name);
    return o;};
  const manifest=parse('manifest.json'),source=parse('source/original.scene.json'),
    fork=parse('derived/fork.scene.json'),diff=parse('evidence/visual-diff.json'),
    history=parse('evidence/edit-history.json');
  const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  if(manifest.schema!=='fab.visual.portable-project.v1'||manifest.release!=='HOLD'||
     manifest.archives!=='ZIP_STORE_CRC32_NOT_CRYPTOGRAPHIC_AUTHENTICATION'||
     manifest.templateSourceSignature!=='NOT_PRESENT'||manifest.hostAuthorization!=='NOT_RUN'||
     manifest.physicalCertification!=='NOT_RUN'||manifest.networkRequired!==false||
     manifest.sourceAuthorityPreserved!==true||manifest.claimPreserved!==true)
     fail('manifest scope/authorization promotion');
  if(source.schema!=='fab.scene.v0.2'||manifest.sourceDigest!==expectedDigest||
     history.sourceDigest!==expectedDigest||fork.fork?.sourceDigest!==expectedDigest||
     diff.sourceDigest!==expectedDigest)fail('original source hash mismatch');
  if(!eq(source,expectedSource))fail('ZIP source differs from embedded trusted Studio scene');
  if(await canonicalProjectDigest(source)!==expectedDigest||
     await canonicalProjectDigest(expectedSource)!==expectedDigest)
    fail('cryptographic canonical SceneIR SHA-256 mismatch');
  if(history.schema!=='fab.visual.local-edit-history.v1'||
     history.publisherSignature!=='NOT_PRESENT'||history.release!=='HOLD'||
     !Array.isArray(history.snapshots)||history.snapshots.length<1||history.snapshots.length>33||
     history.snapshots.length!==manifest.historyLength)
    fail('revision history bounds/status');
  const snapshots=[];
  for(const [i,h] of history.snapshots.entries()){
    if(!h||h.ordinal!==i||!h.scene||typeof h.scene!=='object')fail('noncontiguous revision ordinal');
    visualDiff(source,h.scene,expectedDigest);
    snapshots.push(h.scene);
  }
  if(!eq(snapshots[0],source))fail('timeline must begin with immutable original');
  if(fork.fork?.schema!=='fab.visual.template-fork.v1'||
     fork.fork.release!=='HOLD'||fork.fork.publisherSignature!=='NOT_PRESENT'||
     typeof manifest.slug!=='string'||fork.fork.visualRevision!==manifest.slug||
     manifest.originalSceneId!==source.id||
     manifest.originalModelRevision!==source.model.revision||
     manifest.forkSceneId!==fork.id||manifest.derivedRevision!==fork.model.revision)
    fail('fork ancestry or revision misbinding');
  const current=JSON.parse(JSON.stringify(fork));
  delete current.fork;
  current.id=source.id;current.model.revision=source.model.revision;
  const currentValid=visualDiff(source,current,expectedDigest);
  const match=snapshots.findIndex(s=>eq(s,current));
  if(match<0)fail('fork state missing from stated revision history');
  const generated=projectFiles(source,current,snapshots,expectedDigest,
    manifest.slug,visualDiff,forkVisualScene);
  if(generated.files.length!==entries.size)fail('ZIP file count mismatch');
  for(const file of generated.files)
    if(entries.get(file.path)!==file.content)fail('unmatched canonical project entry '+file.path);
  if(!eq(generated.manifest,manifest)||!eq(generated.report,currentValid))
    fail('manifest or visual-diff regeneration mismatch');
  return {
    schema:'fab.visual.local-project-admission.v1',
    sourceDigest:expectedDigest,slug:manifest.slug,
    originalSceneId:source.id,derivedSceneId:fork.id,
    history:snapshots,currentOrdinal:match,current,manifest,report:currentValid,
    evidence:'CRYPTO_SHA256_AND_EXACT_SCHEMA_REGENERATION',
    publisherSignature:'NOT_PRESENT',hostAuthorization:'NOT_RUN',
    realPhysics:'NOT_RUN',release:'HOLD'
  };
}
