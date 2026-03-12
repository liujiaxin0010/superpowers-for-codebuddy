# 任务工作流目录

团队不需要为每个任务重新设计流程。`Featureflow` 采用“任务类型 -> 默认入口 -> 合同模板 -> 门禁 -> 证据收口”的固定链路。

## 六类高频任务

| 任务 | 最小流程 | 默认入口 | 合同模板 |
|---|---|---|---|
| bugfix | 复现 -> 根因 -> 最小修复 -> 回归 | `/fix-bug` | `.codebuddy/templates/task-contracts/bugfix.md` |
| refactor | 行为边界 -> 重构计划 -> 小步修改 -> 行为验证 | `/write-plan` | `.codebuddy/templates/task-contracts/refactor.md` |
| test | 测试计划 -> 用例实现 -> 执行结果 -> 覆盖缺口 | `/test-gen` / `/unified-test` | `.codebuddy/templates/task-contracts/test.md` |
| new feature | spec -> plan -> execute -> verify -> review | `/spec-lite` | `.codebuddy/templates/task-contracts/new-feature.md` |
| research | 问题定义 -> 信息收集 -> 结论 -> 建议 | `/research` | `.codebuddy/templates/task-contracts/research.md` |
| review / PR | diff 审阅 -> 证据检查 -> 风险声明 -> merge | `/code-review` | `.codebuddy/templates/task-contracts/review-pr.md` |

## 扩展工作流

| 任务 | 组合入口 | 合同模板 |
|---|---|---|
| issue / Jira -> draft PR | `/issue-draft-pr` | `.codebuddy/templates/task-contracts/issue-draft-pr.md` |
| parallel delivery | `/parallel-delivery` | `.codebuddy/templates/task-contracts/parallel-delivery.md` |

## 统一合同字段

- 任务目标
- 范围边界
- 可编辑位置
- 验证命令
- 交付证据
- 人工确认点
- owner
- 超边界时的处理方式

## 对应门禁

- spec / 合同完整性：`.codebuddy/skills/process-gatekeeper/SKILL.md`
- 完成前验证：`.codebuddy/rules/verification-before-completion.md`
- 质量门禁：`.codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1`
