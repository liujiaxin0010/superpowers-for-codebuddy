#!/usr/bin/env node
/**
 * test-post-write-check.js — post-write-check.js（写完即检）回归单测。
 * 覆盖：好/坏 JS、好/坏 JSON、坏 Shell、stdin hook 协议、argv 直传、缺失文件。
 */
'use strict';
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const SCRIPT = path.join(__dirname, '..', '.codebuddy', 'skills', 'instant-check', 'scripts', 'post-write-check.js');
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'iwc-'));
let pass = 0, fail = 0;

function viaArgv(file) {
  return spawnSync(process.execPath, [SCRIPT, file], { encoding: 'utf8' });
}
function viaStdin(file) {
  return spawnSync(process.execPath, [SCRIPT], { input: JSON.stringify({ tool_input: { file_path: file } }), encoding: 'utf8' });
}
function check(name, r, expect) {
  if (r.status === expect) { console.log(`OK   ${name} (exit=${r.status})`); pass++; }
  else { console.log(`FAIL ${name}: exit=${r.status}≠${expect} stderr=${(r.stderr || '').slice(0, 80)}`); fail++; }
}
function w(name, body) { const p = path.join(TMP, name); fs.writeFileSync(p, body); return p; }

check('good-js/argv', viaArgv(w('a.js', 'const x=1;\n')), 0);
check('bad-js/argv', viaArgv(w('b.js', 'const x = {;\n')), 2);
check('good-json/stdin', viaStdin(w('c.json', '{"a":1}\n')), 0);
check('bad-json/stdin', viaStdin(w('d.json', '{a:1}\n')), 2);
check('bad-js/stdin', viaStdin(w('e.js', 'function (){\n')), 2);
check('bad-sh/argv', viaArgv(w('f.sh', 'if [ 1 ]; then\n')), 2);   // 无 bash 环境会退 0，CI(ubuntu) 有 bash
check('md-skip', viaArgv(w('g.md', '# 随便写\n')), 0);
check('missing-file', viaArgv(path.join(TMP, 'nope.js')), 0);
// 运行态目录豁免：里面即使是坏 JS 也放行
fs.mkdirSync(path.join(TMP, '.codebuddy-runtime'), { recursive: true });
check('runtime-dir-skip', viaArgv(w(path.join('.codebuddy-runtime', 'bad.js'), 'const x = {;\n')), 0);
// stdin 给垃圾不崩
check('garbage-stdin', spawnSync(process.execPath, [SCRIPT], { input: 'not-json', encoding: 'utf8' }), 0);

fs.rmSync(TMP, { recursive: true, force: true });
console.log(`\ntest-post-write-check: pass=${pass} fail=${fail}`);
process.exit(fail === 0 ? 0 : 1);
