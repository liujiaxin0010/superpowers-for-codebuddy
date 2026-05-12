---
name: spec-lite
description: 轻量规格生成技能。用于在编码前明确范围、分级（L/M/H）和门禁上下文，输出可执行的 spec 文档和 GateContext/TaskContract/GateResult。用户提到"出规格/写 spec/需求分析/分级/spec-lite/任务定级/生成规格文档"时触发。
---

# Spec-Lite（轻量规格）

## 何时使用

1. 用户提出新需求、新功能、变更请求，需要在编码前明确范围和等级
2. 需要对任务进行 L/M/H 分级以决定后续流程深度
3. 用户要求"出规格"、"写 spec"、"需求分析"或显式调用 `/spec-lite`
4. 需要生成门禁上下文（GateContext）供下游技能消费

## 何时不用

1. 需求已有完整 spec 且未发生变更——直接进入 `/write-plan`
2. 纯 bugfix 且影响范围明确（<=2 文件、单模块）——可直接修复
3. 用户只是问问题或做研究，不涉及实施交付
4. 已处于 `/execute-plan` 执行阶段，不应回退重写规格

## 目标

在实施前先生成可执行的轻量规格，并计算任务等级。

默认输出路径：

`docs/specs/YYYY-MM-DD-<name>-spec-lite.md`

## 输入参数

`/spec-lite <需求描述> [tierOverride=L|M|H] [overrideReason=...] [explore=true|false]`

## 任务分类（新增）

在生成 spec 之前，先将任务归类为以下之一：

1. `new-feature`
2. `bugfix`
3. `refactor`
4. `test`
5. `research`
6. `review-pr`
7. `issue-draft-pr`
8. `parallel-delivery`

若用户未明确说明，默认按 `new-feature` 处理。

同时给出推荐 workflow：

- `new-feature` -> `spec-first`
- `bugfix` -> `bugfix`
- `refactor` -> `minimal-refactor`
- `test` -> `test-first`
- `research` -> `research-only`
- `review-pr` -> `review-pr`
- `issue-draft-pr` -> `issue-draft-pr`
- `parallel-delivery` -> `parallel-delivery`

## 通用需求澄清与方向确认（硬门禁）

在生成 spec 前，必须先确认以下信息：

1. 业务目标与成功标准（判定完成的标准）
2. 用户/调用方与使用场景
3. 触发入口与交互路径（API/CLI/定时/UI/任务）
4. 交付形态（接口/命令/任务/页面/配置）
5. 关键数据对象与范围边界（新增/修改/不改）
6. 外部契约与兼容性影响
7. 非功能约束（性能/安全/稳定性/合规）
8. 观测与运维要求（日志/监控/告警）
9. 日志策略（复用项目日志结构；日志英文；默认禁控制台）

AI 必须给出 2-3 个实现方向供用户确认，每个方向至少包含：

1. 核心思路
2. 主要收益
3. 主要代价/风险
4. 适用前提

若任一项缺失或含 `TBD/待定/未确认`：

1. 返回 `GateResult.status=blocked`
2. `missing[]` 列出未确认项
3. `nextCommand` 指向补充信息后重试 `/spec-lite`
4. 不得推荐进入 `/write-plan`

若用户明确“不接受当前方向”，还必须补充：

1. 可接受的替代方向
2. 不可触碰约束（必须/禁止）

否则同样 `BLOCKED`。

日志相关补充约束：

1. 旧项目：必须先说明“已识别并沿用”的原有日志结构（框架、字段、级别、traceId 传递方式）
2. 新项目：必须在澄清/brainstorm 中确定日志框架与结构化字段
3. 若日志策略未明确，禁止进入 `/write-plan`

## 资源加载规则

到达步骤 7（生成 GateContext/TaskContract）或步骤 11（写入规格文档）时，**必须先读取 `references/gate-context-fields.md`**，获取所有字段定义后再填写。

在此之前不要提前加载。

## 评分规则

- 变更文件数：`<=2:+0, 3-6:+1, >=7:+2`
- 影响模块数：`1:+0, 2:+1, >=3:+2`
- 外部契约变更（API/DB/Event/Config）：`+3`
- 安全/权限域变更：`+3`
- 数据/状态迁移：`+2`
- 关键路径性能影响：`+1`
- 线上故障修复：`+1`

等级映射：

- 0-2 => L
- 3-6 => M
- >=7 => H

