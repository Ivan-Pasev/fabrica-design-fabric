import test from 'node:test';
import assert from 'node:assert/strict';
import {gitBlobSha, parseLsTree, GROUPS, EXPECTED_BLOBS, EXPECTED_BYTES, inspectFullAnatomy, PIN, TREE_PIN} from '../scripts/full-anatomy-source.mjs';
test('Git blob hash matches canonical MIT upstream text',()=>{
  assert.equal(gitBlobSha(Buffer.from('hello')),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0');
});
test('Git tree parser requires canonical tracked blob record',()=>{
  assert.deepEqual(parseLsTree('100644 blob 0123456789abcdef0123456789abcdef01234567 3\ta.txt'),[{path:'a.txt',sha:'0123456789abcdef0123456789abcdef01234567',size:3}]);
  assert.deepEqual(parseLsTree('100644 blob 0123456789abcdef0123456789abcdef01234567      89\t.gitattributes'),[{path:'.gitattributes',sha:'0123456789abcdef0123456789abcdef01234567',size:89}]);
  assert.throws(()=>parseLsTree('160000 commit abc -\tkit'),/unexpected upstream/);
});
test('full-source invariants are explicit and complete',()=>{
  assert.equal(EXPECTED_BLOBS,173);assert.equal(EXPECTED_BYTES,27648351);assert.equal(PIN.length,40);assert.equal(TREE_PIN.length,40);
  for(const group of ['skill','svg','audit','webgl','react','beta3d','canvas','print','publish','browser','references','cases'])assert.ok(GROUPS[group].length);
});
test('missing full source cannot be asserted as PASS',()=>{
  const r=inspectFullAnatomy({root:'/definitely-not-an-upstream-git-checkout'});
  assert.equal(r.status,'BLOCKED_NO_FULL_CHECKOUT');assert.equal(r.executedOriginalTests,false);
});
