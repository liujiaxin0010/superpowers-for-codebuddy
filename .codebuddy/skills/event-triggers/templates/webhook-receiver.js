#!/usr/bin/env node
/**
 * event-triggers webhook receiver (REFERENCE implementation).
 * TEMPLATE_VERSION: 1.1.0  (升级对照见引擎仓库根目录 CHANGELOG.md，或跑 /upgrade-check)
 *
 * Receives GitLab webhook events, validates the secret token, maps a small
 * ALLOWLIST of triggers (MR comments like "/code-review", labels like
 * "ai:review", pipeline failures) to Featureflow commands, and dispatches
 * them to the CodeBuddy CLI. This replaces scheduled-automation polling with
 * event-driven triggering.
 *
 * v1.1.0 unattended-ops hardening:
 *   - per-job timeout watchdog: kills the CLI process group and records it,
 *     so a stuck confirmation can never hang a job forever (the 3h-hang class)
 *   - bounded concurrency with a FIFO queue (comment storms can't fork-bomb)
 *   - persistent dedupe store (survives restarts, capped)
 *   - jsonl job ledger: one line per start/end, with exit code & duration
 *
 * This is a REFERENCE — run it on the same intranet host as the CodeBuddy CLI,
 * behind systemd/pm2 (Windows: NSSM / pm2-windows) and a reverse proxy,
 * reachable only from the internal GitLab. Harden (TLS, rate limiting) for
 * your env.
 *
 * Config : event-triggers.config.json  (see event-triggers.config.sample.json)
 * Env    : GITLAB_WEBHOOK_SECRET (required), CODEBUDDY_CLI (optional override)
 *          EVENT_CONFIG (optional path to config), PORT (optional)
 *          CODEBUDDY_SETTINGS (optional: automation-settings.json for unattended runs)
 *          CODEBUDDY_FLAGS (optional: CLI flags, default "-p"; set "-p -y" to approve all)
 */
'use strict';
const http = require('http');
const crypto = require('crypto');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CONFIG = JSON.parse(fs.readFileSync(process.env.EVENT_CONFIG || 'event-triggers.config.json', 'utf8'));
const SECRET = process.env.GITLAB_WEBHOOK_SECRET || '';
if (!SECRET) { console.error('FATAL: GITLAB_WEBHOOK_SECRET is required'); process.exit(1); }

const MAX_CONCURRENT = CONFIG.maxConcurrent || 2;
const JOB_TIMEOUT_MS = CONFIG.jobTimeoutMs || 30 * 60 * 1000; // 30 min default
const STATE_DIR = CONFIG.stateDir || '.webhook-receiver-state';
const DEDUPE_CAP = 5000;

fs.mkdirSync(STATE_DIR, { recursive: true });
const PROCESSED_FILE = path.join(STATE_DIR, 'processed-keys.json');
const LEDGER_FILE = path.join(STATE_DIR, 'jobs.jsonl');

// Persistent dedupe: survives restarts; capped so the file can't grow forever.
let processedList = [];
try { processedList = JSON.parse(fs.readFileSync(PROCESSED_FILE, 'utf8')); } catch (e) { /* first run */ }
const seen = new Set(processedList);
function markProcessed(key) {
  seen.add(key);
  processedList.push(key);
  if (processedList.length > DEDUPE_CAP) processedList = processedList.slice(-DEDUPE_CAP);
  try { fs.writeFileSync(PROCESSED_FILE, JSON.stringify(processedList)); }
  catch (e) { console.error('[state] persist failed:', e.message); }
}

// Job ledger: one jsonl line per event, greppable, safe to rotate externally.
function ledger(entry) {
  try { fs.appendFileSync(LEDGER_FILE, JSON.stringify({ ts: new Date().toISOString(), ...entry }) + '\n'); }
  catch (e) { console.error('[ledger] append failed:', e.message); }
}

