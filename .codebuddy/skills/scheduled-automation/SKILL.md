---
name: scheduled-automation
description: 定时自动化交付体系技能。把文档补充、夜间发布、每日代码审查、缺陷清理、GitLab Issue 修复、MR 审查合并、设计文档周更 7 类任务做成可调度 runbook，让交付阶段 24×7 无人值守运行；全部经 MR 流程提交、轮询 CI、失败自修复、auto-merge。用户提到"定时任务/夜间自动/无人值守/scheduled/cron/每日审查/自动发布/排程"时触发。具体 GitLab 交互经 gitlab-bridge。
---

# 定时自动化交付体系（Scheduled Automation）

本技能回答的是：**怎样让 CI/CD 的交付阶段不依赖人值守，由定时任务驱动 AI 自动跑文档、审查、修复、发布、合并。**

## 核心心智

1. **交付阶段无人值守**：白天人机协作，下班后定时任务接管，次日查结果。这是方法论「脚本自动化交付阶段」的落地。
2. **每任务独立 runbook**：7 类任务各有明确触发时间、动作、产物，互不耦合。
3. **全走 MR 流程**：所有代码/文档修改不直推 main——经 MR 提交 → 轮询 CI → 失败自修复（最多 3 次）→ CI 绿后 auto-merge。
4. **增量式执行**：首次全量建基线，之后只处理上次→本次的增量。
5. **平台无关**：runbook 定义「做什么」；`/schedule-setup` 适配「怎么调度」——三种触发方式：CodeBuddy 原生定时能力、GitLab CE 14.8.2 原生 **Pipeline Schedules**（`CI/CD → 计划`，cron + `$CI_PIPELINE_SOURCE == "schedule"`）、或系统 cron 调 `codebuddy` CLI。GitLab 原生 Pipeline Schedules 是 CE 14.8.2 已支持的调度载体，详见 `ci-integration/references/ce-14.8.2-cicd-support.md` §6。

## 资源加载规则

- 执行某个具体定时任务、或要看任务清单细节时，读 `references/task-playbooks.md`
- 在业务项目落地调度配置时，读 `templates/schedule-config.sample`
- 轮询 CI 需本地降级（MCP 不可用但 glab 可用）时，读 `templates/ci-poll.sh`

## 何时使用

1. 在业务项目首次接入定时自动化（`/schedule-setup`）
2. 手动触发某个定时任务的 runbook（如「现在跑一次每日审查」）
3. 调整任务调度时间或启停

## 何时不用

1. 单次手动操作（修一个 bug / 审一次代码）→ 直接用对应命令（`/defect-loop`、`/code-review`）
2. 引擎仓库自身——引擎托管在 GitHub，只提供 runbook 与模板，不放成品调度配置

## 阻断条件

1. `gitlab-bridge` 写动作（`mr.merge` / `issue.*`）不可用且无本地降级路径——阻断并提示放开 `GITLAB_READ_ONLY_MODE`
2. 业务项目无可用调度器，且 CodeBuddy 原生定时能力不可用——阻断并说明

## 7 类定时任务总览

| 任务 | 时间 | 动作 | 复用 |
|---|---|---|---|
| Task #1 文档补充 | 每日 01:00 | 扫 24h 提交 → 即时/每日规格回填 | `spec-backfill` + `/spec-sync` |
| Task #3 夜间发布 | 每日 02:00 | semver 定版 → Release Notes → tag → release 流水线 | `release-and-rollback` + `/release` |
| Task #4 每日审查 | 每日 03:00 | 增量审查（周日全量）→ 报告 + Critical Issue | `code-review-standards`（增量模式）|
| Task #9 Issue 清理 | 每日 05:00 | 扫 `.codebuddy-runtime/issues/` → 修 Critical（≤3）| `defect-tracking` + `/defect-loop source=codebuddy` |
| Task #10 GitLab Issue 修复 | 每日 08:00+20:00 | 扫 GitLab Issue → 分类 → 修 1 个 | `defect-tracking` + `/defect-loop source=gitlab` |
| Task #17 MR 审查合并 | 每小时 | open MR → CI 通过+审查通过 → 合并 | `gitlab-bridge` + `code-review` |
| Task #25 文档周更 | 周一 10:00 | 全量扫描 → README 重写 + 模块增量 | `spec-backfill` + `/spec-sync mode=weekly` |

每任务的详细步骤见 `references/task-playbooks.md`。

## 公共机制

- 所有修改经 MR，不直推 main
- MR 提交后轮询 CI（最多 40 次，每次 30s）；主路径经 `gitlab-bridge` 的 `pipeline.status`，降级用 `templates/ci-poll.sh`（本地 glab）
- CI 失败时分析日志自动修复（最多 3 次）
- CI 通过后 auto-merge / squash 合并
- 每个任务结束输出结构化报告
- **事件驱动优先**：接 `/event-setup` 后由 webhook 实时触发，轮询退化为兜底/对账（见 `event-triggers`）
- **幂等 + 并发**：幂等键用 `MR iid + 最新 sha`（与 event-triggers 共用）；同一 MR 串行、取消旧任务，杜绝重复合并/修复
- **结果回贴**：经 `commit.status` 贴 MR 状态、`mr.discussion` 贴行内审查意见
- **触发身份**：AI 自动 push 用能触发 MR 流水线的身份；`CI_JOB_TOKEN` 触发有防循环限制会绕过门禁——接入前用测试 MR 核对（见 `references/task-playbooks.md` 公共机制）

## 安全约束

1. 定时自动化依赖 GitLab 写动作——上线前必须把 MCP server 的 `GITLAB_READ_ONLY_MODE` 改为 `false`，且经 Boss 确认
2. 写权限放开后建议用专用服务账号 PAT（scope: api），不复用管理员 token
3. Task #3 夜间发布只打 tag 触发 release 流水线，**不直接部署生产**；生产部署仍需人工审批（与 `/release` 一致）
4. 无人值守免确认：cron / Pipeline 拉起的会话无终端，逐工具确认会让任务挂起；用 `--settings` 注入专用 `automation-settings.json`（allow 白名单 + deny 红线，见 `event-triggers/templates/automation-settings.sample.json`）限定在无人值守路径。注意这是 **CLI 工具层**确认，与 `GITLAB_READ_ONLY_MODE`（GitLab 写动作）是两层，别混淆；deny 优先于 allow，触达生产数据仍受 data-safety 数据铁律约束

## 禁止事项

1. 不要让定时任务直推 main——绕过 CI 门禁会让无人值守变成无人兜底
2. 不要在写权限未放开时假装能合并——只读模式下输出人工提示，不谎报已合并
3. 不要把 7 个任务塞进一个会话连续跑——每任务独立上下文，避免上下文失忆（新窗口原则）
4. 不要在引擎仓库放成品调度配置——只在装了 `.codebuddy/` 的业务项目里 `/schedule-setup` 实例化
