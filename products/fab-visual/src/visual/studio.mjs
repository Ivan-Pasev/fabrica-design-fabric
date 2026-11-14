/**
 * FAB.VISUAL Ω11J — standalone, dependency-free product workbench.
 *
 * Compiles ONLY validated SceneIR into safe, self-contained local HTML.
 * Renders actual pinned Anatomy isometric geometry when ANALOGICAL audit passes,
 * while retaining the independent SVG reference and explicit evidence boundary.
 * The browser client cannot grant host authorization or scientific validation.
 */
import {assertScene} from './contract.mjs';
import {renderSvg} from './svg.mjs';
import {canonicalJSON,sha256} from './provenance.mjs';
import {inspectorParts,inspectorMarkup,inspectorCss,inspectorRuntime} from './semantic-inspector.mjs';
import {renderAnatomySvg,anatomySceneModel} from '../adapters/anatomy-kernel.mjs';
import {FORMATS,exportInterchange} from '../adapters/interchange.mjs';
import {importGraphAgainstSource} from '../adapters/graph-import.mjs';
import {studioEditorClient} from './editor-runtime.mjs';
import {forkVisualScene,visualDiff,zipStore,projectFiles} from './project.mjs';
import {parseProjectZip,canonicalProjectDigest,admitProjectArchive} from './project-import.mjs';

const escapeHtml=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeJSON=value=>JSON.stringify(value).replace(/</g,'\\u003c').replace(/>/g,'\\u003e')
  .replace(/&/g,'\\u0026').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');

