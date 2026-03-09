# Bugfix / Refactor / Test 工作流

维护类任务不应该混做。`devflow-ai` 将 bugfix、refactor、test 三类任务分开定义。

## Bugfix

- 推荐入口：`/fix-bug`
- 推荐合同：`.codebuddy/templates/task-contracts/bugfix.md`
- 推荐顺序：复现 -> 根因 -> 最小修复 -> 最小复现关闭 -> 回归
- 完成证据：根因说明、最小修复 diff、回归结果、剩余风险

## Refactor

- 推荐入口：`/write-plan`，必要时执行 `/simplify`
- 推荐合同：`.codebuddy/templates/task-contracts/refactor.md`
- 推荐顺序：定义行为不变项 -> 限定改动目录 -> 小步重构 -> 行为验证
- 完成证据：行为不变证明、结构收益、剩余风险

## Test

- 推荐入口：`/test-gen` 或 `/unified-test`
- 推荐合同：`.codebuddy/templates/task-contracts/test.md`
- 推荐顺序：覆盖目标 -> 主路径/边界条件 -> 测试计划 -> 测试实现 -> 执行结果 -> 覆盖缺口
- 完成证据：测试输出、覆盖率、缺口说明

## 不要混做

- 修 bug 时不要顺手做结构重写
- 做 refactor 时不要夹带新需求
- 补测试时不要默认修改业务逻辑
