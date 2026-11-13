/**
 * FAB.VISUAL Ω5 — constrained Anatomy renderer bridge.
 * This module directly executes a narrow, exact-sha vendored subset of Anatomy (MIT).
 * It supports ANALOGICAL diagrams only: its units are visual layout units, NOT metrology.
 */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as K from '../../vendor/anatomy/kit/iso-kit.mjs';
import * as A from '../../vendor/anatomy/kit/audit.mjs';
import { assertScene } from '../visual/contract.mjs';
import { checkSceneAabbIndependently } from './independent-occlusion.mjs';
import { verifySyntheticPolicySnapshot } from './policy-proof.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'vendor', 'anatomy');
const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const KIND = 'ANATOMY_PINNED_ISOMETRIC_REFERENCE';

/** Compare Git blob hashes, not raw SHA1 hashes: Git hashes include the blob header. */
export function verifyAnatomyBlobs(root = ROOT) {
  const manifest = JSON.parse(readFileSync(join(root, 'SOURCE_LOCK.json'), 'utf8'));
  const results = Object.entries(manifest.blobs).map(([file, expected]) => {
    let actual = null, error = null;
    try {
      const bytes = readFileSync(join(root, file));
      actual = createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
    } catch (cause) { error = cause.code || String(cause); }
    return {file, expected, actual, ok: actual === expected, error};
  });
  return {ok:results.every(x => x.ok), pin:manifest.commit, license:manifest.license, scope:manifest.scope, results};
}

