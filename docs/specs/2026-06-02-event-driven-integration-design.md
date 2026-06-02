# 事件驱动集成优化设计（P0/P1）— 对标 Claude Code 的 GitHub 接入

> 日期：2026-06-02 ｜ 目标平台：内网 GitLab Community Edition 14.8.2
>
> 背景：对标 Claude Code 云端连 GitHub 的实现方式（GitHub App + 短期 installation token + OIDC、事件 / `@claude` 触发、多 status checks、行内 PR 评论、托管 runner），找出当前 Featureflow + GitLab CE 接入的差距，并在 CE 14.8.2 约束内补齐。本文是 P0/P1 优化的设计与改动记录。

## 1. 差距对照

| 维度 | Claude Code / GitHub | 原当前实现 / GitLab CE 14.8.2 | 本次优化 |
|---|---|---|---|
| 认证 | GitHub App + 短期 token + OIDC，细粒度权限 | 长期个人 PAT（scope=api，粗粒度）| **P0-4** 项目级令牌 + 轮换 + masked/protected |
| AI 触发 | 事件驱动（webhook / `@claude`）| 轮询（Task#17 每小时、`pipeline.status` 40×30s）| **P0-1** webhook 事件驱动，轮询退兜底 |
| 人召唤 AI | PR 内 `@claude` | CodeBuddy 会话 / cron | **P0-2** MR 评论 `/code-review`、`ai:review` 标签 |
| 审查呈现 | 行内 PR review 评论 | 报告 + Critical Issue（独立于 MR）| **P0-3** `mr.discussion` 行内贴 |
| 合并门禁粒度 | 多个 required checks | 单 pipeline + Pipelines must succeed | **P1-5** 可选审查 job；**P1-6** commit status 展示 |
| 幂等/并发 | 事件天然幂等 | 轮询可能重复动作 | **P1-7** MR iid+sha 幂等键 + 串行锁 |
| CI 在 AI 提交上重跑 | GitHub App token 触发下游 | 未显式核对 | **P1-8** CI_JOB_TOKEN 防循环核对 |

## 2. 设计决策（逐项）

### P0-1 / P0-2 事件驱动 + MR 评论/标签触发
- 新增 `event-triggers` 技能：webhook 接收器 → 验签 → 按 `trigger-map` 映射命令 → 调 CLI → 结果经 bridge 回贴。
- 新增 `/event-setup` 命令（与 `/ci-setup`、`/schedule-setup` 同构）：探测 → 采参 → 实例化接收器/配置 → 注册 webhook → 人工验证清单。
- 接收器为 Node 参考实现（`webhook-receiver.js`）：先 200 应答再异步、`X-Gitlab-Token` 验签、allowlist 触发、幂等去重、不把用户输入拼进 shell。
- `event-triggers` 与 `scheduled-automation` 共用命令与幂等键；轮询退化为兜底/对账。

### P0-3 审查行内化
- `gitlab-bridge` 新增 `mr.discussion`（带 diff `position`）；`/code-review` 步骤 11 把问题按文件+行贴成 MR 讨论；退化为 `mr.comment` 汇总或仅报告；配合「All threads must be resolved」成软门禁。

### P0-4 令牌最小权限与轮换
- `mcp-setup.md` 新增「令牌最小权限与轮换」：优先 Project Access Token / 专用 bot（项目级、可吊销、设过期），CI 用 masked+protected 变量，读写分阶段，吊销演练。
- CE 14.8.2 无 OIDC（`id_tokens` 16.4+）→ 用项目级令牌 + 轮换替代。

### P1-5 AI 审查作为可选 pipeline job
- `ci-integration` 新增 `ai-review-job.yml.template`：专用 `ai-review` tag runner 拉起 CLI，仅 MR 触发，CE 安全子集，默认 `allow_failure: true` 渐进，稳定后改 `false` 成阻断。
- 默认仍走 `scheduled-automation` Task#4 产 Issue；无专用 runner 不强塞普通 runner。

