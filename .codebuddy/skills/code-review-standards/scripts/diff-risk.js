#!/usr/bin/env node
/**
 * diff-risk.js — 基于实际 diff 的变更风险分类器（OPT-R1）。
 * 扫描改动的文件路径 + 新增行内容，识别风险维度，输出：
 *   - 命中的风险维度与证据
 *   - 强制门禁建议（/security-review、/perf-check、/data-safety-check）
 *   - 审查深度（deep | standard | light）
 * 让安全/性能审查由 diff 自动触发，而非靠模型读 spec 关键词（可能漏触发）。
 *
 * 用法：node scripts/diff-risk.js [--range=A..B] [--format=md|json]
 *   默认 range：存在 origin/<默认分支> 用 三点 diff，否则 HEAD~1..HEAD。
 * 跨平台（node）、只读、纯静态分析；启发式从严（宁可多触发，不漏高危）。
 */
'use strict';
const { execSync } = require('child_process');

// 风险维度词典：path=文件路径信号，content=新增行内容信号，gate=命中后强制门禁，weight=高/中
const DIMS = {
  security: {
    label: '安全/鉴权/加密',
    gate: '/security-review', weight: 'high',
    path: /(auth|login|logout|session|oauth|sso|jwt|token|password|passwd|credential|permission|rbac|acl|crypto|cipher|encrypt|decrypt|tls|ssl|secret|vault|sign|verify)/i,
    content: /(crypto|hashlib|bcrypt|scrypt|pbkdf2|jsonwebtoken|\bjwt\b|md5|sha1\b|\bAES\b|\bRSA\b|Math\.random|secrets?\.|api[_-]?key|private[_-]?key|eval\(|exec\(|subprocess|os\.system|pickle\.|deserialize|innerHTML|dangerouslySetInnerHTML|\+\s*req\.|"\s*\+\s*.*SELECT|SELECT.*"\s*\+)/i,
  },
  data: {
    label: '数据/表结构/迁移',
    gate: '/data-safety-check', weight: 'high',
    path: /(migrat|schema|\.sql$|ddl|flyway|liquibase|alembic|entity|repositor|dao|\bmodels?\b)/i,
    content: /(DROP\s+(TABLE|DATABASE|COLUMN)|TRUNCATE|ALTER\s+TABLE|DELETE\s+FROM|UPDATE\s+\w+\s+SET(?![\s\S]*WHERE)|CREATE\s+TABLE|rm\s+-rf|kubectl\s+delete)/i,
  },
  perf: {
    label: '性能敏感（热路径/批量/查询）',
    gate: '/perf-check', weight: 'high',
    path: /(quer(y|ies)|\bdao\b|repositor|\bbatch\b|\bcron\b)/i,
    content: /(SELECT\s+.*\sJOIN|N\+1|for\s*\([^)]*\)\s*\{[\s\S]{0,80}\bawait\b|\.forEach\([\s\S]{0,80}\bawait\b|while\s*\(true\)|O\(n\^?2\)|nested\s+loop)/i,
  },
  concurrency: {
    label: '并发/异步',
    gate: null, weight: 'medium',
    path: /(thread|worker|queue|lock|mutex|concurren)/i,
    content: /(\bThread\b|goroutine|\bsync\.|Mutex|atomic\.|threading\.|asyncio|Promise\.all|parallel|race condition)/i,
  },
  externalInput: {
    label: '外部输入/接口边界',
    gate: null, weight: 'medium',
    path: /(controller|handler|route|\bapi\b|endpoint|webhook|upload)/i,
    content: /(req\.(body|params|query|headers)|request\.(form|args|json)|@RequestMapping|@PostMapping|http\.(get|post)|process\.argv|input\()/i,
  },
};
const TRIVIAL = /(\.md$|\.txt$|\.rst$|^docs\/|LICENSE|\.gitignore$|(^|\/)test|\.test\.|\.spec\.|__tests__|\.sample\.|CHANGELOG)/i;

function sh(cmd) { try { return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }); } catch (e) { return ''; } }

function resolveRange(arg) {
  if (arg) return arg;
  const def = (sh('git symbolic-ref refs/remotes/origin/HEAD').trim().split('/').pop()) || 'master';
  if (sh(`git rev-parse --verify --quiet origin/${def}`).trim()) return `origin/${def}...HEAD`;
  if (sh('git rev-parse --verify --quiet HEAD~1').trim()) return 'HEAD~1..HEAD';
  return 'HEAD';
}

function analyze(range) {
  const files = sh(`git diff --name-only ${range}`).split('\n').filter(Boolean);
  const codeFiles = files.filter(f => !TRIVIAL.test(f));
  const codeSet = new Set(codeFiles);
  const allTrivial = files.length > 0 && codeFiles.length === 0;

  // 文件感知地只取「代码文件」的新增行：文档/测试/.sample 里的 crypto、rm -rf 等是说明文本，
  // 不应触发安全/数据门禁（审查的是代码风险，不是散文）。
  const addedByCode = [];
  let cur = null;
  for (const line of sh(`git diff --unified=0 ${range}`).split('\n')) {
    const h = line.match(/^diff --git a\/(.+?) b\/(.+)$/);
    if (h) { cur = h[2]; continue; }
    if (cur && codeSet.has(cur) && line.startsWith('+') && !line.startsWith('+++')) addedByCode.push(line.slice(1));
  }
  const addedText = addedByCode.join('\n');

  const hits = {};
  for (const [dim, cfg] of Object.entries(DIMS)) {
    const ev = [];
    const pf = codeFiles.filter(f => cfg.path.test(f)); // 路径信号也只看代码文件
    if (pf.length) ev.push(...pf.slice(0, 3).map(f => `path:${f}`));
    const cm = addedText.match(cfg.content);
    if (cm) ev.push(`content:${cm[0].trim().slice(0, 40)}`);
    if (ev.length) hits[dim] = { label: cfg.label, weight: cfg.weight, gate: cfg.gate, evidence: ev };
  }

  const highHit = Object.values(hits).some(h => h.weight === 'high');
  const anyHit = Object.keys(hits).length > 0;

  let depth, rationale;
  if (allTrivial && !anyHit) { depth = 'light'; rationale = '仅文档/测试/配置类改动，无风险信号 → 快速路径'; }
  else if (highHit) { depth = 'deep'; rationale = '命中高危维度（安全/数据/性能）→ 深审 + 强制对应门禁'; }
  else if (anyHit) { depth = 'standard'; rationale = '命中中危维度（并发/外部输入）→ 标准审查并关注边界'; }
  else { depth = 'standard'; rationale = '常规代码改动，无显著高危信号 → 标准审查'; }

  const gates = [...new Set(Object.values(hits).map(h => h.gate).filter(Boolean))];
  return { range, filesChanged: files.length, codeFiles: codeFiles.length, hits, mandatoryGates: gates, reviewDepth: depth, rationale };
}

function renderMd(r) {
  const L = ['# 变更风险评估（diff-risk）', '',
    `- 范围：\`${r.range}\`　改动文件：${r.filesChanged}（代码 ${r.codeFiles}）`,
    `- **审查深度：${r.reviewDepth.toUpperCase()}** — ${r.rationale}`,
    `- **强制门禁：${r.mandatoryGates.length ? r.mandatoryGates.join('、') : '无'}**`, ''];
  L.push('## 命中的风险维度', '');
  const keys = Object.keys(r.hits);
  if (!keys.length) L.push('（无风险信号）');
  else { L.push('| 维度 | 级别 | 强制门禁 | 证据 |', '|---|---|---|---|');
    for (const [d, h] of Object.entries(r.hits))
      L.push(`| ${h.label} | ${h.weight} | ${h.gate || '—'} | ${h.evidence.join('；')} |`); }
  L.push('');
  return L.join('\n');
}

function main() {
  const args = {}; for (const t of process.argv.slice(2)) { const m = t.match(/^--([^=]+)=(.*)$/); if (m) args[m[1]] = m[2]; }
  const root = sh('git rev-parse --show-toplevel').trim(); if (root) process.chdir(root);
  const r = analyze(resolveRange(args.range));
  if (args.format === 'json') { process.stdout.write(JSON.stringify(r, null, 2) + '\n'); return; }
  process.stdout.write(renderMd(r) + '\n');
  // 退出码：deep=2（CI 可据此强制门禁），standard=0，light=0；纯供编排参考，不代表失败
  process.exit(r.reviewDepth === 'deep' ? 2 : 0);
}

main();
