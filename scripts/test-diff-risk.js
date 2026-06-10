#!/usr/bin/env node
/**
 * test-diff-risk.js — diff-risk.js 的回归单测。
 * 在临时 git 仓库里构造各类变更，断言风险维度/深度/强制门禁分类正确。
 */
'use strict';
const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const SCRIPT = path.join(__dirname, 'diff-risk.js');
let pass = 0, fail = 0;

function run(files) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dr-'));
  const sh = (c) => execSync(c, { cwd: dir, stdio: ['ignore', 'pipe', 'ignore'] });
  sh('git init -q .');
  sh('git config user.email t@t'); sh('git config user.name t'); sh('git config commit.gpgsign false');
  fs.writeFileSync(path.join(dir, 'README.md'), 'base\n');
  sh('git add -A'); sh('git commit -qm "[AI-0] chore: base"');
  for (const [f, body] of Object.entries(files)) {
    const fp = path.join(dir, f);
    fs.mkdirSync(path.dirname(fp), { recursive: true });
    fs.writeFileSync(fp, body);
  }
  sh('git add -A'); sh('git commit -qm "[AI-H] feat: change"');
  const out = execSync(`node ${SCRIPT} --range=HEAD~1..HEAD --format=json`, { cwd: dir, encoding: 'utf8' });
  fs.rmSync(dir, { recursive: true, force: true });
  return JSON.parse(out);
}

function check(name, r, { depth, gates = [], dims = [] }) {
  const errs = [];
  if (r.reviewDepth !== depth) errs.push(`depth ${r.reviewDepth}≠${depth}`);
  for (const g of gates) if (!r.mandatoryGates.includes(g)) errs.push(`缺门禁 ${g}`);
  for (const d of dims) if (!r.hits[d]) errs.push(`未命中维度 ${d}`);
  if (errs.length) { console.log(`FAIL ${name}: ${errs.join('; ')}`); fail++; }
  else { console.log(`OK   ${name} (${depth}${gates.length ? ' ' + gates.join(',') : ''})`); pass++; }
}

// 1. 鉴权改动 → deep + /security-review
check('auth+jwt', run({ 'src/auth/login.js': 'const jwt=require("jsonwebtoken");\nfunction sign(u){return jwt.sign(u,KEY);}\n' }),
  { depth: 'deep', gates: ['/security-review'], dims: ['security'] });

// 2. 迁移/DDL → deep + /data-safety-check
check('migration-ddl', run({ 'db/migrations/001_drop.sql': 'DROP TABLE users;\n' }),
  { depth: 'deep', gates: ['/data-safety-check'], dims: ['data'] });

// 3. 查询/仓储层 → deep + /perf-check
check('repository-query', run({ 'src/repository/userQuery.js': 'function all(){ return db.query("SELECT u.* FROM users u JOIN org o ON o.id=u.org"); }\n' }),
  { depth: 'deep', gates: ['/perf-check'], dims: ['perf'] });

// 4. 纯文档 → light，无门禁
check('docs-only', run({ 'docs/guide.md': '# 指南\n内容\n' }),
  { depth: 'light', gates: [] });

// 5. 普通工具代码 → standard，无门禁
check('plain-util', run({ 'src/util/add.js': 'module.exports=(a,b)=>a+b;\n' }),
  { depth: 'standard', gates: [] });

// 6. 外部输入 handler → standard（中危，无强制门禁但抬深度关注边界）
check('external-input', run({ 'src/web/userController.js': 'app.post("/u",(req,res)=>{ const n=req.body.name; res.json({n}); });\n' }),
  { depth: 'standard', dims: ['externalInput'] });

// 7. 多维高危叠加 → deep + 多门禁
check('multi-high', run({
  'src/auth/token.js': 'const crypto=require("crypto");\nfunction t(){return crypto.randomBytes(16);}\n',
  'db/migrate/002.sql': 'ALTER TABLE accounts ADD COLUMN balance int;\n',
}), { depth: 'deep', gates: ['/security-review', '/data-safety-check'], dims: ['security', 'data'] });

console.log(`\ntest-diff-risk: pass=${pass} fail=${fail}`);
process.exit(fail === 0 ? 0 : 1);
