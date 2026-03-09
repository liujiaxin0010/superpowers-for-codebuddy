# 任务类型选择

## 默认映射

| 用户意图 | 任务类型 | 默认入口 |
|---|---|---|
| 新功能、跨模块需求 | `new-feature` | `/spec-lite` |
| 缺陷关闭、最小修复 | `bugfix` | `/fix-bug` |
| 结构收敛、行为不变 | `refactor` | `/write-plan` |
| 补测、覆盖、回归 | `test` | `/test-gen` / `/unified-test` |
| 只读分析、给建议 | `research` | `/research` |
| 审查、合并判断、风险声明 | `review-pr` | `/code-review` |
| 工单驱动的 draft PR | `issue-draft-pr` | `/issue-draft-pr` |
| 多 lane 长任务 | `parallel-delivery` | `/parallel-delivery` |

## 选择规则

1. 如果目标是“关闭已知错误”，优先 `bugfix`
2. 如果目标是“加功能”，优先 `new-feature`
3. 如果目标是“保持行为不变地整理结构”，优先 `refactor`
4. 如果目标是“补测试”，优先 `test`
5. 如果目标是“先研究再决策”，优先 `research`
6. 如果看起来是 `new-feature`，但需求边界不清、方向未定或验收模糊，先判断：
   - 严重模糊 -> `must-brainstorm`
   - 轻度模糊 -> `should-brainstorm`
7. `must-brainstorm` 不直接进入执行链；`should-brainstorm` 默认也优先回退到 `/brainstorm`
