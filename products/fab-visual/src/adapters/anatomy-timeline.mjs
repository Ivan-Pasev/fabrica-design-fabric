/** FAB.VISUAL Ω5: interactive isometric timeline with identical model and visual states. */
import {renderAnatomySvg, anatomySceneModel} from './anatomy-kernel.mjs';
import {assertScene} from '../visual/contract.mjs';
import {verifyPolicyTimeline} from './policy-proof.mjs';
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function jsonInScript(value) {
  return JSON.stringify(value).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
}
export function renderAnatomyTimeline(scenes,{title='FAB.VISUAL · Anatomy policy mechanism'}={}) {
  if(!Array.isArray(scenes)||scenes.length<2||scenes.length>64)throw Error('2..64 scene snapshots required');
  scenes.forEach(assertScene);
  const first=scenes[0];
  if(scenes.some(s=>s.id!==first.id||s.model.id!==first.model.id||s.model.revision!==first.model.revision))throw Error('unrelated authoritative timeline models');
  if(first.model.id==='fab.policy.reference') {
    const proof=verifyPolicyTimeline(scenes);
    if(proof.status!=='PASS')throw Error('Policy model event-trace proof failed: '+JSON.stringify(proof));
  }
  const ids=first.parts.map(p=>p.id).sort().join('\0');
  if(scenes.some(s=>s.parts.map(p=>p.id).sort().join('\0')!==ids))throw Error('stable semantic part IDs required');
  const frames=scenes.map((s,i)=>{
    const r=anatomySceneModel(s);
    if(r.audit.status!=='PASS')throw Error('unverified geometry at snapshot '+i);
    return {svg:renderAnatomySvg(s),observables:s.observables,claim:s.claim,sceneId:s.id,index:i};
  });
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><style>body{font:16px/1.5 system-ui,sans-serif;background:#f6f8fb;color:#1d304b;margin:0}main{max-width:1260px;margin:auto;padding:24px}#stage{border:1px solid #b4c5d8;border-radius:16px;overflow:hidden;background:#fff}svg{display:block;width:100%;height:auto}.ctrl{display:flex;gap:12px;margin:18px 0;align-items:center}button{padding:8px 15px;border:1px solid #8399b2;border-radius:8px;background:white}button:disabled{opacity:.45}button:focus-visible,input:focus-visible{outline:3px solid #2856b8;outline-offset:2px}input[type=range]{flex:1;min-width:140px}.state{font-weight:650;margin:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:260px;overflow:auto}footer{margin-top:24px;color:#516480;font-size:.85rem}</style></head><body><main><h1>${esc(title)}</h1><p>Model-governed synthetic policy states. This is an analogy; no real CodexStation authorization is performed. Geometry is rendered with pinned Anatomy MIT source modules.</p><div id="stage" aria-live="polite"></div><div class="ctrl"><button id="prev" type="button">Previous</button><input id="seek" type="range" min="0" max="${frames.length-1}" value="0" aria-label="Synthetic model state"><button id="next" type="button">Next</button></div><p id="phase" class="state" role="status"></p><details><summary>Model observables and scientific-claim boundary</summary><pre id="evidence"></pre></details><footer>FAB.VISUAL Ω5 · Anatomy exact pinned geometry and sampled depth audit · Independent AABB checks · Release HOLD</footer></main><script type="application/json" id="frames">${jsonInScript(frames)}</script><script>(()=>{const frames=JSON.parse(document.getElementById('frames').textContent);const slider=document.getElementById('seek');const stage=document.getElementById('stage');const p=document.getElementById('phase');const e=document.getElementById('evidence');const prev=document.getElementById('prev');const next=document.getElementById('next');let n=0;function paint(index){n=Math.max(0,Math.min(frames.length-1,index));const f=frames[n];slider.value=n;stage.innerHTML=f.svg;const map=Object.fromEntries(f.observables.map(x=>[x.id,x.value]));p.textContent='Frame '+(n+1)+' of '+frames.length+' · phase='+map.phase+' · authorized='+map.authorized+' · released='+map.released;e.textContent=JSON.stringify({sceneId:f.sceneId,modelObservables:f.observables,claim:f.claim},null,2);prev.disabled=n===0;next.disabled=n===frames.length-1;}prev.addEventListener('click',()=>paint(n-1));next.addEventListener('click',()=>paint(n+1));slider.addEventListener('input',()=>paint(Number(slider.value)));paint(0);})();</script></body></html>`;
}