const STUDIO_STYLE=[
'html{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#eef3f9;color:#182b42;font:15px/1.5 system-ui,-apple-system,sans-serif}',
'main{max-width:1500px;margin:0 auto;padding:22px}header{display:flex;gap:20px;justify-content:space-between;align-items:start;flex-wrap:wrap}',
'h1{font-size:clamp(1.6rem,3vw,2.4rem);letter-spacing:-.04em;line-height:1.12;margin:0 0 7px}',
'.eyebrow{font-size:.75rem;color:#36516d;letter-spacing:.14em;font-weight:750;text-transform:uppercase;margin:0 0 8px}',
'.subtitle{max-width:77ch;color:#42576e;margin:5px 0}',
'.pill{border:1px solid #a1b5cb;color:#244762;background:#e7edf5;padding:7px 13px;border-radius:999px;font-weight:700;font-size:.8rem}',
'.overview{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:23px 0}',
'.metric{padding:15px;background:white;border:1px solid #bdcee0;border-radius:13px;min-width:0}.metric span{display:block;color:#456075;font-size:.8rem}',
'.metric strong{display:block;font-size:1.18rem;overflow-wrap:anywhere}',
'.workbench{display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);align-items:start;gap:16px}',
'.paper,.sidecard{background:#fff;border:1px solid #b8cadb;border-radius:16px;overflow:hidden}',
'.paperbar{padding:13px 17px;border-bottom:1px solid #d8e1eb;display:flex;gap:8px;justify-content:space-between;align-items:center;flex-wrap:wrap}',
'.buttons{display:flex;gap:6px;flex-wrap:wrap}button,select,input{font:inherit}button,select{padding:9px 13px;border:1px solid #829db5;border-radius:9px;background:#fff;color:#1f3850;cursor:pointer}',
'button[aria-pressed=true]{color:white;background:#25547c;border-color:#25547c}button:disabled{opacity:.45;cursor:not-allowed}',
'button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #146fb4;outline-offset:3px}',
'.visual-scroll{min-height:350px;overflow:auto;background:#f8fbff;max-height:72vh;scrollbar-gutter:stable}',
'.visual-scroll svg{max-width:none;display:block;width:100%;height:auto}',
'.visual-scroll svg .part[data-selected=true] rect{stroke:#b54b18;stroke-width:4}',
'.visual-scroll svg .part[data-selected=true] .outline{stroke:#b54b18;stroke-width:5}',
'.compare-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;padding:8px}',
'.compare-grid figure{margin:0;border:1px solid #c8d6e7;border-radius:10px;overflow:hidden;min-width:0}',
'.compare-grid figcaption{padding:8px 10px;background:#eaf0f7;font-size:.8rem;font-weight:750}',
'.compare-grid svg{width:100%}',
'.sidebar{display:grid;gap:16px}.sidecard{padding:17px}.sidecard h2{font-size:1rem;margin:0 0 8px}',
'.sidecard p,.sidecard pre{overflow-wrap:anywhere}.sidecard pre{white-space:pre-wrap;font-size:.8rem}',
'.statusbar{padding:11px 17px;border-top:1px solid #d8e1eb;color:#425974;font-size:.86rem}',
'.export-list{display:flex;flex-wrap:wrap;gap:8px}.export-list button{font-size:.88rem}',
'.search{width:100%;padding:11px 12px;border:1px solid #839cb3;border-radius:9px}',
'.edit-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:10px 0}.edit-grid label{display:grid;gap:3px;font-size:.83rem}.edit-grid input,.edit-grid select{width:100%;padding:8px;border:1px solid #849bb5;border-radius:8px}.edit-actions{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}.edit-actions button{min-height:40px}#edit-status{font-size:.85rem;min-height:3em;overflow-wrap:anywhere;background:#edf4fc;border-radius:8px;padding:9px}#edit-mode{font-size:.8rem;color:#4c6076}',
'footer{margin-top:20px;color:#4b5d72;font-size:.82rem;max-width:100ch}',
'details{margin:10px 0}summary{cursor:pointer;font-weight:600}',
'.project-tools{margin:13px 0;border:1px solid #cad8e5;background:#f4f8fc;border-radius:12px;padding:12px}',
'.project-tools label{display:grid;gap:4px;font-size:.8rem}.project-tools input{width:100%;padding:9px;border:1px solid #92a9c0;border-radius:8px}',
'.project-actions{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}.project-actions button{min-height:41px}',
'.visual-diff{border:1px solid #c8d7e6;border-radius:10px;padding:12px;background:#fff;margin-top:12px}',
'.diff-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.diff-panel{min-width:0;max-height:280px;overflow:auto;border:1px solid #d2dce7;border-radius:8px;padding:7px}.diff-panel svg{width:100%;height:auto}',
'.diff-list{padding-left:20px;font-size:.83rem;color:#344e68}.diff-list li{margin:4px 0}',
'#stage [data-flow][role="button"]{cursor:pointer}#stage [data-flow][data-edit-selected="true"]{stroke:#cc5d18;stroke-width:5}',
'.import-replay{margin:12px 0;padding:12px;border:1px solid #b9cedc;border-radius:12px;background:#edf5fb}',
'.import-replay input{width:100%;max-width:100%;padding:8px}.replay-strip{display:flex;gap:7px;flex-wrap:wrap;margin:9px 0}',
'.replay-strip button{font-size:.78rem;padding:8px 11px}.replay-strip button[aria-current=true]{background:#245f8b;color:#fff}',
'.replay-actions{display:flex;gap:6px;flex-wrap:wrap}.replay-actions button{min-height:40px}',
'.replay-status{font-size:.79rem;overflow-wrap:anywhere;white-space:pre-line}',
'#stage [data-part][role="button"]{cursor:pointer}#stage [data-part][data-connect-selected="true"] rect{stroke:#d87a16;stroke-width:4}',
'@media(max-width:1000px){.workbench{grid-template-columns:1fr}.sidebar{grid-template-columns:repeat(2,minmax(0,1fr))}}',
'@media(max-width:640px){main{padding:12px}.overview{grid-template-columns:repeat(2,minmax(0,1fr))}.sidebar{grid-template-columns:1fr}.compare-grid{grid-template-columns:1fr}.visual-scroll{min-height:200px;max-height:60vh}}',
'@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}',
inspectorCss
].join('');

