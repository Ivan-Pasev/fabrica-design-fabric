import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {verifyAnatomyBlobs} from '../src/adapters/anatomy-kernel.mjs';
import {auditQuantitativeContract} from '../src/visual/quantitative-audit.mjs';

const read=path=>readFileSync(new URL(path,import.meta.url),'utf8');
const manifest=JSON.parse(read('../agents/capability-manifest.v1.json'));
const scenario=JSON.parse(read('../fixtures/quantitative-microgrid.synthetic.json'));
const root=fileURLToPath(new URL('../',import.meta.url));

test('Ω11O public one-link IDE bootstrap exists and explicit feature branch is identified',()=>{
 const entry=read('../../../IDE_START_HERE_FAB_VISUAL.md');
 assert.match(entry,/feature\/fab-visual-omega11o-ide-science-skill/);
 assert.match(entry,/IDE_BOOTSTRAP/);
 assert.match(entry,/READ\/REASON\/VERIFY/);
 assert.match(entry,/user.*explicit|explicit.*user/i);
 assert.match(entry,/does not.*plugin|does not.*installation/i);
});
test('portable Agent Skills frontmatter exists, named and scoped for human review',()=>{
 const a=read('../../../skills/fab-visual-ide/SKILL.md');
 const b=read('../skills/fab-visual/SKILL.md');
 for(const skill of [a,b]){
   assert.match(skill,/^---\nname: fab-visual(?:-ide)?\n/);
   assert.match(skill,/\nlicense: MIT\n/);
   assert.match(skill,/HOLD/);
   assert.match(skill,/Anatomy/);
 }
 assert.match(a,/read-only/i);
 assert.match(b,/audit-quantitative/);
});
test('VS Code Copilot path-scoped instructions and nested AGENTS do not grant permissions',()=>{
 const p=read('../../../.github/instructions/fab-visual.instructions.md');
 assert.match(p,/^---\napplyTo: "products\/fab-visual\/\*\*"/);
 assert.match(p,/no autonomous install/i);
 const agents=read('../AGENTS.md');
 assert.match(agents,/never clone|Never clone/i);
 assert.match(agents,/read-only/i);
});
test('root agent and constitution retain stronger host authority and release HOLD',()=>{
 const rootAgents=read('../../../AGENTS.md');
 const constitution=read('../CONSTITUTION.md');
 assert.match(rootAgents,/review-only/i);
 assert.match(rootAgents,/IDE_START_HERE_FAB_VISUAL.md/);
 assert.match(constitution,/IDE_REFERENCE_IS_NOT_INSTALLATION/);
 assert.match(constitution,/DIMENSIONS_BEFORE_EQUATIONS/);
 assert.match(constitution,/RELEASE_IS_FAIL_CLOSED/);
});
test('machine-readable capability manifest reports exact pin, five blobs and future suite NOT_RUN',()=>{
 assert.equal(manifest.schema,'fab.visual.ide-capability-manifest.v1');
 assert.equal(manifest.release,'HOLD');
 assert.equal(manifest.source.originalAnatomy.commit,'1482e8469b0a9e0d8cc18ea2740a01423d29ae80');
 assert.equal(manifest.source.originalAnatomy.originalGitSourceBlobs,173);
 assert.equal(manifest.source.originalAnatomy.vendoredOriginalBlobs,5);
 assert.equal(manifest.source.originalAnatomy.executedFullUpstreamSuite,'NOT_RUN');
 assert.equal(verifyAnatomyBlobs().ok,true);
});
test('manifest claims real GPU, science and privileged install unavailable',()=>{
 const status=Object.fromEntries(manifest.capabilities.map(c=>[c.id,c.status]));
 assert.equal(status['anatomy-complete-webgl-3d'],'NOT_RUN');
 assert.equal(status['physical-scientific-certification'],'NOT_RUN');
 assert.equal(status['host-autonomy'],'NOT_AUTHORIZED');
 assert.equal(manifest.reasoningDefaults.mode,'READ_ONLY');
 assert.equal(manifest.reasoningDefaults.release,'HOLD');
});
test('public main root README warning is present on unmerged feature branch',()=>{
 const readme=read('../../../README.md');
 assert.match(readme,/main.*review-only|review-only.*main/s);
 assert.match(readme,/IDE_START_HERE_FAB_VISUAL.md/);
});
test('human mathematical and agent intelligence documents include exact proof ceiling',()=>{
 const math=read('../docs/MATH_LOGIC_PHYSICS_BOUNDARIES_OMEGA11O.md');
 const ide=read('../docs/IDE_AUTONOMY_CONTRACT_OMEGA11O.md');
 for(const s of [math,ide]){
   assert.match(s,/NOT_RUN/);
   assert.match(s,/HOLD/);
   assert.match(s,/source/i);
 }
 assert.match(math,/POWER/);
 assert.match(math,/triangle-inequality/i);
 assert.match(math,/R³ to R²|3D_TO_2D|R. to R./);
 assert.match(ide,/no execution|execution permission|host authorization/i);
});
test('public agent bootstrap never executes source or asks for secrets by itself',()=>{
 const s=read('../../../IDE_START_HERE_FAB_VISUAL.md');
 assert.doesNotMatch(s,/\bcurl\b\s+.*\|\s*(?:bash|sh)\b/);
 assert.doesNotMatch(s,/--force\s+push/);
 assert.match(s,/never install|Never install/i);
 assert.match(s,/explicit.*approval|approval.*explicit/i);
});
test('science sidecar cannot embed a certified approval as an unreviewed top-level field',()=>{
 const s=structuredClone(scenario);
 s.scientificCertification='PASS';
 assert.throws(()=>auditQuantitativeContract(s),/unreviewed top-level claims/);
});
test('source authority field cannot be promoted through unreviewed key',()=>{
 const s=structuredClone(scenario);
 s.source.publisherApproved=true;
 assert.throws(()=>auditQuantitativeContract(s),/unknown source authority/);
});
test('signed IN/OUT rates have nonnegative finite magnitudes; no hidden double sign',()=>{
 const s=structuredClone(scenario);
 s.balances[0].terms[0].value=-7;
 assert.throws(()=>auditQuantitativeContract(s),/finite signed contributions/);
});
test('unknown meta fields on term/balance are rejected instead of ignored',()=>{
 const a=structuredClone(scenario);
 a.balances[0].approvedBy='AI';
 assert.throws(()=>auditQuantitativeContract(a),/unknown numerical balance claim/);
 const b=structuredClone(scenario);
 b.balances[0].terms[0].physicalCert='PASS';
 assert.throws(()=>auditQuantitativeContract(b),/unknown term authority/);
});
test('CLI help presents numerical auditor without ever claiming release',()=>{
 const x=spawnSync(process.execPath,['bin/fab-visual.mjs','help'],{cwd:root,encoding:'utf8'});
 assert.equal(x.status,0,x.stderr);
 assert.match(x.stdout,/audit-quantitative/);
 assert.doesNotMatch(x.stdout,/ELIGIBLE_FOR_AUTHORIZED_RELEASE/);
});
