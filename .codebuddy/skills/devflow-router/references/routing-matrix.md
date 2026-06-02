# Routing Matrix

| 用户意图 | 任务类型 | 推荐命令 | 缺少前置时回退 |
|---|---|---|---|
| 模糊需求（必须先澄清） | `new-feature` 或 `unknown` | `/brainstorm` | 补目标、范围、验收或方向选择 |
| 模糊需求（建议先澄清） | `new-feature` | `/brainstorm`（优先） / `/spec-lite`（最小字段齐备时） | 补验收、入口、边界条件 |
| 加功能、做需求 | `new-feature` | `/spec-lite` | 补需求澄清 |
| 写需求规格/功能清单 | `new-feature` | `requirement-spec`（需求规格列表）| 补开发背景 |
| 编码前对齐架构/接口 | `new-feature` | `/walkthrough`（概要/详细串讲）| 补 spec / 计划草案 |
| 校验 spec 目录结构 | `new-feature` | `/spec-check` | 补 spec/ 结构 |
| 规格与代码同步回填 | 任意 | `/spec-sync` | 无 spec/ → spec-organization |
| 修问题、关缺陷 | `bugfix` | `/fix-bug`（单次）/ `/defect-loop`（批量闭环）| 补复现条件 |
| 接 GitLab 定时自动化 | 任意 | `/schedule-setup` | 先 `/ci-setup` |
| 整理结构、行为不变 | `refactor` | `/write-plan` | 补行为边界 |
| 写测试、补覆盖 | `test` | `/test-gen` / `/unified-test` | 补测试目标 |
| 先分析再建议 | `research` | `/research` | 补研究问题 |
| 做审查、看 diff | `review-pr` | `/code-review` | 补 diff / owner |
| 工单到 PR | `issue-draft-pr` | `/issue-draft-pr` | 补 acceptance criteria |
| 长任务并行推进 | `parallel-delivery` | `/parallel-delivery` | 补 plan / lane 拆分 |

## 模糊需求判定速查

### `must-brainstorm`

以下表达默认视为必须先 `/brainstorm`：

- “帮我做一个 XX”
- “给这个模块升级一下”
- “优化一下这里”
- “重构下这个功能”
- “搞一个类似 XX 的能力”

前提是用户没有同时给出明确边界、验收标准和受影响范围。

### `should-brainstorm`

以下情况默认视为建议先 `/brainstorm`：

- 已经给了目标，但验收仍然很粗
- 已经给了模块，但入口和边界条件不清
- 已经给了初步方案，但没有明确选方向
