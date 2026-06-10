#!/usr/bin/env node
/**
 * metrics.js — 交付效能度量 Tier 0 聚合器（只读，纯聚合现有产物，无副作用）。
 * 设计见 docs/specs/2026-06-09-delivery-metrics-design.md。
 *
 * 数据源（缺失即标 N/A，不阻断其余）：
 *   - git 历史：AI 标签分布 / 提交类型构成 / 规范合规率 / 提交节奏
 *   - docs/quality/last-quality-gate.json, test-summary.json：门禁与测试
 *   - jobs.jsonl（接收器台账，--jobs 指定或默认探测）：自动化成功率/超时率/耗时
 *   - docs/pending-decisions.md：决策挂起时效
 *
 * 用法：node scripts/metrics.js [--since=YYYY-MM-DD] [--format=md|json]
 *                               [--out=<path>] [--jobs=<path/to/jobs.jsonl>]
 * 选 node 而非 shell：跨平台（含 Windows）、原生解析 JSON、免 jq 依赖。
 */
'use strict';
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const TYPES = ['feat', 'fix', 'docs', 'refactor', 'test', 'chore', 'perf', 'build', 'ci', 'revert'];
const AI_TAGS = ['AI-0', 'AI-H', 'AI-100'];

function parseArgs(argv) {
  const a = { format: 'md' };
  for (const t of argv.slice(2)) {
    const m = t.match(/^--([^=]+)=(.*)$/);
    if (m) a[m[1]] = m[2];
    else if (t.startsWith('--')) a[t.slice(2)] = true;
  }
  if (!a.since) {
    const d = new Date(Date.now() - 30 * 864e5);
    a.since = d.toISOString().slice(0, 10);
  }
  return a;
}

function sh(cmd) {
  try { return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }); }
  catch (e) { return ''; }
}

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { return null; }
}

function pct(n, d) { return d > 0 ? Math.round((n / d) * 1000) / 10 : 0; }

function quantile(sorted, q) {
  if (!sorted.length) return null;
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  return sorted[base + 1] !== undefined
    ? Math.round(sorted[base] + rest * (sorted[base + 1] - sorted[base]))
    : Math.round(sorted[base]);
}

function daysAgo(iso) {
  const t = Date.parse(iso);
  return Number.isNaN(t) ? null : Math.round((Date.now() - t) / 864e5);
}

// ── git 交付活动 ──
function gitMetrics(since) {
  const SEP = '';
  const raw = sh(`git log --no-merges --since=${since} --pretty=%s${SEP}%aI`);
  const lines = raw.split('\n').filter(Boolean);
  const tags = { 'AI-0': 0, 'AI-H': 0, 'AI-100': 0, none: 0 };
  const types = {}; TYPES.forEach(t => { types[t] = 0; }); types.other = 0;
  const weeks = {};
  let compliant = 0;
  for (const ln of lines) {
    const [subject, iso] = ln.split(SEP);
    const tagMatches = (subject.match(/\[AI-(0|H|100)\]/g) || []);
    const oneTag = tagMatches.length === 1;
    if (oneTag) tags['AI-' + tagMatches[0].slice(4, -1)] += 1; else tags.none += 1;
    const rest = subject.replace(/^\[AI-(0|H|100)\]\s+/, '');
    const typeM = rest.match(/^(\w+)(\([^)]+\))?:/);
    const ticketM = rest.match(/^AC\d+:/);
    let type = 'other';
    if (typeM && TYPES.includes(typeM[1])) type = typeM[1];
    types[type] += 1;
    if (oneTag && /^\[AI-(0|H|100)\] /.test(subject) && (ticketM || (typeM && TYPES.includes(typeM[1])))) compliant += 1;
    if (iso) {
      const d = new Date(iso);
      const onejan = new Date(d.getFullYear(), 0, 1);
      const wk = `${d.getFullYear()}-W${String(Math.ceil(((d - onejan) / 864e5 + onejan.getDay() + 1) / 7)).padStart(2, '0')}`;
      weeks[wk] = (weeks[wk] || 0) + 1;
    }
  }
  return { total: lines.length, tags, types, compliant, complianceRate: pct(compliant, lines.length), weeks };
}