function shapeOf(part, height = 28) {
  const plan = {x:part.x,y:part.y,w:part.w,d:part.h,r:Math.min(12, part.w/7, part.h/7)};
  const min = [part.x, part.y, 0];
  const max = [part.x+part.w, part.y+part.h, height];
  const mid = [(min[0]+max[0])/2,(min[1]+max[1])/2, height/2];
  return {min, max, mid, plan, height};
}
function makeProjection(scene,{width,height,height3d,azimuth=45,elevation=30}) {
  const raw = {origin:[0,0],scale:1,azimuth,elevation};
  const coords=[];
  for(const part of scene.parts) {
    const s=shapeOf(part,height3d);
    for(const x of [s.min[0],s.max[0]]) for(const y of [s.min[1],s.max[1]]) for(const z of [0,s.height]) coords.push(K.iso([x,y,z],raw));
  }
  const x0=Math.min(...coords.map(p=>p[0])), x1=Math.max(...coords.map(p=>p[0]));
  const y0=Math.min(...coords.map(p=>p[1])), y1=Math.max(...coords.map(p=>p[1]));
  const margin=95;
  const scale=Math.min((width-margin*2)/Math.max(1,x1-x0),(height-margin*2)/Math.max(1,y1-y0),3);
  return {origin:[margin-x0*scale,margin-y0*scale],scale,azimuth,elevation};
}
function boundsResult(scene,projection,width,height,height3d) {
  const check=[];
  for(const part of scene.parts){
    const s=shapeOf(part,height3d);
    for(const x of [s.min[0],s.max[0]])for(const y of [s.min[1],s.max[1]])for(const z of [0,s.height]){
      const [u,v]=K.iso([x,y,z],projection);
      if(u < 0 || u > width || v<0 || v>height)check.push({part:part.id,u,v});
    }
  }
  return {ok:check.length===0, violations:check};
}
export function anatomySceneModel(scene, options={}) {
  assertScene(scene);
  if(scene.representation!=='ANALOGICAL')throw new Error('Anatomy Ω5 bridge supports ANALOGICAL scenes only; no metrology or formal proof renderer');
  const {width=1200,height=740,height3d=28,auditStep=2.5,azimuth=45,elevation=30}=options;
  if(![width,height].every(x=>Number.isInteger(x)&&x>=400&&x<=4096))throw new Error('invalid viewport dimensions');
  if(!Number.isFinite(height3d)||height3d<=0||height3d>100)throw new Error('invalid visual-only extrusion height');
  if(!Number.isFinite(auditStep)||auditStep<=0||auditStep>10)throw new Error('invalid audit step');
  if(!Number.isFinite(azimuth)||!Number.isFinite(elevation)||elevation<1||elevation>89)throw new Error('invalid isometric camera');
  const pin=verifyAnatomyBlobs();
  if(!pin.ok)throw new Error('Anatomy source SHA integrity gate failed');
  // A model-specific replay oracle is mandatory when this known model is claimed.
  // For unknown models the evidence stays NOT_RUN; never self-compare the input readout.
  const modelEvidence=scene.model.id==='fab.policy.reference'
    ? verifySyntheticPolicySnapshot(scene)
    : {status:'NOT_RUN',message:'No authoritative model evaluator registered'};
  if(scene.model.id==='fab.policy.reference' && modelEvidence.status!=='PASS')
    throw new Error('model replay/observable parity failed: '+JSON.stringify(modelEvidence));
  const P=makeProjection(scene,{width,height,height3d,azimuth,elevation});
  const mapped=scene.parts.map(part=>({part,...shapeOf(part,height3d)}));
  const boxed=mapped.map(m=>({name:m.part.id, shape:A.box(m.min,m.max,{name:m.part.id}),mid:m.mid}));
  const R=A.recorder(P);
  for(const m of boxed){R.solid(m.shape);R.put({name:m.name,piece:m.name,at:m.mid,shapes:[m.shape]});}
  const order=A.settle(R,P,{states:[0],step:auditStep,least:0.25,tolerance:0.3});
  const depth=A.depthOrder(order.items,P,{overlaps:order.overlaps,solved:order.solved});
  // Contract: actual painter sequence MUST use the settled keys that the audit checked.
  if(order.items.some((item,i)=>!Number.isFinite(item.key)||item.key!==order.solved.keys[i]))
    throw new Error('auditor emitted inconsistent painter keys');
  const paintOrder=order.items.map((item,index)=>({name:item.name,key:item.key,index}))
    .sort((a,b)=>a.key-b.key||a.index-b.index).map(x=>x.name);
  if(paintOrder.length!==scene.parts.length || new Set(paintOrder).size!==scene.parts.length)
    throw new Error('painter identity mismatch');
  const screen=boundsResult(scene,P,width,height,height3d);
  const independent=checkSceneAabbIndependently(scene,{height:height3d});
  const status = !independent.ok || !screen.ok || depth.problems.length || depth.missing.length || order.solved.dropped.length || order.solved.cycles.length ? 'FAIL' : 'PASS';
  const audit={
    status, sampling:'SAMPLED_NOT_FORMAL', step:auditStep,
    scope:'PINNED_SOLIDS_ONLY', paint_order:paintOrder,
    model_evidence:modelEvidence,
    connections:{status:(scene.links||[]).length?'NOT_RUN':'PASS',scope:'DECORATIVE_LINK_PATHS_NOT_PART_OF_ANATOMY_DEPTH_AUDIT'},
    full_scene_assurance:(scene.links||[]).length || modelEvidence.status!=='PASS'?'INCONCLUSIVE':'SAMPLED_BOUNDED',
    release:'HOLD',
    projected_bounds:screen,
    independent_analytic_aabb:independent,
    upstream_audit_engine:'kit/audit.mjs (PINNED)',
    evaluated_pairs:order.overlaps.pairs.length,
    discarded_constraints:order.solved.dropped.length,
    cycles:order.solved.cycles.length,
    depth_problems:depth.problems.length,
    missing_shapes:depth.missing.length,
    notes:['Boxes-only; no routed cable/tube geometry checked in the scene','No full A.auditOrExit run for this analogical demo','A PASS indicates only these bounded sampled checks, not proof or scientific validation']
  };
  return {scene,projection:P,width,height,mapped,paintOrder,boxShapes:boxed.map(x=>x.shape),audit,source:pin};
}
export function renderAnatomySvg(scene,options={}) {
  const m=anatomySceneModel(scene,options);
  if(m.audit.status!=='PASS')throw new Error('Anatomy sampled geometry gate failed: '+JSON.stringify(m.audit));
  const {projection:P,width,height,mapped}=m;
  const byId=new Map(mapped.map(q=>[q.part.id,q]));
  const ordered=m.paintOrder.map(id=>byId.get(id));
  if(ordered.some(x=>!x))throw new Error('settled painter order includes an unknown part');
  const get=(id)=>mapped.find(q=>q.part.id===id);
  const links=(scene.links||[]).map((link,i)=>{
    const a=get(link.from),b=get(link.to);
    const p0=K.iso(a.mid,P),p1=K.iso(b.mid,P);
    return `<path class="wire" data-link="${i}" data-flow="${escape(link.flow)}" d="${K.pathOf([p0,p1])}"/><title>${escape(link.from)} to ${escape(link.to)}</title>`;
  }).join('');
  const groups=ordered.map((m,paintIndex)=>{
    const s=K.slabOf(m.plan,0,m.height,P,8,0);
    const id=escape(m.part.id),label=escape(m.part.label);
    const status=escape(m.part.status||'NEUTRAL');
    const top=K.iso([m.mid[0],m.mid[1],m.height],P);
    return `<g class="part" data-part="${id}" data-paint-index="${paintIndex}" data-status="${status}" role="group" aria-label="${label}"><title>${label}</title><path class="body" d="${s.fill}"/><path class="shade shade-0" d="${s.shades[0]}"/><path class="shade shade-1" d="${s.shades[1]}"/><path class="shade shade-2" d="${s.shades[2]}"/><path class="shade shade-3" d="${s.shades[3]}"/><path class="top" d="${s.top}"/><path class="outline" d="${s.outline}"/><text class="caption" x="${top[0].toFixed(2)}" y="${(top[1]-9).toFixed(2)}" text-anchor="middle">${label}</text></g>`;
  }).join('');
  const status=escape(scene.claim.status),kind=escape(scene.representation),title=escape(scene.id);
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" role="img" aria-labelledby="fab-ttl fab-desc"><title id="fab-ttl">${title}</title><desc id="fab-desc">An isometric analogical view of ${title}. ${escape(scene.claim.interpretation)}. Not a physical construction or certified machine.</desc><style>.bg{fill:#f5f7fc}.wire{fill:none;stroke:#8195b3;stroke-width:3;stroke-dasharray:8 6}.part .body{fill:#d4dfed;stroke:none}.shade-0{fill:#768aaa}.shade-1{fill:#93a8c1}.shade-2{fill:#b5c7da}.shade-3{fill:#c6d8e9}.part .top{fill:#f5f9ff;stroke:#73839c;stroke-width:1.6}.outline{fill:none;stroke:#5e728d;stroke-width:2}.caption{font:600 16px system-ui,sans-serif;fill:#20364c}.part[data-status=BLOCKED] .top,.part[data-status=DENIED] .top{fill:#ffe1df}.part[data-status=ALLOWED] .top{fill:#d6f7df}.legend{font:600 14px system-ui,sans-serif;fill:#51637d}</style><rect class="bg" width="${width}" height="${height}"/><g class="connections">${links}</g><g class="assemblies">${groups}</g><text class="legend" x="22" y="${height-28}">FAB.VISUAL Ω5 · Pinned Anatomy geometry · ANALOGICAL · Claim: ${status} · LINKS NOT DEPTH-AUDITED · No scientific validation</text></svg>`;
}
export function renderAnatomyHtml(scene,options={}) {
  const svg=renderAnatomySvg(scene,options);
  const observables=scene.observables||[];
  // renderAnatomySvg already applies the model-specific replay gate; do not
  // self-compare user-supplied observables and label that proof.
  const assessment=anatomySceneModel(scene).audit;
  if(scene.model.id==='fab.policy.reference' && assessment.model_evidence.status!=='PASS')
    throw new Error('model replay parity not established');
  const data=escape(JSON.stringify({model:scene.model,observables,claim:scene.claim}));
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(scene.id)} · Anatomy</title><style>body{font:16px/1.5 system-ui,sans-serif;background:#f4f6fa;color:#21354b;margin:0}main{max-width:1250px;margin:auto;padding:24px}svg{display:block;max-width:100%;height:auto;border:1px solid #bdccdd;border-radius:15px}pre{white-space:pre-wrap;overflow-wrap:anywhere}p{max-width:70ch}</style></head><body><main><h1>${escape(scene.id)}</h1><p>Model-governed synthetic analogy. No real authorization; this view is not an engineering drawing or scientific proof.</p>${svg}<p>${escape(scene.claim.interpretation)}</p><details><summary>Evidence and model observables</summary><pre>${data}</pre></details><footer>FAB.VISUAL Ω5 · Exact Anatomy MIT geometry and audit subset · Sampled geometry only · HOLD</footer></main></body></html>`;
}