function tokenOk(received) {
  const a = Buffer.from(String(received || ''));
  const b = Buffer.from(SECRET);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Map an event payload to a job, or null if nothing in the allowlist matches.
function route(event) {
  const t = CONFIG.triggers || {};
  const kind = event.object_kind;

  if (kind === 'note') {
    const oa = event.object_attributes || {};
    if (oa.noteable_type !== 'MergeRequest') return null;
    const m = String(oa.note || '').match(/^\s*(\/[a-zA-Z][\w-]*)([^\n]*)/); // first line "/cmd args"
    if (!m) return null;
    const mapped = (t.comment || {})[m[1].toLowerCase()];
    if (!mapped) return null; // not allowlisted -> ignore
    return {
      command: mapped, args: m[2].trim(),
      mr: event.merge_request && event.merge_request.iid,
      actor: event.user && event.user.username,
      key: `note:${oa.id}`,
    };
  }

  if (kind === 'merge_request') {
    const oa = event.object_attributes || {};
    const sha = oa.last_commit && oa.last_commit.id;
    const labels = (event.labels || []).map(l => l.title);
    for (const [label, mapped] of Object.entries(t.label || {})) {
      if (labels.includes(label)) {
        return { command: mapped, args: '', mr: oa.iid, actor: event.user && event.user.username,
                 key: `mr-label:${oa.iid}:${label}:${sha}` };
      }
    }
    const mapped = (t.mrAction || {})[oa.action];
    if (mapped) {
      return { command: mapped, args: '', mr: oa.iid, actor: event.user && event.user.username,
               key: `mr:${oa.iid}:${oa.action}:${sha}` };
    }
    return null;
  }

  if (kind === 'pipeline') {
    const oa = event.object_attributes || {};
    if (oa.status === 'failed' && t.pipelineFailed && event.merge_request) {
      return { command: t.pipelineFailed, args: '', mr: event.merge_request.iid, actor: 'ci',
               key: `pipe:${oa.id}` };
    }
    return null;
  }

  return null;
}

function actorAllowed(actor) {
  const list = CONFIG.allowedActors || [];
  return list.length === 0 || list.includes(actor);
}

// Bounded concurrency: a FIFO queue feeds at most MAX_CONCURRENT CLI sessions.
const queue = [];
let running = 0;

function dispatch(job) {
  if (seen.has(job.key)) { console.log('[dedupe] skip', job.key); return; }
  markProcessed(job.key);
  if (!actorAllowed(job.actor)) { console.log('[deny] actor not allowed:', job.actor); return; }
  queue.push(job);
  ledger({ ev: 'queued', key: job.key, actor: job.actor, command: job.command, mr: job.mr, depth: queue.length });
  pump();
}

function pump() {
  while (running < MAX_CONCURRENT && queue.length > 0) start(queue.shift());
}

function start(job) {
  const cli = process.env.CODEBUDDY_CLI || CONFIG.codebuddyCli || 'codebuddy';
  // The mapped slash-command + args + MR context. Adapt to your CLI's invocation.
  const prompt = `${job.command} ${job.args} mr=${job.mr}`.trim();
  // 无人值守：detached 会话没有 TTY/stdin，交互确认会让进程永久挂起。
  //   -p = 以非交互(print)方式跑（CodeBuddy headless）。注意：-p 单独不免确认，
  //        仍按 permissions.allow / -y 决定是否弹窗。
  //   免确认二选一：① 受控（推荐）= permissions.allow 白名单 + deny 红线（automation-settings.json，
  //                              经 --settings 注入或放进 CodeBuddy 设置），只用 -p；
  //                 ② 全量    = codebuddyFlags 设 ["-p","-y"]，-y 自动批准所有确认（无工具级护栏）。
  //   flag 名以 `codebuddy --help` 为准。
  const flags = (process.env.CODEBUDDY_FLAGS && process.env.CODEBUDDY_FLAGS.trim().split(/\s+/))
             || CONFIG.codebuddyFlags || ['-p'];
  const settings = process.env.CODEBUDDY_SETTINGS || CONFIG.automationSettings;
  const args = [...flags];
  if (settings) args.push('--settings', settings);
  args.push(prompt);

  running += 1;
  const startedAt = Date.now();
  console.log('[start]', job.actor, '->', prompt, `(running=${running})`);
  ledger({ ev: 'start', key: job.key, command: job.command, mr: job.mr });

  // NOTE: command/args come from the allowlist + are passed as a single arg (no shell),
  //       user-controlled text is never interpolated into a shell string.
  // detached:true gives the child its own process group, so the watchdog can
  // kill the whole CLI session tree (CLI + its spawned tools) in one shot.
  const child = spawn(cli, args, { cwd: CONFIG.projectDir, stdio: ['ignore', 'inherit', 'inherit'], detached: true });

  // Kill the whole session tree: POSIX = process group; Windows has no
  // process groups, so fall back to taskkill /T.
  const killTree = () => {
    try {
      if (process.platform === 'win32') spawn('taskkill', ['/pid', String(child.pid), '/T', '/F']);
      else process.kill(-child.pid, 'SIGKILL');
    } catch (e) { /* already gone */ }
  };

  let timedOut = false;
  const watchdog = setTimeout(() => {
    timedOut = true;
    console.error('[timeout] killing job after', JOB_TIMEOUT_MS, 'ms:', job.key);
    killTree();
  }, JOB_TIMEOUT_MS);

  const finish = (code, sig, err) => {
    clearTimeout(watchdog);
    running -= 1;
    ledger({ ev: 'end', key: job.key, command: job.command, mr: job.mr,
             code: code == null ? null : code, signal: sig || null,
             timedOut, error: err || null, ms: Date.now() - startedAt });
    if (timedOut) console.error('[end] TIMED OUT', job.key);
    else console.log('[end]', job.key, 'code=' + code, `(${Date.now() - startedAt}ms)`);
    pump();
  };

  child.on('error', e => { console.error('[cli] spawn failed:', e.message); finish(null, null, e.message); });
  child.on('exit', (code, sig) => finish(code, sig));
}

const server = http.createServer((req, res) => {
  if (req.method !== 'POST') { res.writeHead(405); return res.end(); }
  if (!tokenOk(req.headers['x-gitlab-token'])) { res.writeHead(401); return res.end('bad token'); }
  let buf = '';
  req.on('data', c => { buf += c; if (buf.length > 2e6) req.destroy(); });
  req.on('end', () => {
    res.writeHead(200); res.end('ok'); // ack fast; GitLab webhooks time out otherwise
    try {
      const job = route(JSON.parse(buf));
      if (job) dispatch(job);
    } catch (e) { console.error('[parse/route]', e.message); }
  });
});

const port = process.env.PORT || CONFIG.port || 3010;
server.listen(port, () => console.log(`event-triggers receiver v1.1.0 listening on :${port} (maxConcurrent=${MAX_CONCURRENT}, jobTimeout=${JOB_TIMEOUT_MS}ms)`));
