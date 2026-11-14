#!/usr/bin/env node
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { policyScene } from '../src/visual/fixture.mjs';
import { assertScene } from '../src/visual/contract.mjs';
import { renderSvg, renderHtml } from '../src/visual/svg.mjs';
import { witness } from '../src/visual/provenance.mjs';
import { anatomyPlan, inspectAnatomy } from '../src/adapters/anatomy.mjs';
import {renderAnatomySvg,renderAnatomyHtml,anatomySceneModel,verifyAnatomyBlobs} from '../src/adapters/anatomy-kernel.mjs';
import {renderAnatomyTimeline} from '../src/adapters/anatomy-timeline.mjs';
import { gate } from '../src/gate.mjs';
import { renderStudio } from '../src/visual/studio.mjs';
import {buildGalleryBundle} from '../src/visual/gallery.mjs';
import {forkVisualScene,visualDiff,zipStore,projectFiles} from '../src/visual/project.mjs';
import {sha256,canonicalJSON} from '../src/visual/provenance.mjs';
import { exportInterchange, FORMATS } from '../src/adapters/interchange.mjs';
import { importInterchange } from '../src/adapters/graph-import.mjs';
function help(){console.log(`FAB.VISUAL v0.6.0-alpha.0 · Ω11L\nUsage:\n  node bin/fab-visual.mjs demo [out.html]\n  node bin/fab-visual.mjs render <scene.json> <out.svg|out.html>\n  node bin/fab-visual.mjs validate <scene.json>\n  node bin/fab-visual.mjs anatomy-plan <scene.json>\n  node bin/fab-visual.mjs inspect-upstream <path>\n  node bin/fab-visual.mjs anatomy-verify\n  node bin/fab-visual.mjs anatomy-render <scene.json> <out.svg|out.html>\n  node bin/fab-visual.mjs anatomy-timeline [out.html]\n  node bin/fab-visual.mjs studio <scene.json> <out.html>\n  node bin/fab-visual.mjs gallery [output-directory]\n  node bin/fab-visual.mjs project <source.scene.json> <edited.scene.json> <fork-slug> <out.zip>\n  node bin/fab-visual.mjs interchange <scene.json> <reactflow|cytoscape|mermaid|dot> <out>\n  node bin/fab-visual.mjs interchange-import <reactflow|cytoscape> <graph.json> <source-scene.json> <out.json>\n  node bin/fab-visual.mjs gate <manifest.json>`);}
function write(path,content){const p=resolve(path);mkdirSync(dirname(p),{recursive:true});writeFileSync(p,content);return p;}
const [cmd,...args]=process.argv.slice(2);
try {
  if (!cmd||cmd==='help'||cmd==='--help')help();
  else if(cmd==='demo'){const scene=policyScene(['START','POLICY_ESCALATE']);const p=args[0]||'dist/policy-machine.html';write(p,renderHtml(scene));console.log(JSON.stringify({output:resolve(p),claim:'EXPLANATORY',status:'GENERATED_NOT_RELEASED'}));}
  else if(cmd==='validate'){const s=JSON.parse(readFileSync(args[0],'utf8'));assertScene(s);console.log('SceneIR VALID');}
  else if(cmd==='anatomy-plan'){const s=JSON.parse(readFileSync(args[0],'utf8'));console.log(JSON.stringify(anatomyPlan(s),null,2));}
  else if(cmd==='anatomy-verify'){const r=verifyAnatomyBlobs();console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=2;}
  else if(cmd==='anatomy-render'){const s=JSON.parse(readFileSync(args[0],'utf8')); const out=args[1];if(!out||!/(\.html|\.svg)$/i.test(out))throw Error('output must end .html or .svg');const svg=out.toLowerCase().endsWith('.svg');const content=svg?renderAnatomySvg(s):renderAnatomyHtml(s);const assessment=anatomySceneModel(s).audit;const receipt=witness({scene:s,format:svg?'svg':'html',bytes:content,renderer:'anatomy-exact-pinned-subset',checks:{'source':'PASS','model':assessment.model_evidence.status,'connections':assessment.connections.status,'independent_aabb':assessment.independent_analytic_aabb.ok?'PASS':'FAIL','sampled_depth':assessment.status,'upstream_full_suite':'NOT_RUN','visual_accessibility':'NOT_RUN'}});write(out,content);write(out+'.witness.json',JSON.stringify({...receipt,substantiveAudit:assessment},null,2)+'\n');console.log(JSON.stringify({output:resolve(out),audit:assessment,release:'HOLD'},null,2));}
  else if(cmd==='anatomy-timeline'){const events=['START','POLICY_ESCALATE','HUMAN_APPROVE','RELEASE'];const snaps=[policyScene([])];for(let i=1;i<=events.length;i++)snaps.push(policyScene(events.slice(0,i)));const out=args[0]||'dist/anatomy-timeline.html';const content=renderAnatomyTimeline(snaps);write(out,content);console.log(JSON.stringify({output:resolve(out),frames:snaps.length,source:'PINNED_ANATOMY',release:'HOLD'}));}
  else if(cmd==='inspect-upstream'){const r=inspectAnatomy(args[0]);console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=2;}
  else if(cmd==='project'){
    const [sourcePath,editedPath,slug,out]=args;
    if(!sourcePath||!editedPath||!slug||!out||!/\.zip$/i.test(out))
      throw Error('usage: project <source.scene.json> <edited.scene.json> <fork-slug> <out.zip>');
    const src=resolve(sourcePath),derived=resolve(editedPath),destination=resolve(out);
    if(src===destination||derived===destination)
      throw Error('project ZIP output cannot overwrite source inputs');
    for(const protectedRoot of ['src','templates','vendor','fixtures','bin','tests'].map(x=>resolve(x)))
      if(destination===protectedRoot||destination.startsWith(protectedRoot+'/'))
        throw Error('project archive cannot be written into source directories');
    const source=assertScene(JSON.parse(readFileSync(src,'utf8')));
    const current=assertScene(JSON.parse(readFileSync(derived,'utf8')));
    const digest='sha256:'+sha256(canonicalJSON(source));
    const built=projectFiles(source,current,[source,current],digest,slug,visualDiff,forkVisualScene);
    const zip=zipStore(built.files);
    write(destination,zip);
    const receipt={schema:'fab.visual.portable-project-receipt.v1',
      sourceDigest:digest,archiveSha256:'sha256:'+sha256(zip),
      size:zip.length,entries:built.files.map(x=>x.path),
      forkSceneId:built.manifest.forkSceneId,externalCodeImported:false,
      signedByAuthority:false,release:'HOLD'};
    write(destination+'.witness.json',JSON.stringify(receipt,null,2)+'\n');
    console.log(JSON.stringify({archive:destination,receipt:destination+'.witness.json',
      files:receipt.entries.length,bytes:zip.length,release:'HOLD'},null,2));
  }
  else if(cmd==='gallery'){
    const target=resolve(args[0]||'dist/gallery');
    const protectedRoots=['src','templates','vendor','fixtures','bin','tests','extensions']
      .map(name=>resolve(name));
    if(protectedRoots.some(root=>target===root||target.startsWith(root+'/')))
      throw Error('gallery output cannot write inside source code or original templates');
    const {assets,manifest}=buildGalleryBundle();
    for(const file of assets){
      if(!/^(?:studios\/[a-z][a-z0-9-]*\.html|scenes\/[a-z][a-z0-9-]*\.scene\.json|previews\/[a-z][a-z0-9-]*\.svg|index\.html|gallery\.manifest\.json)$/.test(file.path))
        throw Error('unexpected gallery artifact name');
      write(resolve(target,file.path),file.content);
    }
    console.log(JSON.stringify({gallery:resolve(target,'index.html'),
      files:assets.length,templates:manifest.templates.map(x=>x.id),
      release:'HOLD',externalRuntime:false},null,2));
  }
  else if(cmd==='studio'){
    const input=args[0],out=args[1];
    if(!input||!out||!/\.html$/i.test(out))throw Error('usage: studio <scene.json> <output.html>');
    if(resolve(input)===resolve(out))throw Error('source cannot overwrite itself');
    const scene=JSON.parse(readFileSync(input,'utf8'));
    const result=renderStudio(scene);
    write(out,result.html);
    write(out+'.witness.json',JSON.stringify(result.metadata,null,2)+'\n');
    console.log(JSON.stringify({output:resolve(out),witness:resolve(out+'.witness.json'),
      views:result.metadata.views,formats:result.metadata.interchangeFormats,
      isometric:result.metadata.isoStatus,release:'HOLD'},null,2));
  }
  else if(cmd==='interchange'){
    const input=args[0],format=args[1],out=args[2];
    if(!input||!FORMATS.includes(format)||!out)
      throw Error('usage: interchange <scene.json> <reactflow|cytoscape|mermaid|dot> <output>');
    if(resolve(input)===resolve(out))throw Error('source cannot overwrite itself');
    const scene=JSON.parse(readFileSync(input,'utf8'));
    const result=exportInterchange(scene,format);
    if(!out.toLowerCase().endsWith('.'+result.extension))throw Error('expected .'+result.extension+' interchange output');
    write(out,result.text);
    write(out+'.witness.json',JSON.stringify(result.receipt,null,2)+'\n');
    console.log(JSON.stringify({output:resolve(out),witness:resolve(out+'.witness.json'),
      format,release:'HOLD'},null,2));
  }
  else if(cmd==='interchange-import'){
    const [format,graphFile,sourceFile,out]=args;
    if(!['reactflow','cytoscape'].includes(format)||!graphFile||!sourceFile||!out||!/\.json$/i.test(out))
      throw Error('usage: interchange-import <reactflow|cytoscape> <graph.json> <source-scene.json> <out.json>');
    if(resolve(out)===resolve(graphFile)||resolve(out)===resolve(sourceFile))
      throw Error('import output cannot overwrite graph or original source');
    const seed=JSON.parse(readFileSync(sourceFile,'utf8'));
    const graph=readFileSync(graphFile,'utf8');
    if(Buffer.byteLength(graph)>2000000)throw Error('graph input exceeds 2MB');
    const received=importInterchange(graph,format,seed);
    write(out,JSON.stringify(received.scene,null,2)+'\n');
    write(out+'.import-report.json',JSON.stringify(received.report,null,2)+'\n');
    write(out+'.witness.json',JSON.stringify(received.receipt,null,2)+'\n');
    console.log(JSON.stringify({output:resolve(out),report:resolve(out+'.import-report.json'),
      changedParts:received.report.changed_parts,release:'HOLD'},null,2));
  }
  else if(cmd==='gate'){const r=gate(JSON.parse(readFileSync(args[0],'utf8')));console.log(JSON.stringify(r,null,2));if(r.status!=='ELIGIBLE_FOR_AUTHORIZED_RELEASE')process.exitCode=2;}
  else if(cmd==='render'){
    const s=JSON.parse(readFileSync(args[0],'utf8'));assertScene(s);
    const path=args[1];if(!/\.(html|svg)$/i.test(path))throw new Error('output must end .svg or .html');
    const type=path.endsWith('.svg')?'svg':'html'; const output=type==='svg'?renderSvg(s):renderHtml(s);
    write(path,output);const receipt=witness({scene:s,format:type,bytes:output,checks:{'schema':'PASS','upstream':'NOT_RUN','geometry':'NOT_RUN','accessibility':'NOT_RUN'}});
    write(path+'.witness.json',JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({output:resolve(path),witness:resolve(path+'.witness.json'),status:'HOLD'},null,2));
  } else throw new Error(`unknown command: ${cmd}`);
} catch(e){console.error(`fab-visual: ${e.message}`);process.exitCode=1;}
