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
| commit-msg-lint.sh | 1.0.1 | `.codebuddy/skills/ci-integration/templates/` |
| ci-poll.sh | 1.0.0 | `.codebuddy/skills/scheduled-automation/templates/` |
| hooks-settings.sample.json（写完即检） | 1.0.0 | `.codebuddy/skills/instant-check/templates/` |

## 2026-06-10 — 计划/决策/记忆三件套（OPT-P1/P2/X1 + Q3/C1/D3/O1）

- write-plan 7.5：任务级复杂度 `S|M|L` + `complexityProfile`（OPT-P1）；3.6：读 `docs/adr/`，冲突须显式 supersede（OPT-P2）
- walkthrough 7.5 + `templates/adr-template.md`：架构级结论沉淀 ADR（accepted 后只可 supersede 不可改写）
- file-based-memory 归档轮转：台账 >400 行原文搬运 `docs/archive/` + 指针，禁总结压缩（OPT-X1）；引擎 progress.md 已轮转（518→23 行）
- requirement-review 7.5 风险回填 spec（Q3）；execute-plan 5.5 批次 checkpoint commit（C1）；release 4.5 版本→需求→MR 追溯链（D3）；O1 由 /metrics §3+§5 覆盖核销

## 2026-06-10 — 度量/审查/质量左移三件套 + 脚本归位

- **修复（重要）**：随安装分发的脚本归位技能目录——`/metrics`、`/code-review` 此前引用引擎根 `scripts/`，业务项目安装 `.codebuddy/` 后会 404。现：`metrics.js`/`stage-event.js` → `delivery-metrics/scripts/`，`diff-risk.js` → `code-review-standards/scripts/`；引擎根 `scripts/` 只留引擎自检。
- 新技能 `delivery-metrics`：`/metrics` Tier 0（git/门禁/jobs/决策聚合 + Top 摩擦点）+ Tier 1（自动修复接受率=git revert 零埋点；阶段周期 stage-event 埋点已接入 7 个主链命令步骤 0；缺陷逃逸率 foundPhase 约定）。
- `code-review-standards` 增 `diff-risk.js`（OPT-R1）：审查深度（deep/standard/light）与 `/security-review`·`/perf-check`·`/data-safety-check` 强制门禁由**实际 diff 代码信号**自动触发；文件感知排除文档/.sample 误判。
- 新技能 `instant-check`（OPT-C3）：PostToolUse hook 写完即检（JS/JSON/Shell/Python 单文件语法层），失败 stderr 当场回馈 AI；缺工具/异常一律放行；引擎仓库已 dogfood（`.claude/settings.json`）。
- 引擎 CI 新增三组单测（diff-risk 7 / instant-check 10 / metrics 冒烟）。

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

## 2026-06-09 — commit-msg-lint.sh 1.0.1

- **修复**：merge 提交豁免（`git rev-list --no-merges`）。此前从 master 合回 MR 分支的合并提交、GitHub Actions 的合成 PR merge commit 等**自动生成消息**会被误判"缺 AI 标签"而拦红流水线——引擎自检 CI 首跑即复现此 bug。升级 = 整文件替换。

## 2026-06-09 — 引擎自身

- 新增引擎自检 CI（`.github/workflows/engine-lint.yml`）：JS/JSON/Shell 语法、文档路径引用 lint、commit-msg 门禁单测、自家 PR 提交标签校验
- `CODEBUDDY.md` 铁律 2 增加无人值守分支：headless 会话禁止同步等人，落盘 + 回贴 + BLOCKED 退出
- 仓库卫生：个人配置与运行产物出库、9 处路径腐烂修复、`缺陷.md` → `defect-classification.md`
