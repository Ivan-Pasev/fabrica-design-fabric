/**
 * FAB.VISUAL Ω9 — accessible, model-backed semantic inspection of illustrative SVG.
 * This is a presentation aid, not a geometry audit, screen-reader certification,
 * a source of new observables, or an execution authority.
 */
export function inspectorParts(scene) {
  return scene.parts.map(({id,label,status,parent})=>({
    id,label,status:status||'NEUTRAL',parent:parent||null
  }));
}

export const inspectorCss = `
.visual-tools{border:1px solid #aabed3;background:#fff;border-radius:12px;padding:clamp(12px,3vw,18px);margin:16px 0}
.visual-tools h2{font-size:1.14rem;margin:0 0 4px}.visual-tools p{margin:3px 0 10px}
.zoom-bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:8px 0 12px}
.zoom-bar button,.part-list button{min-height:44px;padding:10px 15px;font:inherit;border:1px solid #56708f;border-radius:9px;background:#fff;color:#193653;cursor:pointer}
.zoom-bar button:focus-visible,.part-list button:focus-visible,.visual-scroll:focus-visible{outline:3px solid #2856b8;outline-offset:2px}
.zoom-bar button:disabled{opacity:.4;cursor:not-allowed}
.zoom-readout{font-size:1rem;font-weight:700;min-width:4rem}
.part-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,180px),1fr));gap:8px;padding:0;list-style:none;margin:10px 0}
.part-list li{min-width:0}.part-list button{width:100%;text-align:left;overflow-wrap:anywhere}
.part-list button[aria-pressed=true]{background:#e5f0ff;border:2px solid #245aa9}
.part-status{font-size:1rem;line-height:1.5;padding:12px;background:#f1f5fa;border-radius:9px;overflow-wrap:anywhere}
.visual-scroll{overflow:auto;scrollbar-gutter:stable;overscroll-behavior:contain;max-height:75vh}
.visual-scroll svg{max-width:none!important;display:block}
.visual-scroll svg .part[data-selected=true] .outline{stroke:#a14500;stroke-width:5px}
@media(max-width:600px){main{padding:12px!important}.ctrl{flex-wrap:wrap}.ctrl input{min-width:100px}.visual-scroll{max-height:60vh}}
@media(prefers-reduced-motion:reduce){.visual-scroll,.visual-scroll *{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
`;

export const inspectorMarkup = `<section class="visual-tools" aria-labelledby="visual-inspector-heading">
<h2 id="visual-inspector-heading">Inspect visual components</h2>
<p id="zoom-hint">Enlarge the diagram, then scroll its image or choose a labeled component. This is an illustrative view; readouts follow the source model.</p>
<div class="zoom-bar" role="group" aria-label="Diagram magnification">
<button type="button" id="zoom-out" aria-label="Zoom out diagram">−</button>
<output id="zoom-level" class="zoom-readout" aria-live="polite">100%</output>
<button type="button" id="zoom-in" aria-label="Zoom in diagram">+</button>
<button type="button" id="zoom-reset">Reset zoom</button>
</div>
<p><strong>Components in the current model state</strong></p>
<ul id="part-list" class="part-list" aria-label="Diagram components"></ul>
<p id="part-info" class="part-status" role="status" aria-live="polite">Select a component to read its current label and status.</p>
</section>`;

export const inspectorRuntime = String.raw`(() => {
  'use strict';
  const presets=[1,1.5,2,3];
  window.FabVisualInspector=function attach(stage){
    if(!stage || !stage.classList.contains('visual-scroll'))throw Error('Missing semantic scroll stage');
    const level=document.getElementById('zoom-level');
    const zoomOut=document.getElementById('zoom-out');
    const zoomIn=document.getElementById('zoom-in');
    const zoomReset=document.getElementById('zoom-reset');
    const list=document.getElementById('part-list');
    const info=document.getElementById('part-info');
    if(!level||!zoomOut||!zoomIn||!zoomReset||!list||!info)throw Error('Incomplete inspector controls');
    let zoomIndex=0, current=[], selected=null;
    const currentSvg=()=>stage.querySelector('svg');
    function showZoom(){
      const zoom=presets[zoomIndex],svg=currentSvg();
      if(svg)svg.style.width=(zoom*100)+'%';
      level.textContent=Math.round(zoom*100)+'%';
      zoomOut.disabled=zoomIndex===0;
      zoomIn.disabled=zoomIndex===presets.length-1;
    }
    function focusPart(id){
      const part=current.find(x=>x.id===id);
      if(!part)return;
      selected=id;
      const svg=currentSvg();
      for(const button of list.querySelectorAll('button[data-part-id]'))button.setAttribute('aria-pressed',String(button.dataset.partId===id));
      for(const graphic of svg?.querySelectorAll('.part[data-part]')||[])graphic.dataset.selected=String(graphic.dataset.part===id);
      info.textContent=part.label+' · status='+part.status+(part.parent?' · parent='+part.parent:'')+' · model-based illustration; not independent verification';
      const shape=[...(svg?.querySelectorAll('.part[data-part]')||[])].find(x=>x.dataset.part===id);
      // Scroll within the diagram container, not the full document. Bounding geometry
      // is used for navigation only; it is not accepted as a physical measurement.
      if(shape&&svg&&typeof shape.getBBox==='function'){
        const bounds=shape.getBBox(), view=svg.viewBox.baseVal;
        if(view.width>0&&view.height>0){
          const sx=svg.getBoundingClientRect().width/view.width,sy=svg.getBoundingClientRect().height/view.height;
          stage.scrollLeft=Math.max(0,(bounds.x+bounds.width/2-view.x)*sx-stage.clientWidth/2);
          stage.scrollTop=Math.max(0,(bounds.y+bounds.height/2-view.y)*sy-stage.clientHeight/2);
        }
      }
    }
    function update(parts){
      if(!Array.isArray(parts)||!parts.every(x=>typeof x.id==='string'&&typeof x.label==='string'&&typeof x.status==='string'))throw Error('Invalid inspector model parts');
      const ids=parts.map(x=>x.id);
      if(new Set(ids).size!==ids.length)throw Error('Duplicate inspector part identities');
      current=parts;
      list.replaceChildren();
      for(const part of parts){
        const li=document.createElement('li');
        const btn=document.createElement('button');
        btn.type='button';btn.dataset.partId=part.id;
        btn.textContent=part.label;
        btn.setAttribute('aria-pressed',String(selected===part.id));
        btn.setAttribute('aria-label','Inspect '+part.label+'; status '+part.status);
        btn.addEventListener('click',()=>focusPart(part.id));
        li.appendChild(btn);list.appendChild(li);
      }
      showZoom();
      if(selected&&parts.some(x=>x.id===selected))focusPart(selected);
      else {selected=null;info.textContent='Select a component to read its current label and status.';}
    }
    zoomOut.addEventListener('click',()=>{zoomIndex=Math.max(0,zoomIndex-1);showZoom();});
    zoomIn.addEventListener('click',()=>{zoomIndex=Math.min(presets.length-1,zoomIndex+1);showZoom();});
    zoomReset.addEventListener('click',()=>{zoomIndex=0;showZoom();stage.scrollLeft=0;stage.scrollTop=0;});
    showZoom();
    return {update,focusPart,get zoom(){return presets[zoomIndex]}};
  };
})();`;