function studioClient(){
  'use strict';
  const data=JSON.parse(document.getElementById('fab-studio-data').textContent);
  const stage=document.getElementById('stage');
  const state=document.getElementById('scene-state');
  const filter=document.getElementById('flow-filter');
  const search=document.getElementById('component-search');
  const inspector=window.FabVisualInspector(stage);
  const buttons=[...document.querySelectorAll('button[data-view]')];
  const exports=[...document.querySelectorAll('button[data-export]')];
  let view='2d';

  for(const flow of data.flowTypes){
    const option=document.createElement('option');
    option.value=flow;option.textContent=flow;
    filter.appendChild(option);
  }
  function applyFilter(){
    const selected=filter.value;
    for(const link of stage.querySelectorAll('[data-flow]')){
      link.style.display=selected==='all'||link.dataset.flow===selected?'':'none';
    }
  }
  function updateSearch(){
    const needle=search.value.trim().toLocaleLowerCase();
    let visible=0;
    for(const btn of document.querySelectorAll('#part-list button[data-part-id]')){
      const found=btn.textContent.toLocaleLowerCase().includes(needle)
        ||btn.dataset.partId.toLocaleLowerCase().includes(needle);
      btn.parentElement.hidden=!found;if(found)visible++;
    }
    const count=document.getElementById('search-count');
    count.textContent=visible+' of '+data.parts.length+' components';
  }
  function markSelected(id){
    for(const part of stage.querySelectorAll('[data-part]')){
      part.setAttribute('data-selected',String(part.getAttribute('data-part')===id));
    }
  }
  function paint(next){
    if(next!=='2d' && !data.iso)next='2d';
    if(!['2d','isometric','compare'].includes(next))next='2d';
    view=next;
    if(view==='compare'){
      stage.innerHTML='<div class="compare-grid"><figure><figcaption>Independent 2D reference</figcaption>'
        +data.svg2d+'</figure><figure><figcaption>Pinned Anatomy isometric</figcaption>'
        +data.iso+'</figure></div>';
    }else stage.innerHTML=(view==='isometric'?data.iso:data.svg2d);
    inspector.update(data.parts);applyFilter();updateSearch();
    for(const b of buttons)b.setAttribute('aria-pressed',String(b.dataset.view===view));
    state.textContent='View: '+(view==='2d'?'reference 2D':view==='isometric'?'pinned Anatomy isometric':'2D / Anatomy comparison')
      +' · '+data.scene.representation+' · evidence '+data.scene.claim.status+' · release HOLD';
  }
  function download(kind){
    const entry=kind==='svg'?
      {text:view==='isometric'?data.iso:data.svgRaw,mime:'image/svg+xml',extension:'svg'}:
      kind==='scene'?
      {text:JSON.stringify(data.scene,null,2)+'\n',mime:'application/json',extension:'json'}:
      data.exports[kind];
    if(!entry)return;
    const blob=new Blob([entry.text],{type:entry.mime+';charset=utf-8'});
    const url=URL.createObjectURL(blob),link=document.createElement('a');
    link.href=url;link.download='fab-visual-'+kind+'.'+entry.extension;
    document.body.appendChild(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),2000);
    document.getElementById('download-status').textContent=kind+' exported locally. Claim/release unchanged: HOLD.';
  }
  for(const b of buttons)b.addEventListener('click',()=>paint(b.dataset.view));
  for(const b of exports)b.addEventListener('click',()=>download(b.dataset.export));
  stage.addEventListener('click',event=>{
    const node=event.target.closest('[data-part]');
    if(node){inspector.focusPart(node.dataset.part);markSelected(node.dataset.part);}
  });
  stage.addEventListener('keydown',event=>{
    if(event.key==='Enter' || event.key===' '){
      const node=event.target.closest('[data-part]');
      if(node){event.preventDefault();inspector.focusPart(node.dataset.part);markSelected(node.dataset.part);}
    }
  });
  // Keep both reference and Anatomy panes at the same magnification in Compare.
  // Inspector owns first-svg zoom; this listener copies its confirmed width.
  for(const zoomControl of document.querySelectorAll('#zoom-in,#zoom-out,#zoom-reset')){
    zoomControl.addEventListener('click',()=>{
      if(view!=='compare')return;
      const svgs=[...stage.querySelectorAll('svg')];
      if(svgs.length<2)return;
      for(const other of svgs.slice(1))other.style.width=svgs[0].style.width;
    });
  }
  filter.addEventListener('change',applyFilter);
  search.addEventListener('input',updateSearch);
  paint('2d');
}

