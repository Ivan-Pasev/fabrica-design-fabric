import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
const mandatory = ['source', 'state', 'observables', 'geometry', 'accessibility', 'security'];
const states = new Set(['PASS', 'FAIL', 'NOT_RUN', 'INCONCLUSIVE', 'EXCEPTION']);
const representations = new Set(['PHYSICAL', 'ANALOGICAL', 'FORMAL']);
export function gate(artifact) {
  const violations = [];
  if (artifact.schema_version !== 'fab.visual.v0.1') violations.push('Unsupported schema version');
  if (!artifact.id || typeof artifact.id !== 'string') violations.push('Missing artifact id');
  if (!representations.has(artifact.representation)) violations.push('Invalid representation');
  if (!artifact.model?.id || !artifact.model?.revision || !artifact.model?.authority) violations.push('Unresolved model authority');
  if (!artifact.claims || !artifact.claims.status || typeof artifact.claims.scientifically_validated !== 'boolean') violations.push('Missing explicit claim boundary');
  if (artifact.claims?.status === 'CERTIFIED' && !artifact.claims?.scientifically_validated) violations.push('Certified claim lacks scientific validation');
  if (artifact.representation === 'ANALOGICAL' && artifact.claims?.scientifically_validated) violations.push('Analogy cannot self-certify science');
  for (const key of mandatory) {
    const value = artifact.evidence?.[key];
    if (!states.has(value)) violations.push(`${key}: invalid or missing evidence status`);
    else if (value !== 'PASS') violations.push(`${key}: ${value}`);
  }
  if (!artifact.provenance?.upstream_commit || !artifact.provenance?.license) violations.push('Source provenance incomplete');
  return { status: violations.length ? 'BLOCKED' : 'ELIGIBLE_FOR_AUTHORIZED_RELEASE', violations };
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const path = process.argv[2];
  if (!path) throw new Error('usage: node src/gate.mjs manifest.json');
  const artifact = JSON.parse(readFileSync(path, 'utf8'));
  const report = gate(artifact);
  console.log(JSON.stringify(report, null, 2));
  process.exitCode = report.status === 'BLOCKED' ? 2 : 0;
}
