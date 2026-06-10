#!/usr/bin/env node
/**
 * post-write-check.js — 写完即检（OPT-C3）。
 * 作为 PostToolUse hook 在每次 Edit/Write 后立即对被改文件做快速静态检查，
 * 把语法/解析错误在【写入的那一刻】反馈给 AI，而不是堆到测试/评审阶段。
 *
 * 输入：hook 协议 stdin JSON（{tool_input:{file_path}}），或退化为 argv[2] 直接传路径。
 * 输出：通过=静默退出 0；失败=stderr 给出精炼错误并退出 2（hook 协议中 stderr 会回馈给 AI）。
 * 检查矩阵（无对应工具则跳过，绝不误报）：
 *   .js/.mjs/.cjs → node --check        .json → JSON.parse
 *   .sh           → bash -n（无 bash 跳过，如 Windows）
 *   .py           → python -m py_compile（无 python 跳过）
 * 设计原则：快（单文件、纯语法层）、稳（任何意外都退 0 不挡路）、跨平台。
 */
'use strict';
const { spawnSync } = require('child_process');
const fs = require('fs');

function readStdin() {
  try {
    if (process.stdin.isTTY) return '';
    return fs.readFileSync(0, 'utf8');
  } catch (e) { return ''; }
}

function resolveFile() {
  const arg = process.argv[2];
  if (arg && !arg.startsWith('-')) return arg;
  const raw = readStdin();
  if (!raw) return null;
  try {
    const j = JSON.parse(raw);
    return (j.tool_input && (j.tool_input.file_path || j.tool_input.notebook_path)) || null;
  } catch (e) { return null; }
}

function has(cmd) {
  const probe = process.platform === 'win32' ? 'where' : 'which';
  return spawnSync(probe, [cmd], { stdio: 'ignore' }).status === 0;
}

function fail(msg) {
  process.stderr.write(`[instant-check] ${msg}\n`);
  process.exit(2);
}

function main() {
  const file = resolveFile();
  if (!file || !fs.existsSync(file)) process.exit(0);
  // 运行态/产物目录不检查
  if (/\.codebuddy-runtime|node_modules|\.git\//.test(file)) process.exit(0);

  const ext = (file.match(/\.[^.]+$/) || [''])[0].toLowerCase();

  if (['.js', '.mjs', '.cjs'].includes(ext)) {
    const r = spawnSync(process.execPath, ['--check', file], { encoding: 'utf8' });
    if (r.status !== 0) fail(`JS 语法错误 ${file}:\n${(r.stderr || '').split('\n').slice(0, 6).join('\n')}`);
  } else if (ext === '.json') {
    try { JSON.parse(fs.readFileSync(file, 'utf8')); }
    catch (e) { fail(`JSON 解析失败 ${file}: ${e.message}`); }
  } else if (ext === '.sh') {
    if (has('bash')) {
      const r = spawnSync('bash', ['-n', file], { encoding: 'utf8' });
      if (r.status !== 0) fail(`Shell 语法错误 ${file}:\n${(r.stderr || '').split('\n').slice(0, 6).join('\n')}`);
    }
  } else if (ext === '.py') {
    const py = has('python3') ? 'python3' : (has('python') ? 'python' : null);
    if (py) {
      const r = spawnSync(py, ['-m', 'py_compile', file], { encoding: 'utf8' });
      if (r.status !== 0) fail(`Python 语法错误 ${file}:\n${(r.stderr || '').split('\n').slice(0, 6).join('\n')}`);
    }
  }
  process.exit(0);
}

try { main(); } catch (e) { process.exit(0); /* 检查器自身异常不挡路 */ }