// ── 质量门禁 / 测试 ──
function qualityMetrics() {
  const gate = readJson('docs/quality/last-quality-gate.json');
  const test = readJson('docs/quality/test-summary.json');
  if (!gate && !test) return null;
  const cov = test && (typeof test.coverage === 'number' ? test.coverage
    : test.coverage && (test.coverage.branches ?? test.coverage.statements));
  return {
    gate: gate && { status: gate.status, passRate: gate.passRate, coverage: gate.coverage,
      coverageThreshold: gate.coverageThreshold, docSyncStatus: gate.docSyncStatus,
      checkedAt: gate.checkedAt, staleDays: gate.checkedAt ? daysAgo(gate.checkedAt) : null },
    test: test && { total: test.total, passed: test.passed, passRate: test.passRate, coverage: cov },
  };
}

// ── 自动化 ROI（jobs.jsonl）──
function jobsMetrics(jobsPath) {
  const candidates = jobsPath ? [jobsPath]
    : ['.webhook-receiver-state/jobs.jsonl', 'jobs.jsonl', '.codebuddy-runtime/jobs.jsonl'];
  const file = candidates.find(p => fs.existsSync(p));
  if (!file) return null;
  const byCmd = {};
  for (const ln of fs.readFileSync(file, 'utf8').split('\n').filter(Boolean)) {
    let e; try { e = JSON.parse(ln); } catch (x) { continue; }
    if (e.ev !== 'end') continue;
    const c = e.command || '(unknown)';
    byCmd[c] = byCmd[c] || { runs: 0, ok: 0, timeout: 0, ms: [] };
    byCmd[c].runs += 1;
    if (e.timedOut) byCmd[c].timeout += 1;
    else if (e.code === 0) byCmd[c].ok += 1;
    if (typeof e.ms === 'number') byCmd[c].ms.push(e.ms);
  }
  const rows = Object.entries(byCmd).map(([cmd, v]) => {
    const s = v.ms.slice().sort((a, b) => a - b);
    return { cmd, runs: v.runs, okRate: pct(v.ok, v.runs), timeoutRate: pct(v.timeout, v.runs),
      p50: quantile(s, 0.5), p95: quantile(s, 0.95) };
  }).sort((a, b) => b.runs - a.runs);
  return { file, rows };
}

// ── 决策时效 ──
function pendingMetrics() {
  const p = 'docs/pending-decisions.md';
  if (!fs.existsSync(p)) return null;
  const txt = fs.readFileSync(p, 'utf8');
  const count = (re) => (txt.match(re) || []).length;
  return { pending: count(/status\s*[:=]\s*pending/gi), partial: count(/status\s*[:=]\s*partial/gi) };
}

function frictionPoints(m) {
  const out = [];
  if (m.git && m.git.total - m.git.compliant > 0)
    out.push(`提交规范：${m.git.total - m.git.compliant}/${m.git.total} 条不合规（缺/多 AI 标签或类型非法）`);
  if (m.quality && m.quality.gate && m.quality.gate.staleDays != null && m.quality.gate.staleDays > 14)
    out.push(`门禁数据过期：last-quality-gate.json checkedAt 距今 ${m.quality.gate.staleDays} 天，可能不反映当前状态`);
  if (m.quality && m.quality.gate && m.quality.gate.status && m.quality.gate.status !== 'pass')
    out.push(`质量门禁未通过：status=${m.quality.gate.status}`);
  if (m.jobs) {
    const worst = m.jobs.rows.filter(r => r.timeoutRate > 0).sort((a, b) => b.timeoutRate - a.timeoutRate)[0];
    if (worst) out.push(`自动化超时：${worst.cmd} 超时率 ${worst.timeoutRate}%（${worst.runs} 次）`);
  }
  if (m.pending && (m.pending.pending + m.pending.partial) > 0)
    out.push(`决策挂起：${m.pending.pending} 项 pending、${m.pending.partial} 项 partial 未收敛`);
  return out;
}

