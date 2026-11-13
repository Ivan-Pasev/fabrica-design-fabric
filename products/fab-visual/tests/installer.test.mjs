import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, existsSync, rmSync, mkdirSync, symlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
const script=resolve('scripts/install-codexstation.mjs');
test('installer dry-run does not modify release directory',()=>{const root=mkdtempSync(join(tmpdir(),'fabvisual-install-'));try{const run=spawnSync(process.execPath,[script,'--root',root],{encoding:'utf8'});assert.equal(run.status,0,run.stderr);assert.equal(existsSync(join(root,'.agents')),false);assert.match(run.stdout,/DRY_RUN/);}finally{rmSync(root,{recursive:true,force:true})}});
test('installer applies only opt-in extension, never overwrites',()=>{const root=mkdtempSync(join(tmpdir(),'fabvisual-install-'));try{const a=spawnSync(process.execPath,[script,'--root',root,'--apply'],{encoding:'utf8'});assert.equal(a.status,0,a.stderr);assert.equal(existsSync(join(root,'.agents/skills/fab-visual/SKILL.md')),true);const b=spawnSync(process.execPath,[script,'--root',root,'--apply'],{encoding:'utf8'});assert.equal(b.status,2);assert.match(b.stderr,/HOLD_COLLISION/);}finally{rmSync(root,{recursive:true,force:true})}});

test('installer does not follow an extension-root symlink',()=>{const root=mkdtempSync(join(tmpdir(),'fabvisual-symlink-'));const elsewhere=mkdtempSync(join(tmpdir(),'fabvisual-elsewhere-'));try{symlinkSync(elsewhere,join(root,'.agents'));const run=spawnSync(process.execPath,[script,'--root',root,'--apply'],{encoding:'utf8'});assert.notEqual(run.status,0);assert.equal(existsSync(join(elsewhere,'skills')),false);}finally{rmSync(root,{recursive:true,force:true});rmSync(elsewhere,{recursive:true,force:true})}});
