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
function help(){console.log(`FAB.VISUAL v0.3.0-alpha.0 · Ω5\nUsage:\n  node bin/fab-visual.mjs demo [out.html]\n  node bin/fab-visual.mjs render <scene.json> <out.svg|out.html>\n  node bin/fab-visual.mjs validate <scene.json>\n  node bin/fab-visual.mjs anatomy-plan <scene.json>\n  node bin/fab-visual.mjs inspect-upstream <path>\n  node bin/fab-visual.mjs anatomy-verify\n  node bin/fab-visual.mjs anatomy-render <scene.json> <out.svg|out.html>\n  node bin/fab-visual.mjs anatomy-timeline [out.html]\n  node bin/fab-visual.mjs gate <manifest.json>`);}
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
  else if(cmd==='gate'){const r=gate(JSON.parse(readFileSync(args[0],'utf8')));console.log(JSON.stringify(r,null,2));if(r.status!=='ELIGIBLE_FOR_AUTHORIZED_RELEASE')process.exitCode=2;}
  else if(cmd==='render'){
    const s=JSON.parse(readFileSync(args[0],'utf8'));assertScene(s);
    const path=args[1];if(!/\.(html|svg)$/i.test(path))throw new Error('output must end .svg or .html');
    const type=path.endsWith('.svg')?'svg':'html'; const output=type==='svg'?renderSvg(s):renderHtml(s);
    write(path,output);const receipt=witness({scene:s,format:type,bytes:output,checks:{'schema':'PASS','upstream':'NOT_RUN','geometry':'NOT_RUN','accessibility':'NOT_RUN'}});
    write(path+'.witness.json',JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({output:resolve(path),witness:resolve(path+'.witness.json'),status:'HOLD'},null,2));
  } else throw new Error(`unknown command: ${cmd}`);
} catch(e){console.error(`fab-visual: ${e.message}`);process.exitCode=1;}
