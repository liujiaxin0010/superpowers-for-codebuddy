---
name: pending-decisions
description: 待决策项持久化技能。当一轮对话中出现 ≥2 个待决策/待讨论项、且 Boss 未一次性全部回答时，强制把这些项落盘到 `docs/pending-decisions.md`，避免在 brainstorm/spec-lite 等多轮澄清场景中遗失。用户提到“多个待决策/有几个问题需要确认/待讨论项/先记下来/不要忘/这几个先放着”，或 AI 自己在一次回复中抛出 ≥2 个选项题、决策点、设计岔路时触发。
---

# Pending Decisions（待决策项持久化）

## 1. 解决的问题

`findings.md`、`progress.md`、`spec-lite.md` 只承载已收敛的研究结论、阶段状态与轻量规格。
但 brainstorm 和 spec-lite 阶段常常出现：

1. AI 一次抛出多个待决策项（≥2 个选项题/设计岔路/合规取舍）
2. Boss 只回答其中 1 个，剩余项被对话淹没
3. 下一轮 AI 自动“忘了”剩余项，三个 md 也都没记

本技能负责把这种**短期、流动、未收敛**的决策点单独落盘，并保证：

- 不丢
- 可逐项回查
- 阶段切换 / 会话结束前能主动复盘

## 2. 强制触发条件

满足任一即必须使用：

1. AI 在一次回复里给 Boss 抛出 ≥ 2 个待决策项（选项题、岔路、取舍）
2. Boss 上一轮的回复**只覆盖了部分项**，剩余项未明确回答
3. Boss 主动说“先记下来 / 这几个先放着 / 别忘了 / 加到待决策”
4. 切阶段（brainstorm→spec-lite、spec-lite→write-plan 等）或 handoff 前

不要等 Boss 提醒——AI 自检发现一次抛了 ≥ 2 项就要立刻持久化。

## 3. 文档与字段

默认路径：`docs/pending-decisions.md`，按 `template.md` 创建。

每条记录字段（与 `schemas/pending-decisions.schema.json` 对齐）：

| 字段 | 说明 |
|---|---|
| `id` | `PD-YYYYMMDD-NNN`，单调递增 |
| `phase` | `brainstorm` / `spec-lite` / `write-plan` / `execute-plan` / `code-review` / `release` / `other` |
| `raisedAt` | 提出时间（ISO 日期） |
| `question` | 问题原文（不要 AI 改写，保留对话原文） |
| `options` | 选项数组，每个选项含 `label / pros / cons / prerequisite` |
| `recommendation` | AI 当前推荐及理由（可空） |
| `status` | `pending` / `partial` / `answered` / `deferred` / `dropped` |
| `answer` | Boss 最终决策（status=answered 时必填） |
| `answeredAt` | 决策时间 |
| `linkedDocs` | 关联 `specPath / brainstormPath / planPath` 等 |
| `notes` | 补充上下文（讨论摘要、风险提示） |

## 4. 流程协议

### 4.1 检测阶段（每次 AI 回复完成前自检）

1. 数本轮回复中向 Boss 抛出的待决策项数量 N
2. `N >= 2` → 立刻执行 4.2
3. `N < 2` → 跳过本次持久化，但仍需检查上一轮是否有未回答项（4.3）

### 4.2 写入阶段（持久化）

1. 若 `docs/pending-decisions.md` 不存在，读取 `template.md` 创建
2. 给本轮新抛出的每一项分配 `PD-YYYYMMDD-NNN`
3. 默认 `status=pending`；若 AI 已给出推荐选项，仍记 `pending`，由 Boss 决策后再变更
4. 把 `linkedDocs` 指向当前阶段的主文档（如 spec 文档路径）
5. 在向 Boss 输出的对话末尾追加一行提示：
   `Boss，本轮新增 N 条待决策项已持久化到 docs/pending-decisions.md（IDs: PD-...）。`

### 4.3 回复合并阶段（每次收到 Boss 回复后）

1. 读取 `docs/pending-decisions.md`，找到 `status in (pending, partial)` 的项
2. 比对 Boss 本轮回复：
   - 已明确回答 → `status=answered`，填 `answer / answeredAt`
   - 部分回答 → `status=partial`，把已答内容写入 `notes`
   - 明确放弃/作废 → `status=dropped`
   - 明确延后 → `status=deferred`
3. 把 `answered` 项的结论同步回对应主文档（spec/brainstorm/plan），不允许只留在 pending-decisions.md
4. 仍有 `pending / partial` 项时，下一轮回复**必须显式提醒** Boss 剩余项

### 4.4 阶段切换 / 收尾扫描

切阶段（brainstorm→spec-lite、spec-lite→write-plan 等）或 handoff 前：

1. 全表扫描 `status in (pending, partial)` 的项
2. 若存在，默认返回 `BLOCKED`，必须由 Boss 显式批准“延后”或“作废”才能进入下一阶段
3. 走 handoff 时把未决项写进 `session-handoff` 快照

## 5. 与 file-based-memory 的边界

| 写入 pending-decisions | 写入 findings | 写入 progress |
|---|---|---|
| 未收敛的待决策项 | 已收敛的技术决策 | 当前阶段状态/下一步 |
| 多选 + 优劣 + 推荐 | 决策结论 + 理由 | 阶段进展、错误日志 |
| 状态流转 pending→answered | 静态、可复用 | 动态、强时序 |

`answered` 后的结论可以**同步**到 findings（如形成可复用决策），但 pending-decisions 本身**不删除**，保留审计轨迹。

## 6. 资源加载

- 模板：`template.md`
- Schema：`schemas/pending-decisions.schema.json`
- 校验脚本：`scripts/lint-pending.sh`
- 命令入口：`/pending`（见 `.codebuddy/commands/pending.md`）

## 7. 禁止事项

1. 不要把已收敛的决策（已 `answered`）也只写在 pending-decisions.md 而不回填主文档
2. 不要 silently 修改既有项的 `question` 原文，必要时新增项并标 `notes=supersede(PD-X)`
3. 不要在持久化前**继续追问**新一轮问题——先落盘再追问
4. 不要让 pending-decisions.md 体积无界增长——`dropped/answered` 项保留，但按月归档到 `docs/pending-decisions/YYYY-MM.md`（只在文件 >500 行时触发）
5. 不要把含敏感数据（凭证、token、个人信息）的讨论写入此文件
