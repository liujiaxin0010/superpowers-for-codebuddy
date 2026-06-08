#!/usr/bin/env node
/**
 * event-triggers webhook receiver (REFERENCE implementation).
 *
 * Receives GitLab webhook events, validates the secret token, maps a small
 * ALLOWLIST of triggers (MR comments like "/code-review", labels like
 * "ai:review", pipeline failures) to Featureflow commands, and dispatches
 * them to the CodeBuddy CLI. This replaces scheduled-automation polling with
 * event-driven triggering.
 *
 * This is a REFERENCE — run it on the same intranet host as the CodeBuddy CLI,
 * behind systemd/pm2 and a reverse proxy, reachable only from the internal
 * GitLab. Harden (TLS, rate limiting, persistent dedupe store) for your env.
 *
 * Config : event-triggers.config.json  (see event-triggers.config.sample.json)
 * Env    : GITLAB_WEBHOOK_SECRET (required), CODEBUDDY_CLI (optional override)
 *          EVENT_CONFIG (optional path to config), PORT (optional)
 *          CODEBUDDY_SETTINGS (optional: automation-settings.json for unattended,
 *                              confirmation-free runs; see automation-settings.sample.json)
 */
'use strict';
const http = require('http');
const crypto = require('crypto');
const { spawn } = require('child_process');
const fs = require('fs');

const CONFIG = JSON.parse(fs.readFileSync(process.env.EVENT_CONFIG || 'event-triggers.config.json', 'utf8'));
const SECRET = process.env.GITLAB_WEBHOOK_SECRET || '';
const seen = new Set(); // in-memory dedupe; swap for a file/redis store in prod

if (!SECRET) { console.error('FATAL: GITLAB_WEBHOOK_SECRET is required'); process.exit(1); }

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

function dispatch(job) {
  if (seen.has(job.key)) { console.log('[dedupe] skip', job.key); return; }
  seen.add(job.key);
  if (!actorAllowed(job.actor)) { console.log('[deny] actor not allowed:', job.actor); return; }

  const cli = process.env.CODEBUDDY_CLI || CONFIG.codebuddyCli || 'codebuddy';
  // The mapped slash-command + args + MR context. Adapt to your CLI's invocation.
  const prompt = `${job.command} ${job.args} mr=${job.mr}`.trim();
  console.log('[dispatch]', job.actor, '->', prompt);
  // NOTE: command/args come from the allowlist + are passed as a single arg (no shell),
  //       user-controlled text is never interpolated into a shell string.
  // 无人值守：detached 会话没有 TTY/stdin，逐工具的确认弹窗会让进程永久挂起。
  // --settings 指向主机上的专用 automation-settings.json（allow 白名单 + deny 红线），
  // 让 CI 事件触发的会话免人工确认，同时保留 rm -rf 等红线。flag 名以 CLI --help 为准。
  const settings = process.env.CODEBUDDY_SETTINGS || CONFIG.automationSettings;
  const args = ['run', '--cwd', CONFIG.projectDir];
  if (settings) args.push('--settings', settings);
  args.push(prompt);
  // stdin 用 'ignore'：无人值守不继承终端，杜绝任何残留的交互等待
  const child = spawn(cli, args, { stdio: ['ignore', 'inherit', 'inherit'], detached: true });
  child.on('error', e => console.error('[cli] spawn failed:', e.message));
  child.unref();
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
server.listen(port, () => console.log(`event-triggers receiver listening on :${port}`));
