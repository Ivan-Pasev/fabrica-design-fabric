import { assertScene } from './contract.mjs';
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num = value => Number(value.toFixed(3));
const anchor = p => ({ x: p.x + p.w / 2, y: p.y + p.h / 2 });
// A trusted 2D reference renderer: NOT Anatomy; deterministic SVG with embedded component semantics.
export function renderSvg(scene, { title = scene.id, width = 1100, height = 690, projection = '2d' } = {}) {
  assertScene(scene);
  if (![width, height].every(v => Number.isInteger(v) && v >= 200 && v <= 4096)) throw new Error('unsupported output size');
  if (!['2d', 'isometric'].includes(projection)) throw new Error('unsupported projection');
  const map = new Map(scene.parts.map(p => [p.id, p]));
  const project = (p) => projection === '2d' ? [p.x, p.y] : [p.x - p.y * 0.18, p.y * 0.84];
  const lines = [];
  for (const [i, link] of (scene.links || []).entries()) {
    const a = anchor(map.get(link.from)); const b = anchor(map.get(link.to));
    const [x1,y1] = project(a), [x2,y2] = project(b);
    lines.push(`<path class="edge" data-flow="${esc(link.flow)}" data-edge="${i}" d="M${num(x1)} ${num(y1)} L${num(x2)} ${num(y2)}"/><title>${esc(link.from)} to ${esc(link.to)}</title>`);
  }
  const shapes = scene.parts.map((part, i) => {
    const [x,y] = project(part); const [_, ey] = project({ x: part.x, y: part.y + part.h });
    const w = part.w; const h = projection === '2d' ? part.h : Math.max(15, ey-y);
    const group = esc(part.id);
    const label = esc(part.label);
    const status = esc(part.status || 'NEUTRAL');
    const color = ['BLOCKED','DENIED','FAIL'].includes(part.status) ? 'blocked' : ['ALLOWED','RELEASED','PASS'].includes(part.status) ? 'approved' : 'neutral';
    return `<g class="node ${color}" data-part="${group}" data-status="${status}" role="group" aria-label="${label}, ${status}"><rect x="${num(x)}" y="${num(y)}" width="${num(w)}" height="${num(h)}" rx="11"/><text x="${num(x+w/2)}" y="${num(y+h/2+4)}" text-anchor="middle">${label}</text><title>${label}: ${status}</title></g>`;
  });
  const obs = (scene.observables || []).map(o=>`<text x="24" y="${num(540 + 20 * (scene.observables || []).indexOf(o))}">${esc(o.id)}: ${esc(o.value)} ${esc(o.unit || '')}</text>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" role="img" aria-labelledby="t d"><title id="t">${esc(title)}</title><desc id="d">${esc(scene.claim.interpretation)}. ${scene.parts.length} semantic components; ${scene.links?.length || 0} connections. Status ${esc(scene.claim.status)}.</desc><style>.bg{fill:#fff}.edge{stroke:#6b7890;stroke-width:2;fill:none}.node rect{stroke:#46566a;stroke-width:1.7;fill:#edf2f7}.node text{fill:#243045;font:600 14px system-ui,sans-serif}.node.approved rect{fill:#daf5e7;stroke:#267e58}.node.blocked rect{fill:#ffe2df;stroke:#bf4545}text{fill:#243045;font:13px system-ui,sans-serif}</style><rect class="bg" width="100%" height="100%"/><g aria-hidden="true">${lines.join('')}</g><g>${shapes.join('')}</g><g aria-label="Model observables">${obs}</g></svg>`;
}
export function renderHtml(scene, config = {}) {
  const svg = renderSvg(scene, config);
  const serialized = JSON.stringify({id:scene.id, model:scene.model, observables:scene.observables || [], claim:scene.claim}).replace(/</g,'\\u003c');
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(scene.id)}</title><style>body{margin:0;background:#f2f5f8;color:#1f2937;font:16px system-ui,sans-serif}main{max-width:1140px;padding:2rem;margin:auto}figure{margin:0}svg{max-width:100%;height:auto;display:block}figcaption{margin-top:1rem}.status{font-size:.9rem}</style></head><body><main><h1>${esc(scene.id)}</h1><figure>${svg}<figcaption>${esc(scene.claim.interpretation)} — ${esc(scene.claim.status)}</figcaption></figure><p class="status">This visualization is ${esc(scene.representation.toLowerCase())}; rendering is not scientific validation.</p><details><summary>Source and observables</summary><pre id="model"></pre></details></main><script type="application/json" id="fab-model">${serialized}</script><script>document.getElementById('model').textContent=JSON.stringify(JSON.parse(document.getElementById('fab-model').textContent),null,2)</script></body></html>`;
}
