# 7 类定时任务 Runbook

每个任务独立运行，产物经 MR 流程合入 main，CI 通过后才算完成。任务大多采用**增量式执行**：首次全量建基线，之后只处理上次→本次的增量。

## 公共机制（所有任务共用）

```
修改产出 → MR 提交 → 轮询 CI（最多 40×30s）
                          ├─ 通过 → auto-merge / squash 合并 → 输出报告
                          └─ 失败 → 分析日志自动修复（最多 3 次）→ 重新提交
                                       └─ 仍失败 → 标记需人工，输出报告
```

CI 轮询主路径：`gitlab-bridge` 的 `pipeline.status`；MCP 不可用但本地 glab 可用时用 `templates/ci-poll.sh`。

---

## Task #1 — 文档补充（每日 01:00）

- 触发：定时扫描最近 24 小时 git 提交
- 动作：feat→检查是否已在 spec 中描述、fix→检查行为描述是否需更新、refactor→通常不动
- 委托：`spec-backfill` 即时/每日回填 → `/spec-sync mode=daily`
- 范围：`spec/` 下 README、核心流程、OpenAPI、配置设计、数据库设计 + CONTEXT.md
- 产出：文档更新 MR + 更新报告

## Task #3 — 夜间发布（每日 02:00）

- 触发：检查 origin/main 自上次 tag 以来的新提交
- 动作：按 semver 定版（0.x：feat→minor / fix→patch）→ 生成结构化 Release Notes → 打 tag 推送 → 触发 release 流水线
- 委托：`release-and-rollback` + `/release`
- 失败：流水线失败时分析日志并修复
- 约束：只打 tag 触发流水线，**不直接部署生产**
- 产出：新版本 tag + Release Notes + 多平台构建产物

## Task #4 — 每日代码审查（每日 03:00）

- 触发：定时
- 模式：增量（工作日，基于 Baseline Commit diff）/ 全量（周日 / 首次）
- 动作：流程追踪 → Block 化 → 按 P0-P3 逐 Block 审查 → Critical 写 `.clawbench/issues/ISS-{nnn}.md` → 检查已有 open Issue 疑似解决状态
- 委托：`code-review-standards`（`references/incremental-mode.md` + `review-cube.md` + `clawbench-issue-format.md`）
- 约束：**只生成审查输出文件，不修改源代码**（修复由 Task #9 做）
- 产出：审查计划 + Block 报告 + 汇总报告（末尾记 Baseline Commit）+ Issue 文件

## Task #9 — Review Issue 清理（每日 05:00）

- 触发：定时
- 动作：扫 `.clawbench/issues/` open Issue → 验证已有修复 → 按 P0 Security > P0 Flow > P1 Concurrency 选目标 → 每次最多修 3 个，最小化修复 + 补测试
- 委托：`defect-tracking` + `/defect-loop source=clawbench max=3`
- 产出：修复代码 + 测试 + Issue 状态更新 + MR

## Task #10 — GitLab Issue 自动修复（每日 08:00 + 20:00）

- 触发：定时
- 动作：`intake.list` 扫 GitLab open Issue → AI 分类（bug/enhancement/question）→ 每次只修 1 个 bug，独立 Worktree
- 委托：`defect-tracking` + `/defect-loop source=gitlab max=1`
- 放弃标准：>5 文件 / 跨层架构 / 核心流程重构 / 方案不确定
- 产出：修复代码 + 测试 + Issue 标签/状态更新 + MR

## Task #17 — MR 审查与合并（每小时）

- 触发：定时
- 动作：`intake`/`mr.status` 获取 open MR，分「自己的」和「其他人的」
  - 自己的：CI 全通过 + 无冲突 → `mr.merge`；否则创建 Worktree 修复 → push → 轮询 → 合并
  - 其他人的：有冲突 → `mr.comment` 通知作者跳过；CI+审查通过 → 合并；有严重问题 → request-changes
- 审查重点：逻辑正确性 + 边界 + 安全性 + 测试覆盖
- 去重：不重复评论已 review 的 MR
- 委托：`gitlab-bridge`（`mr.*`）+ `code-review`
- 产出：MR 审查意见 + 合并操作 + CI 修复

## Task #25 — 设计文档周更新（每周一 10:00）

- 触发：定时
- 动作：读 `spec/` 全部文档建心理模型 → 扫本周代码变化 → README 全量重写 + 模块文件增量更新 → 三段式写作 → 自检（流程图可渲染 / 功能完整 / 术语一致 / 无实现细节泄漏 / 无过时信息）
- 委托：`spec-backfill` + `/spec-sync mode=weekly`
- 产出：设计文档更新 MR + 更新报告

---

## 每日时间线

```
01:00   02:00   03:00   05:00   08:00      20:00      每小时      周一10:00
  │       │       │       │       │          │           │           │
文档    发布    审查    Issue   GitLab      GitLab      MR审查      设计文档
补充    打tag   (周日   清理    Issue修复   Issue修复   合并        周更新
                全量)   (≤3)
```
