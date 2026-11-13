import { test } from 'node:test';
import assert from 'node:assert/strict';
// Static source-equivalent miniature of upstream ripple-tank's nodal-count logic, not upstream code execution.
function nodalCount(spacing,lambda){return 2*Math.floor(spacing/lambda+0.5);}
function nodalVertices(spacing,lambda){const out=[];for(let m=0;(m+0.5)*lambda<spacing;m++)out.push((m+0.5)*lambda/2,-(m+0.5)*lambda/2);return out;}
test('known reported/readout boundary discrepancy is detected',()=>{const lambda=22.750830626733407,d=1.5*lambda; assert.equal(nodalCount(d,lambda),4);assert.equal(nodalVertices(d,lambda).length,2);assert.notEqual(nodalCount(d,lambda),nodalVertices(d,lambda).length);});
test('same-theme pages reveal lossy publication-key convention',()=>{const pages={};for(const [file,theme] of [['main.html','dark'],['alt.html','dark']])pages[theme]=file;assert.equal(Object.keys(pages).length,1);assert.equal(pages.dark,'alt.html');});