### P1-6 commit status 贴 MR
- `gitlab-bridge` 新增 `commit.status`（REST `POST /projects/:id/statuses/:sha`）；`/code-review` 与 `scheduled-automation` 回贴状态。CE 下为展示态（无 External Status Checks，非强制门禁）。

### P1-7 幂等 + 并发
- `scheduled-automation` 公共机制：幂等键 `MR iid + 最新 commit sha`（与事件触发共用）；同一 MR 串行、取消旧任务。

### P1-8 CI_JOB_TOKEN 防循环核对
- `ci-integration` 禁止事项 + `scheduled-automation` 公共机制：AI 自动 push 用能触发 MR 流水线的身份（PAT / Project Access Token），避免 `CI_JOB_TOKEN` 防循环导致绕过门禁；接入前用测试 MR 核对。

## 3. 改动清单（文件级）

**新增**
- `.codebuddy/skills/event-triggers/SKILL.md`、`references/trigger-map.md`、`templates/webhook-receiver.js`、`templates/event-triggers.config.sample.json`
- `.codebuddy/commands/event-setup.md`
- `.codebuddy/skills/ci-integration/templates/ai-review-job.yml.template`
- 本设计 spec

**修改**
- `gitlab-bridge`：`SKILL.md`（动作表 + 安全约束）、`references/capability-map.md`（`mr.discussion`/`commit.status`/`webhook.*` 映射+开关+降级）、`references/gitlab-version-support.md`（webhook/discussion/status 行）、`references/mcp-setup.md`（令牌最小权限与轮换）
- `ci-integration`：`SKILL.md`（可选审查 job + CI_JOB_TOKEN 禁止项）、`references/ci-quality-principles.md`（review 阶段）
- `code-review.md`（步骤 11 行内化）、`requesting-code-review/SKILL.md`（输出要求）
- `scheduled-automation`：`SKILL.md` + `references/task-playbooks.md`（事件优先 + 幂等并发 + 回贴 + 触发身份）
- 索引：`README.md`、`CODEBUDDY.md`、`docs/playbooks/best-practices-tutorial.md`（C.9）

## 4. CE 14.8.2 残留差异（未满足实现，记入版本支持表）

| 能力 | 缺在 | CE 替代 | 残留差异 |
|---|---|---|---|
| OIDC 无存储短期令牌 | 16.4（`id_tokens`）| 项目级令牌 + 过期轮换 + masked/protected | 仍是长期令牌，靠轮换收敛风险 |
| External Status Checks（多 required checks 强制）| EE/Ultimate | 单 pipeline 强制 + `commit.status` 展示 | AI 审查作 job 才强制，否则仅展示 |
| 审查作合并阻断 | 需 agent 运行时 | 专用 `ai-review` runner（P1-5）| 需自维护带 CLI 的 runner |

## 5. 接入顺序与验证

1. `/ci-setup`（已具备）
2. 令牌收敛（P0-4）：换 Project Access Token，CI 变量 masked+protected
3. `/event-setup`（P0-1/2）：部署接收器、注册 webhook、配 `X-Gitlab-Token`
4. 放开 MCP 写权限（`GITLAB_READ_ONLY_MODE=false`，Boss 确认）
5. 把 `scheduled-automation` 轮询（Task#17 等）调成低频兜底
6. （可选）维护 `ai-review` runner，启用审查 job（P1-5）

**验证**：测试 MR 评论 `/code-review` → 事件到达、命令触发、`mr.discussion` 行内回贴、`commit.status` 显示；重复事件不重复动作（幂等）；AI 自动 push 能拉起 5 阶段流水线（CI_JOB_TOKEN 核对）。

## 6. 与既有体系关系

- `event-triggers`（主，实时）↔ `scheduled-automation`（兜底，定时）：共用命令 + 幂等键。
- `gitlab-bridge`：所有新交互（webhook 注册、行内评论、commit status）仍走唯一对接层，保持可移植 + 优雅降级。
- `ci-integration`：基础 5 阶段不变；审查 job 为可选增量。
