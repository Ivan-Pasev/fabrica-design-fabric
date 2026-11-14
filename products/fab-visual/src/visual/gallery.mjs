/**
 * FAB.VISUAL Ω11L — source-labelled, entirely offline domain gallery.
 *
 * Input content: first-party SYNTHETIC SceneIR templates, NOT sensor readings,
 * scientific or energy performance claims, actual policy execution or approval.
 * Output: one portable folder containing index.html, three editable Studios,
 * 3 original JSON scenes, SVG previews and a SHA-linked manifest.
 */
import {readFileSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {assertScene} from './contract.mjs';
import {renderSvg} from './svg.mjs';
import {renderStudio} from './studio.mjs';
import {canonicalJSON,sha256} from './provenance.mjs';

const SOURCE=join(dirname(fileURLToPath(import.meta.url)),'..','..','templates');
const PROFILE='FIRST_PARTY_SYNTHETIC_SCENE';
const ESC=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const items=Object.freeze([
  {key:'energy',file:'energy-microgrid.scene.json',category:'Energy systems',
   title:'Citizen Solar · Microgrid',eyebrow:'Generation · Storage · Control',
   summary:'Explore synthetic solar-generation, storage and demand routing with typed energy and control links.',
   accent:'#2d7b6d',icon:'☀'},
  {key:'laboratory',file:'lab-daq.scene.json',category:'Research apparatus',
   title:'GILC · Laboratory DAQ',eyebrow:'Sensors · Interlocks · Acquisition',
   summary:'Inspect a hypothetical sensor, chamber and interlock topology without asserting measurements or safety certification.',
   accent:'#496bba',icon:'◇'},
  {key:'agents',file:'agent-evidence.scene.json',category:'Agent orchestration',
   title:'CodexStation · Evidence Gate',eyebrow:'Evidence · Policy · Human Approval',
   summary:'Explore an explanatory agent coordination and approval workflow; external execution remains blocked.',
   accent:'#9562b4',icon:'◎'}
]);
export const DOMAIN_TEMPLATE_CATALOG=items;

export function validateDomainTemplate(scene,descriptor){
  assertScene(scene);
  if(!descriptor||!items.some(x=>x.key===descriptor.key&&x.file===descriptor.file))
    throw Error('unknown fixed registry template');
  const reject=reason=>{throw Error('DOMAIN_TEMPLATE_HOLD: '+reason)};
  if(scene.representation!=='ANALOGICAL')reject('source template cannot imply physical representation');
  if(scene.template?.schema!=='fab.visual.domain-template.v1'||
     scene.template?.origin!=='FIRST_PARTY_SYNTHETIC'||
     scene.template?.scope!=='TOPOLOGY_ILLUSTRATION_ONLY'||
     scene.template?.source_status!=='NOT_MEASURED'||
     scene.template?.real_hardware_or_host_attestation!=='NOT_RUN'||
     scene.template?.domain!==({energy:'energy','laboratory':'laboratory','agents':'agent-orchestration'}[descriptor.key]))
       reject('missing first-party synthetic source status');
  if(scene.model?.source_profile!==PROFILE||scene.model?.synthetic!==true||
     !scene.model.authority.includes('synthetic fixture')||
     !scene.model.authority.includes('no external measurements or authorization'))
    reject('falsely authenticated domain source');
  if(scene.claim?.status!=='EXPLANATORY'||
     !/(synthetic|hypothetical)/i.test(scene.claim.interpretation)||
     Object.values(scene.audit||{}).some(x=>x!=='NOT_RUN'))
    reject('scientific/host claims cannot be promoted');
  if(scene.parts.length>20||scene.parts.length<4||scene.links?.length>35)
    reject('bounded sample topology requires 4-20 nodes and at most 35 links');
  if(!Array.isArray(scene.observables)||scene.observables.length<3||
     scene.observables.some(o=>o.source!==scene.model.authority||o.evidence!=='NOT_RUN'||
       (typeof o.value==='number'&&!(typeof o.unit==='string'&&o.unit.trim().length>0))))
    reject('unlabelled observable provenance or units');
  if(scene.observables.some(o=>typeof o.value==='number'&&!scene.template.all_numeric_observables_are_synthetic))
    reject('numeric synthetic input falsely presented as measurement');
  if(scene.id.length>100||scene.parts.some(p=>p.id.length>100||p.label.length>140))
    reject('model identifier/label bounds exceeded');
  return scene;
}

export function loadDomainTemplates(){
  return items.map(item=>{
    const bytes=readFileSync(join(SOURCE,item.file));
    const scene=validateDomainTemplate(JSON.parse(bytes.toString('utf8')),item);
    return {...item,scene,sourceSha256:sha256(bytes),sceneDigest:'sha256:'+sha256(canonicalJSON(scene))};
  });
}

function galleryClient(){
  'use strict';
  const search=document.getElementById('template-search');
  const select=document.getElementById('template-category');
  const cards=[...document.querySelectorAll('[data-gallery-card]')];
  const result=document.getElementById('gallery-count');
  function filter(){
    const query=search.value.trim().toLocaleLowerCase(),cat=select.value;
    let shown=0;
    for(const card of cards){
      const match=(cat==='all'||card.dataset.category===cat) &&
        card.dataset.search.includes(query);
      card.hidden=!match;
      if(match)shown++;
    }
    result.textContent=shown+' of '+cards.length+' local templates';
    document.getElementById('gallery-empty').hidden=shown!==0;
  }
  search.addEventListener('input',filter);
  select.addEventListener('change',filter);
  filter();
}

export function buildGalleryBundle(templates=loadDomainTemplates()){
  if(!Array.isArray(templates)||templates.length!==3)
    throw Error('gallery accepts exactly 3 fixed source-labelled domain templates');
  const keys=new Set(),assets=[],manifestEntries=[];
  const cards=[];
  for(const source of templates){
    const matched=items.find(x=>x.key===source.key);
    if(!matched||keys.has(source.key)||source.file!==matched.file)
      throw Error('duplicate or unregistered template');
    keys.add(source.key);
    const scene=validateDomainTemplate(source.scene,matched);
    const original=JSON.stringify(scene,null,2)+'\n';
    const iso=renderStudio(scene,{title:matched.title+' — Editable Studio'});
    const svg=renderSvg(scene);
    const studioPath='studios/'+matched.key+'.html';
    const scenePath='scenes/'+matched.key+'.scene.json';
    const svgPath='previews/'+matched.key+'.svg';
    const originalSha=sha256(original);
    assets.push({path:studioPath,content:iso.html});
    assets.push({path:scenePath,content:original});
    assets.push({path:svgPath,content:svg});
    manifestEntries.push({
      id:scene.id,key:matched.key,category:matched.category,
      template_source:'products/fab-visual/templates/'+matched.file,
      template_source_sha256:source.sourceSha256||'NOT_ATTESTED_EXTERNAL_SUPPLY',
      scene_sha256:originalSha,
      canonical_source_digest:'sha256:'+sha256(canonicalJSON(scene)),
      html_sha256:sha256(iso.html),svg_sha256:sha256(svg),
      studio_path:studioPath,scene_path:scenePath,preview_path:svgPath,
      nodes:scene.parts.length,links:(scene.links||[]).length,
      observables:scene.observables.length,
      synthetic_scene:true,claim_status:scene.claim.status,
      isometric_audit:iso.metadata.isoStatus,
      physical_or_scientific_validation:'NOT_RUN',production_release:'HOLD'
    });
    cards.push('<article class="template-card" data-gallery-card data-category="'+ESC(matched.category)+
      '" data-search="'+ESC((matched.title+' '+matched.eyebrow+' '+matched.category+' '+matched.summary).toLocaleLowerCase())+
      '" style="--accent:'+matched.accent+'">'+
      '<div class="card-top"><span class="glyph" aria-hidden="true">'+matched.icon+'</span><span class="kind">'+ESC(matched.category)+'</span></div>'+
      '<p class="eyebrow">'+ESC(matched.eyebrow)+'</p><h3>'+ESC(matched.title)+'</h3>'+
      '<p class="description">'+ESC(matched.summary)+'</p>'+
      '<div class="thumb">'+svg+'</div>'+
      '<div class="template-data"><span>'+scene.parts.length+' components</span><span>'+(scene.links||[]).length+
      ' links</span><span>'+scene.observables.length+' simulated readouts</span></div>'+
      '<div class="actions"><a class="primary" data-open-studio="'+matched.key+'" href="'+studioPath+
      '">Open editable Studio</a><a class="secondary" href="'+scenePath+
      '" download="'+matched.key+'.scene.json">SceneIR JSON</a></div>'+
      '<p class="trust">SYNTHETIC · EXPLANATORY · Not measured · Release HOLD</p></article>');
  }
  const css=[
'*{box-sizing:border-box}html{color-scheme:light}body{margin:0;color:#193048;background:#f2f6fb;font:15px/1.55 system-ui,sans-serif}',
'main{max-width:1470px;margin:0 auto;padding:28px 24px}a{color:inherit;text-decoration:none}',
'.hero{border-radius:24px;background:linear-gradient(120deg,#112b47,#254b72);color:#fff;padding:34px 36px;display:grid;grid-template-columns:1.8fr 1fr;gap:30px}',
'.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-weight:800;font-size:.72rem;color:#7bafc4;margin:0 0 9px}',
'.hero .eyebrow{color:#b8e7e5}.hero h1{letter-spacing:-.045em;font-size:clamp(2rem,4.3vw,3.55rem);line-height:1.09;margin:0 0 15px}',
'.hero p{max-width:72ch;margin:0;opacity:.91}.hero-stats{display:grid;align-content:center;grid-template-columns:repeat(2,1fr);gap:10px}',
'.hero-stats div{border:1px solid #6d93b9;border-radius:13px;padding:16px}.hero-stats strong{display:block;font-size:1.6rem}.hero-stats span{font-size:.83rem;color:#c6deee}',
'.tools{display:flex;justify-content:space-between;gap:14px;align-items:center;margin:24px 0 16px;flex-wrap:wrap}',
'.tools h2{font-size:1.2rem;margin:0}.tool-inputs{display:flex;gap:10px;flex-wrap:wrap}',
'input,select{min-height:45px;padding:10px 12px;border:1px solid #9bb3ca;border-radius:10px;background:white;color:#23425f;font:inherit}',
'input{width:min(340px,80vw)}:focus-visible{outline:3px solid #2e8ea9;outline-offset:3px}',
'.gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}',
'.template-card{min-width:0;border:1px solid #c5d4e3;background:#fff;border-radius:18px;padding:21px;display:flex;flex-direction:column;box-shadow:0 2px 6px #253b4c0c}',
'.card-top{display:flex;align-items:center;justify-content:space-between;gap:12px}.glyph{color:var(--accent);font-size:2rem;font-weight:800}',
'.kind{border:1px solid #cad7e3;padding:5px 10px;border-radius:999px;font-size:.72rem;color:#4b6073}',
'.template-card .eyebrow{color:var(--accent);margin-top:16px}.template-card h3{font-size:1.45rem;letter-spacing:-.03em;line-height:1.2;margin:0 0 9px}',
'.description{margin:0 0 15px;color:#53697b;min-height:4.6em}',
'.thumb{height:200px;overflow:hidden;border:1px solid #deebf1;border-radius:11px;background:#f8fafc;display:grid;place-items:center;padding:6px}',
'.thumb svg{width:100%!important;height:100%!important;max-width:100%;max-height:100%}',
'.template-data{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0 auto}.template-data span{font-size:.72rem;border:1px solid #d9e3ed;background:#f5f8fb;padding:4px 7px;border-radius:7px}',
'.actions{display:flex;gap:8px;margin-top:20px;flex-wrap:wrap}.actions a{display:inline-flex;align-items:center;justify-content:center;min-height:43px;border-radius:9px;padding:10px 12px;font-size:.87rem;font-weight:750}',
'.primary{background:#1c547f;color:white}.secondary{border:1px solid #8ba8be;color:#254966}.actions a:hover{filter:brightness(.94)}',
'.trust{font-size:.72rem;color:#5d6b78;margin:15px 0 0;padding-top:12px;border-top:1px solid #e1e8ef}',
'.info{margin:24px 0;background:#fff;border:1px solid #c5d4e3;border-radius:14px;padding:18px;color:#465a6d}',
'footer{font-size:.83rem;color:#607386;margin:20px 0;max-width:100ch}',
'[hidden]{display:none!important}',
'@media(max-width:1100px){.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}}',
'@media(max-width:700px){main{padding:12px}.hero{grid-template-columns:1fr;padding:25px}.gallery{grid-template-columns:1fr}.description{min-height:0}.thumb{height:230px}}'
].join('');
  const page=[
'<!doctype html><html lang="en"><head><meta charset="utf-8">',
'<meta name="viewport" content="width=device-width,initial-scale=1">',
'<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; script-src &#39;unsafe-inline&#39;; style-src &#39;unsafe-inline&#39;; img-src data: blob:; connect-src &#39;none&#39;; font-src &#39;none&#39;; base-uri &#39;none&#39;; object-src &#39;none&#39;">',
'<title>FAB.VISUAL — Domain Template Gallery</title><style>'+css+'</style></head><body><main>',
'<header class="hero"><div><p class="eyebrow">FAB.SYS / FAB.VISUAL · Ω11L</p>',
'<h1>Explore ideas.<br>Build visual systems.</h1>',
'<p>Choose a source-labelled synthetic topology and open its fully offline editable Studio. Energy systems, research apparatus and agent orchestration—all in one portable package, with zero external runtime dependencies.</p></div>',
'<div class="hero-stats"><div><strong>03</strong><span>Domain template packs</span></div>',
'<div><strong>100%</strong><span>Offline static gallery</span></div>',
'<div><strong>SceneIR</strong><span>Typed source model</span></div>',
'<div><strong>HOLD</strong><span>Production release</span></div></div></header>',
'<section class="tools" aria-label="Template filters"><div><h2>Domain templates</h2>',
'<p id="gallery-count" role="status" aria-live="polite"></p></div><div class="tool-inputs">',
'<label for="template-search">Search <input id="template-search" type="search" placeholder="Find a capability…" autocomplete="off"></label>',
'<label for="template-category">Category <select id="template-category"><option value="all">All categories</option>',
...items.map(x=>'<option value="'+ESC(x.category)+'">'+ESC(x.category)+'</option>'),
'</select></label></div></section>',
'<section class="gallery" id="gallery" aria-label="Three selectable templates">',...cards,'</section>',
'<p id="gallery-empty" hidden>No matching templates. Try another search or category.</p>',
'<section class="info"><strong>How to use</strong><p>Choose <b>Open editable Studio</b>, inspect the source model, move or resize illustrative components, create typed links, undo/redo and export local scenes or graph formats. Source HTML, SceneIR JSON and SVG previews are packaged next to this gallery; opening local files needs no server.</p></section>',
'<footer>All templates are explicitly synthetic first-party examples. Observable values are not measured, physical equipment is not certified, no agents are connected or authorized, and the diagrams are not scientific proof. Every release remains HOLD. No private project data is embedded.</footer>',
'</main><script>('+galleryClient.toString()+')();</script></body></html>'
];
  const html=page.join('');
  const manifest={schema:'fab.visual.gallery-manifest.v1',
    generated_from:'PINNED_FIRST_PARTY_SYNTHETIC_TEMPLATES',
    templates:manifestEntries,output_html_sha256:sha256(html),
    scope:'ANALOGICAL_TOPOLOGY_DEMOS_ONLY',
    external_resources_required:false,source_authority_transferred:false,
    real_measurements:'NOT_PRESENT',scientific_certification:'NOT_RUN',
    physical_validity:'NOT_RUN',host_authorization:'NOT_RUN',
    release:'HOLD'};
  assets.push({path:'index.html',content:html});
  assets.push({path:'gallery.manifest.json',content:JSON.stringify(manifest,null,2)+'\n'});
  return {assets,manifest};
}
