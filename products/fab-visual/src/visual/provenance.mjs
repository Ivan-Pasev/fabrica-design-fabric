import { createHash } from 'node:crypto';
export function sha256(data) { return createHash('sha256').update(data).digest('hex'); }
export function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k => [k, canonicalize(value[k])]));
  if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('nonfinite value forbidden');
  return value;
}
export function canonicalJSON(value) { return JSON.stringify(canonicalize(value)); }
export function witness({scene, format, bytes, renderer='fab-visual-reference-svg', environment='node', checks={}}) {
  return {schema:'fab.visual.witness.v0.2',sourceModel:scene.model,sceneId:scene.id,sceneDigest:`sha256:${sha256(canonicalJSON(scene))}`,outputFormat:format,outputDigest:`sha256:${sha256(bytes)}`,renderer,environment,checks,claim:scene.claim,release:'HOLD'};
}
