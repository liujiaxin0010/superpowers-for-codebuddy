#!/usr/bin/env node
/**
 * stage-event.js — 阶段计时埋点（追加一条事件到 stage-events.jsonl）。
 * 供 /metrics §6 各阶段周期时间消费。只追加、无副作用、跨平台。
 *
 * 用法：
 *   node scripts/stage-event.js <phase> <start|end> [--task=<id>] [--out=<jsonl>]
 *   phase 建议取流程阶段名：spec | plan | execute | test | review | release
 * 例：
 *   node scripts/stage-event.js execute start --task=REQ-42
 *   node scripts/stage-event.js execute end   --task=REQ-42
 *
 * 默认写 .codebuddy-runtime/stage-events.jsonl（运行态目录，不入库）。
 * 接入方式（择一）：① 在命令 runbook 起止步骤各调一次；② 配 CodeBuddy hook 在命令前后触发。
 */
'use strict';
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const phase = args[0];
const event = args[1];
const opt = {};
for (const t of args.slice(2)) {
  const m = t.match(/^--([^=]+)=(.*)$/);
  if (m) opt[m[1]] = m[2];
}

if (!phase || !['start', 'end'].includes(event)) {
  console.error('usage: stage-event.js <phase> <start|end> [--task=<id>] [--out=<jsonl>]');
  process.exit(2);
}

const out = opt.out || '.codebuddy-runtime/stage-events.jsonl';
const rec = { ts: new Date().toISOString(), phase, event, task: opt.task || '' };

try {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.appendFileSync(out, JSON.stringify(rec) + '\n');
  console.log(`[stage-event] ${phase} ${event}${opt.task ? ' task=' + opt.task : ''} -> ${out}`);
} catch (e) {
  console.error('[stage-event] write failed:', e.message);
  process.exit(1);
}