function renderMd(m) {
  const L = [];
  L.push(`# 交付效能度量报告`, '');
  L.push(`- 窗口：自 ${m.since}（约 ${daysAgo(m.since + 'T00:00:00Z')} 天）`);
  L.push(`- 生成：${m.generatedAt}`);
  L.push(`- 口径：Tier 0（仅聚合现有产物，无新埋点；逃逸率/接受率等精确值待 Tier 1）`, '');

  L.push('## ⚠️ Top 摩擦点', '');
  const fp = frictionPoints(m);
  if (fp.length) fp.forEach((x, i) => L.push(`${i + 1}. ${x}`)); else L.push('（无显著摩擦点）');
  L.push('');

  L.push('## 1. 交付活动（git）', '');
  if (m.git && m.git.total) {
    const g = m.git;
    L.push(`- 提交数（不含 merge）：**${g.total}**　规范合规率：**${g.complianceRate}%**（${g.compliant}/${g.total}）`);
    L.push(`- 自动化结构（AI 标签）：AI-100 ${g.tags['AI-100']} ｜ AI-H ${g.tags['AI-H']} ｜ AI-0 ${g.tags['AI-0']} ｜ 无标签 ${g.tags.none}`);
    const typeStr = Object.entries(g.types).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1])
      .map(([k, v]) => `${k} ${v}`).join(' ｜ ');
    L.push(`- 变更类型：${typeStr}`);
    const wkStr = Object.entries(g.weeks).sort().map(([k, v]) => `${k}:${v}`).join('  ');
    L.push(`- 提交节奏（按周）：${wkStr || 'N/A'}`);
  } else { L.push('N/A（窗口内无提交）'); }
  L.push('');

  L.push('## 2. 质量门禁 / 测试', '');
  if (m.quality) {
    const q = m.quality;
    if (q.gate) L.push(`- 门禁：status=**${q.gate.status}**　passRate=${q.gate.passRate}%　coverage=${q.gate.coverage}（阈值 ${q.gate.coverageThreshold}）　docSync=${q.gate.docSyncStatus}　checkedAt=${q.gate.checkedAt}${q.gate.staleDays != null ? `（${q.gate.staleDays} 天前）` : ''}`);
    if (q.test) L.push(`- 测试：${q.test.passed}/${q.test.total} 通过（${q.test.passRate}%），coverage=${q.test.coverage}`);
  } else { L.push('N/A（无 docs/quality/*.json）'); }
  L.push('');

  L.push('## 3. 自动化 ROI（jobs.jsonl）', '');
  if (m.jobs) {
    L.push(`数据源：\`${m.jobs.file}\``, '');
    L.push('| 命令 | 次数 | 成功率 | 超时率 | p50(ms) | p95(ms) |', '|---|---|---|---|---|---|');
    m.jobs.rows.forEach(r => L.push(`| ${r.cmd} | ${r.runs} | ${r.okRate}% | ${r.timeoutRate}% | ${r.p50 ?? '-'} | ${r.p95 ?? '-'} |`));
  } else { L.push('N/A（无 jobs.jsonl；该指标在已接事件/定时触发的业务项目才有）'); }
  L.push('');

  L.push('## 4. 决策时效（pending-decisions）', '');
  L.push(m.pending ? `- pending ${m.pending.pending} 项 ｜ partial ${m.pending.partial} 项`
    : 'N/A（无 docs/pending-decisions.md）');
  L.push('');
  return L.join('\n');
}

function main() {
  const a = parseArgs(process.argv);
  // 确保在仓库根运行
  const root = sh('git rev-parse --show-toplevel').trim();
  if (root) process.chdir(root);
  const m = {
    since: a.since,
    generatedAt: new Date().toISOString(),
    git: gitMetrics(a.since),
    quality: qualityMetrics(),
    jobs: jobsMetrics(a.jobs),
    pending: pendingMetrics(),
  };
  if (a.format === 'json') {
    const out = JSON.stringify(m, null, 2);
    if (a.out) fs.writeFileSync(a.out, out);
    process.stdout.write(out + '\n');
    return;
  }
  const md = renderMd(m);
  const out = a.out || `docs/quality/metrics-${new Date().toISOString().slice(0, 10)}.md`;
  try { fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, md); }
  catch (e) { /* 只读环境则仅打印 */ }
  process.stdout.write(md + `\n\n> 已写入 ${out}\n`);
}

main();
