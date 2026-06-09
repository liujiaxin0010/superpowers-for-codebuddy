# 引擎与模板变更记录

业务项目是**复制模板**落地的，引擎修了 bug 不会自动同步过去——在业务项目里跑 `/upgrade-check` 对照本文件检查落后项。
模板版本标注位置：JS 头部 `TEMPLATE_VERSION` 注释 / JSON 的 `_templateVersion` 字段；**无标注 = pre-1.1.0，建议立即升级**。

## 模板当前版本

| 模板 | 版本 | 位置 |
|---|---|---|
| webhook-receiver.js | 1.1.0 | `.codebuddy/skills/event-triggers/templates/` |
| event-triggers.config.sample.json | 1.1.0 | 同上 |
| automation-settings.sample.json | 1.1.0 | 同上 |
| schedule-config.sample | 1.1.0 | `.codebuddy/skills/scheduled-automation/templates/` |
| commit-msg-lint.sh | 1.0.0 | `.codebuddy/skills/ci-integration/templates/` |
| ci-poll.sh | 1.0.0 | `.codebuddy/skills/scheduled-automation/templates/` |

## 2026-06-09 — 模板 1.1.0（无人值守免确认 + 可运维加固）

**破坏性认知修正**：CLI 非交互调用形态从假设的 `codebuddy run --cwd <dir>` 修正为实测的 `codebuddy -p`（headless）；`-p` 单独**不**免确认，免确认 = `permissions.allow` 白名单（受控，推荐）或 `-y`（全量自动批准，绕过 deny 红线）。

- `webhook-receiver.js` 1.1.0：
  - 免确认注入：`codebuddyFlags`（默认 `["-p"]`）+ `automationSettings`（`--settings`）；`stdin: ignore`；`cwd` 走 spawn 选项
  - **看门狗** `jobTimeoutMs`（默认 30min）：到时杀整棵进程树（POSIX 进程组 / Windows `taskkill /T`），根治「确认弹窗挂死数小时」类故障
  - **并发上限** `maxConcurrent`（默认 2）+ FIFO 队列
  - **持久幂等** `stateDir/processed-keys.json`（重启不丢，5000 上限）
  - **任务台账** `stateDir/jobs.jsonl`（queued/start/end、退出码、信号、timedOut、耗时）
- `event-triggers.config.sample.json`：新增 `codebuddyFlags` / `automationSettings` / `maxConcurrent` / `jobTimeoutMs` / `stateDir`
- `automation-settings.sample.json`（新增模板）：无人值守专用权限设置——`allow` 白名单 + `deny` 红线（deny 优先）；仅作用于带 `--settings` 的会话
- `schedule-config.sample`：cron 行加 `-p --settings`；新增 Windows `schtasks` 方式 B'
- 升级要点（从 pre-1.1.0）：替换 `webhook-receiver.js` 整文件；config 增补新字段（旧字段兼容）；主机落一份 `automation-settings.json`（勿入库）；验证命令见 `docs/playbooks/unattended-permission-checklist.md` §4

## 2026-06-09 — 引擎自身

- 新增引擎自检 CI（`.github/workflows/engine-lint.yml`）：JS/JSON/Shell 语法、文档路径引用 lint、commit-msg 门禁单测、自家 PR 提交标签校验
- `CODEBUDDY.md` 铁律 2 增加无人值守分支：headless 会话禁止同步等人，落盘 + 回贴 + BLOCKED 退出
- 仓库卫生：个人配置与运行产物出库、9 处路径腐烂修复、`缺陷.md` → `defect-classification.md`