export function renderStudio(scene,{title='FAB.VISUAL Studio · local scene explorer'}={}) {
  assertScene(scene);
  if(scene.parts.length>300||(scene.links||[]).length>800||(scene.observables||[]).length>300)
    throw Error('studio cap: 300 components, 800 flows, 300 observables');
  if(typeof title!=='string'||title.length>180)throw Error('invalid studio title');
  const svgRaw=renderSvg(scene);
  const svg2d=svgRaw.replaceAll('class="node ','class="part node ');
  let iso=null,isoStatus='NOT_RUN',isoReason='Isometric view supports analogical models only.';
  if(scene.representation==='ANALOGICAL'){
    try{
      const model=anatomySceneModel(scene);
      if(model.audit.status==='PASS'){
        iso=renderAnatomySvg(scene);
        isoStatus='PASS_BOUNDED_SAMPLED_ANATOMY';
        isoReason='Pinned MIT Anatomy subset; sampled geometry only; no physical certification.';
      }else{isoStatus='FAIL';isoReason='Isometric sampled geometry check failed.';}
    }catch(e){isoStatus='FAIL_OR_INCONCLUSIVE';isoReason=String(e.message).slice(0,250);}
  }
  const formats=Object.fromEntries(FORMATS.map(format=>{
    const value=exportInterchange(scene,format);
    return [format,{text:value.text,mime:value.mediaType,extension:value.extension}];
  }));
  const bundle={
    schema:'fab.visual.studio.v1',scene,parts:inspectorParts(scene),svgRaw,svg2d,iso,
    isoStatus,isoReason,flowTypes:[...new Set((scene.links||[]).map(e=>e.flow))].sort(),
    exports:formats,
    sourceDigest:'sha256:'+sha256(canonicalJSON(scene)),
    generatedLocally:true,release:'HOLD',
    claim:'MODEL_DERIVED_INTERACTIVE_VIEW_NOT_PROOF'
  };
  const noIso=iso===null?' disabled aria-disabled="true"':'';
  const claim=escapeHtml(scene.claim.interpretation);
  const page=[
    '<!doctype html><html lang="en"><head><meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; script-src &#39;unsafe-inline&#39;; style-src &#39;unsafe-inline&#39;; img-src data: blob:; connect-src &#39;none&#39;; font-src &#39;none&#39;; object-src &#39;none&#39;; base-uri &#39;none&#39;">',
    '<title>'+escapeHtml(title)+'</title><style>'+STUDIO_STYLE+'</style></head><body>',
    '<main><header><div><p class="eyebrow">FAB.VISUAL / Product Studio</p><h1>'+escapeHtml(title)+'</h1>',
    '<p class="subtitle">Explore model-derived diagrams, inspect source identities, compare reference and pinned isometric geometry, and export portable graph formats. No network connection needed.</p></div>',
    '<span class="pill">Research preview · Release HOLD</span></header>',
    '<section class="overview" aria-label="Source model summary">',
    '<div class="metric"><span>Model</span><strong>'+escapeHtml(scene.model.id)+'</strong></div>',
    '<div class="metric"><span>Revision</span><strong>'+escapeHtml(scene.model.revision)+'</strong></div>',
    '<div class="metric"><span>Components</span><strong>'+scene.parts.length+'</strong></div>',
    '<div class="metric"><span>Flows</span><strong>'+(scene.links||[]).length+'</strong></div>',
    '</section><div class="workbench"><section class="paper" aria-label="Visual studio">',
    '<div class="paperbar"><div class="buttons" role="group" aria-label="View mode">',
    '<button type="button" data-view="2d" aria-pressed="true">Reference 2D</button>',
    '<button type="button" data-view="isometric" aria-pressed="false"'+noIso+'>Anatomy isometric</button>',
    '<button type="button" data-view="compare" aria-pressed="false"'+noIso+'>Compare</button></div>',
    '<label>Flow <select id="flow-filter" aria-label="Flow visibility filter"><option value="all">All flows</option></select></label></div>',
    '<div id="stage" class="visual-scroll" tabindex="0" role="region" aria-label="Interactive semantic diagram" aria-describedby="zoom-hint"></div>',
    '<div class="statusbar" id="scene-state" role="status" aria-live="polite"></div></section>',
    '<aside class="sidebar"><section class="sidecard">',
    '<h2>Component explorer</h2><label for="component-search">Find components by ID or label</label>',
    '<input class="search" id="component-search" type="search" placeholder="Search the model" autocomplete="off">',
    '<p id="search-count" role="status"></p>'+inspectorMarkup+'</section>',
    '<section class="sidecard"><h2>Offline visual editor</h2>',
    '<p>Edit layout geometry and illustrative connections, undo/redo snapshots, or import a previously exported graph. Model approval and source authority cannot change.</p>',
    '<p id="edit-mode">Original source view</p>',
    '<label for="edit-part">Component</label><select id="edit-part" class="search"></select>',
    '<div class="edit-grid"><label>X<input id="edit-x" type="number" step="any"></label><label>Y<input id="edit-y" type="number" step="any"></label>',
    '<label>Width<input id="edit-w" type="number" min="0.01" step="any"></label><label>Height<input id="edit-h" type="number" min="0.01" step="any"></label></div>',
    '<div class="edit-actions"><button type="button" id="edit-apply">Apply layout</button><button type="button" id="edit-undo">Undo</button><button type="button" id="edit-redo">Redo</button></div>',
    '<p id="edit-history"></p><h3>Add illustrative connection</h3>',
    '<div class="edit-grid"><label>From<select id="edit-from"></select></label><label>To<select id="edit-to"></select></label>',
    '<label>Flow<select id="edit-flow"></select></label></div>',
    '<button type="button" id="edit-add-link">Add connection</button>',
    '<label for="edit-link-select">Existing connection</label><select id="edit-link-select" class="search"></select>',
    '<button type="button" id="edit-remove-link">Remove selected connection</button>',
    '<div class="project-tools" aria-label="Source-preserving project actions">',
    '<h3>Canvas connectors and local projects</h3>',
    '<p>Use the canvas or keyboard to select source-defined nodes and existing flows; actions stay illustrative.</p>',
    '<button type="button" id="edit-canvas-connect" aria-pressed="false">Connect nodes on canvas</button>',
    '<p id="edit-canvas-status" role="status" aria-live="polite">Select an edge to inspect it, or activate connector mode.</p>',
    '<label for="edit-fork-slug">Local fork identifier<input id="edit-fork-slug" maxlength="40" pattern="[a-z0-9][a-z0-9-]*" value="experiment"></label>',
    '<div class="project-actions"><button type="button" id="edit-fork">Download fork SceneIR</button>',
    '<button type="button" id="edit-project">Download project ZIP</button>',
    '<button type="button" id="edit-diff-toggle" aria-expanded="false">Compare source / current</button></div>',
    '<label for="edit-revision">Compare revision<select id="edit-revision"></select></label>',
    '<div id="edit-diff" class="visual-diff" hidden></div>',
    '</div>',
    '<section class="import-replay" aria-label="Open and replay offline portable project">',
    '<h3>Open portable project ZIP</h3>',
    '<p>Choose a local FAB.VISUAL project. Its original scene, SHA-256, fork, history and all ZIP entries must match before admission. No publisher authentication or live execution.</p>',
    '<label for="edit-project-import-file">Local project ZIP<input id="edit-project-import-file" type="file" accept=".zip,application/zip"></label>',
    '<p id="edit-project-import-status" class="replay-status" role="status" aria-live="polite">No project opened · RELEASE HOLD</p>',
    '<div id="edit-replay-cards" class="replay-strip" role="group" aria-label="Local revision cards"></div>',
    '<div class="replay-actions"><button type="button" id="edit-replay-prev" disabled>Previous</button>',
    '<button type="button" id="edit-replay-next" disabled>Next</button>',
    '<button type="button" id="edit-replay-apply" disabled>Apply selected revision</button></div>',
    '</section>',
    '<h3>Import source-anchored graph</h3>',
    '<label>Graph format<select id="graph-import-format"><option value="reactflow">XYFlow / React Flow</option><option value="cytoscape">Cytoscape.js</option></select></label>',
    '<label>Local JSON<input class="search" id="graph-import-file" type="file" accept=".json,application/json"></label>',
    '<p id="edit-status" role="status" aria-live="polite"></p>',
    '</section><section class="sidecard"><h2>Export and interoperability</h2>',
    '<p>Download model-derived, evidence-bounded artifacts. The original model is not modified.</p>',
    '<div class="export-list">',
    '<button type="button" data-export="svg">SVG</button>',
    '<button type="button" data-export="scene">SceneIR JSON</button>',
    '<button type="button" data-export="lineage">Local edit history</button>',
    '<button type="button" data-export="reactflow">XYFlow JSON</button>',
    '<button type="button" data-export="cytoscape">Cytoscape JSON</button>',
    '<button type="button" data-export="mermaid">Mermaid</button>',
    '<button type="button" data-export="dot">Graphviz DOT</button></div>',
    '<p id="download-status" role="status" aria-live="polite"></p>',
    '<details><summary>Evidence and model observables</summary><pre>'+escapeHtml(JSON.stringify({authority:scene.model.authority,claim:scene.claim,observables:scene.observables||[],source_digest:bundle.sourceDigest},null,2))+'</pre></details>',
    '<p><strong>Isometric:</strong> '+escapeHtml(isoStatus)+' — '+escapeHtml(isoReason)+'</p>',
    '<p><strong>Claim:</strong> '+claim+'</p></section></aside></div>',
    '<footer>FAB.VISUAL · no external runtime imports · semantic graph exports are not scientific proof, real metrology, executed authorization or GPU-presented-frame attestation. All releases HOLD.</footer>',
    '</main><script type="application/json" id="fab-studio-data">'+safeJSON(bundle)+'</script>',
    '<script>'+inspectorRuntime+'</script>',
    '<script>('+studioClient.toString()+')();</script>',
    '<script>('+studioEditorClient.toString()+')('+importGraphAgainstSource.toString()+','+
       visualDiff.toString()+','+forkVisualScene.toString()+','+zipStore.toString()+','+projectFiles.toString()+','+
       admitProjectArchive.toString()+','+canonicalProjectDigest.toString()+','+parseProjectZip.toString()+');</script></body></html>'
  ];
  const html=page.join('');
  return {
    html,
    metadata:{
      schema:'fab.visual.studio-witness.v1',
      sceneId:scene.id,model:scene.model,representation:scene.representation,
      sourceDigest:bundle.sourceDigest,
      outputDigest:'sha256:'+sha256(html),
      byteCount:Buffer.byteLength(html,'utf8'),
      views:iso?['2d','isometric','compare']:['2d'],
      interchangeFormats:FORMATS,
      isoStatus,isoReason,
      validation:'SCENEIR_VALIDATED',
      claim:'MODEL_DERIVED_INTERACTIVE_VIEW_NOT_PROOF',
      realRendererFrame:'NOT_ADMITTED',scientificCertification:'NOT_RUN',
      activeHostAuthorization:'NOT_RUN',
      release:'HOLD'
    }
  };
}