## 混合覆盖策略

1. 先计算 `recommendedTier`
2. 若提供 `tierOverride`，则 `overrideReason` 必填
3. 缺少覆盖理由时直接 `BLOCKED`
4. `finalTier = tierOverride 或 recommendedTier`

## 执行流程

1. 读取 `template.md`
2. 先进行任务分类，确定 `taskType` 与 `workflow`
3. 执行通用需求澄清，补齐所有必填项
4. 输出 2-3 个实现方向并获取用户确认
5. 若存在缺失项或方向未确认，直接阻断并返回补充问题清单
6. 填写目标、范围外、接口/数据影响、澄清结论、方向确认记录、风险、验收、回滚
7. 结合任务类型，从 `.codebuddy/templates/task-contracts/` 选择对应模板并生成 `TaskContract`
8. 将合同压缩为 agent 可执行的最小字段：目标、边界、验证、证据、owner、超边界处理
9. 计算评分并得到 `recommendedTier`
10. 应用覆盖策略并得到 `finalTier`
11. 写入规格文档与 `GateContext`、`TaskContract`
12. 若当前需求已先完成 `/brainstorm`，优先回填 `brainstormPath`；其余 AI2AI 追踪链接允许先占位
13. 返回 `GateResult`：
   - `H` -> 下一步 `/brainstorm <需求描述> spec=<specPath> tier=H`
   - `L/M` -> 下一步 `/write-plan spec=<specPath> tier=<finalTier>`

## 复杂任务的覆盖矩阵约束（强制）

当上游已存在以下任一文档时，**spec-lite 必须把它作为输入**并生成"需求覆盖矩阵"：

- `docs/plans/<...>-需求预分析.md`（来自 `/brainstorm`）
- `docs/specs/<...>-requirement-analysis.md`（来自 `/extend` Step 0.4）

矩阵要求：

1. 列：`需求项 ID | 需求描述 | spec 章节 | 计划任务 ID | 验证用例 ID | 状态`
2. 矩阵必须**逐项**回链到上游文档的需求项，禁止合并 / 摘要
3. spec-lite 自身**不得引入上游文档未列出的需求项**（YAGNI 强约束）
4. 任何需求项未填齐"spec 章节 + 计划任务 ID + 验证用例 ID" → 阻断进入 `/write-plan`
5. 矩阵保存在 spec 文档末尾"## 需求覆盖矩阵"章节，并写入 `GateContext.coverageMatrixPath`

## 待决策项持久化（强制）

spec-lite 的"通用需求澄清 + 2~3 个方向比较"天然会产生多个待决策项。任何一次回复抛出 ≥ 2 个澄清问题
或方向对比选项，或 Boss 只回答了部分项时，**必须**按 `.codebuddy/skills/pending-decisions/SKILL.md` 落盘到
`docs/pending-decisions.md`，禁止把待决策项只留在对话上下文里。

具体协议：

1. 抛问前自检：本轮抛给 Boss 的问题/选项数量 N，N ≥ 2 → 先写 pending-decisions.md，并把 `linkedDocs` 指向当前 specPath
2. 回复合并：每收到 Boss 回复，更新对应项 `status`；`answered` 的结论同步回 spec 的"澄清结论 / 方向确认"章节
3. 进入下游门禁（`/write-plan`）前：跑 `/pending sweep`；存在 pending/partial 项视为澄清未完成，返回 `BLOCKED`

## 禁止事项

1. 不要在澄清项存在 `TBD/待定/未确认` 时放行进入下游——因为未澄清的规格会导致计划和实现全部返工
2. 不要跳过方向评估直接输出单一方案——因为缺乏对比会掩盖风险和替代路径
3. 不要在用户否决方向后仍沿用原方案继续——因为这会产生不符合预期的交付物
4. 不要手动硬编码 `finalTier` 绕过评分规则——因为等级决定下游门禁深度，错误等级会导致流程缺失或过度
5. 不要把 spec 文档当作最终设计文档使用——spec-lite 只提供轻量规格，详细设计应在 brainstorm 或 plan 阶段补充
6. 不要在已有上游需求分析文档时跳过覆盖矩阵——下游审查与系统测试都依赖这张矩阵做断言
7. 不要在一次回复抛出 ≥ 2 个澄清问题却跳过 `docs/pending-decisions.md` 持久化——待决策项在多轮对话中极易丢失
