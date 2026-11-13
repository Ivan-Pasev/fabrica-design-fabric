// FAB.VISUAL model/scene contracts; independent source, no upstream Anatomy code.
const KIND = new Set(['PHYSICAL', 'ANALOGICAL', 'FORMAL']);
const FLOW = new Set(['signal', 'energy', 'material', 'control', 'information', 'dependency', 'mechanical']);
const EVIDENCE = new Set(['PASS', 'FAIL', 'NOT_RUN', 'INCONCLUSIVE', 'EXCEPTION']);
const inText = x => typeof x === 'string' && x.trim().length > 0;
const validNumber = n => typeof n === 'number' && Number.isFinite(n);
function fail(errors, path, reason) { errors.push(`${path}: ${reason}`); }
export function validateScene(scene) {
  const errors = [];
  if (!scene || typeof scene !== 'object' || Array.isArray(scene)) return { ok: false, errors: ['scene: expected object'] };
  if (scene.schema !== 'fab.scene.v0.2') fail(errors, 'schema', 'must be fab.scene.v0.2');
  if (!inText(scene.id)) fail(errors, 'id', 'required');
  if (!KIND.has(scene.representation)) fail(errors, 'representation', 'invalid');
  if (!inText(scene.model?.id) || !inText(scene.model?.revision) || !inText(scene.model?.authority)) fail(errors, 'model', 'id, revision and authority required');
  if (!Array.isArray(scene.parts) || scene.parts.length === 0) fail(errors, 'parts', 'nonempty array required');
  const parts = Array.isArray(scene.parts) ? scene.parts : [];
  const ids = new Set();
  const parents = new Map();
  for (const [n, part] of parts.entries()) {
    const base = `parts[${n}]`;
    if (!inText(part?.id) || ids.has(part.id)) fail(errors, `${base}.id`, 'missing or duplicate');
    else ids.add(part.id);
    if (!inText(part?.label)) fail(errors, `${base}.label`, 'missing');
    for (const k of ['x','y','w','h']) if (!validNumber(part?.[k])) fail(errors, `${base}.${k}`, 'finite number required');
    if (validNumber(part?.w) && part.w <= 0) fail(errors, `${base}.w`, 'positive required');
    if (validNumber(part?.h) && part.h <= 0) fail(errors, `${base}.h`, 'positive required');
    if (part?.parent !== undefined && part.parent !== null) {
      if (!inText(part.parent)) fail(errors, `${base}.parent`, 'invalid');
      parents.set(part.id, part.parent);
    }
    if (part?.ports !== undefined) {
      if (!Array.isArray(part.ports)) fail(errors, `${base}.ports`, 'array required');
      else {
        const portIds = new Set();
        for (const port of part.ports) {
          if (!inText(port?.id) || portIds.has(port.id)) fail(errors, `${base}.ports`, 'duplicate or missing id');
          portIds.add(port?.id);
          if (!FLOW.has(port?.flow)) fail(errors, `${base}.ports.${port?.id}`, 'unknown flow type');
          if (port?.unit !== undefined && !inText(port.unit)) fail(errors, `${base}.ports.${port?.id}`, 'unit must be nonempty');
        }
      }
    }
  }
  for (const [child, parent] of parents) if (!ids.has(parent)) fail(errors, `parent.${child}`, 'unknown parent');
  const visiting = new Set(), visited = new Set();
  function cycle(id) {
    if (visiting.has(id)) { fail(errors, `parent.${id}`, 'containment cycle'); return; }
    if (visited.has(id)) return;
    visiting.add(id);
    const p = parents.get(id);
    if (p && ids.has(p)) cycle(p);
    visiting.delete(id); visited.add(id);
  }
  for (const id of ids) cycle(id);
  const partMap = new Map(parts.map(p => [p?.id, p]));
  const links = Array.isArray(scene.links) ? scene.links : [];
  if (scene.links !== undefined && !Array.isArray(scene.links)) fail(errors, 'links', 'array required');
  for (const [i, link] of links.entries()) {
    if (!ids.has(link.from) || !ids.has(link.to)) fail(errors, `links[${i}]`, 'missing endpoint');
    if (!FLOW.has(link.flow)) fail(errors, `links[${i}].flow`, 'invalid');
    if (link.fromPort !== undefined && !partMap.get(link.from)?.ports?.some(p => p.id === link.fromPort && p.flow === link.flow)) fail(errors, `links[${i}].fromPort`, 'unresolved/mismatched source port');
    if (link.toPort !== undefined && !partMap.get(link.to)?.ports?.some(p => p.id === link.toPort && p.flow === link.flow)) fail(errors, `links[${i}].toPort`, 'unresolved/mismatched target port');
  }
  const observables = Array.isArray(scene.observables) ? scene.observables : [];
  if (scene.observables !== undefined && !Array.isArray(scene.observables)) fail(errors, 'observables', 'array required');
  const obsIds = new Set();
  for (const [i, o] of observables.entries()) {
    if (!inText(o?.id) || obsIds.has(o.id)) fail(errors, `observables[${i}].id`, 'missing or duplicate');
    else obsIds.add(o.id);
    if (!validNumber(o?.value) && typeof o?.value !== 'boolean' && typeof o?.value !== 'string') fail(errors, `observables[${i}].value`, 'number, boolean, or string required');
    if (typeof o?.value === 'number' && !inText(o?.unit)) fail(errors, `observables[${i}].unit`, 'explicit unit or 1 for dimensionless');
    if (!inText(o?.source)) fail(errors, `observables[${i}].source`, 'model provenance required');
  }
  if (!inText(scene.claim?.status) || !inText(scene.claim?.interpretation)) fail(errors, 'claim', 'status and interpretation required');
  if (scene.audit && Object.values(scene.audit).some(v => !EVIDENCE.has(v))) fail(errors, 'audit', 'invalid status');
  return { ok: errors.length === 0, errors };
}
export function assertScene(scene) {
  const report = validateScene(scene);
  if (!report.ok) throw new Error(report.errors.join('\n'));
  return scene;
}
export function assertObservableAgreement(scene, actual, tolerances = {}) {
  assertScene(scene);
  const problems = [];
  for (const expected of scene.observables || []) {
    const observed = actual?.[expected.id];
    const tolerance = tolerances[expected.id] ?? 0;
    if (!validNumber(tolerance) || tolerance < 0) problems.push(`${expected.id}: invalid tolerance`);
    else if (typeof expected.value === 'number') {
      if (!validNumber(observed) || Math.abs(observed - expected.value) > tolerance) problems.push(`${expected.id}: mismatch`);
    } else if (observed !== expected.value) problems.push(`${expected.id}: mismatch`);
  }
  return { ok: problems.length === 0, problems, checked: (scene.observables || []).length };
}
