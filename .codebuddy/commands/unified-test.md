---
description: 前后端统一单元测试入口（.vue/.go）
---

# /unified-test 前后端统一单元测试

请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/unified-test/SKILL.md`（统一测试）
3. `.codebuddy/skills/test-driven-development/SKILL.md`（TDD）
4. `.codebuddy/skills/test-driven-development/testing-anti-patterns.md`

你的任务是：
针对 `.vue` 或 `.go` 目标执行统一测试流程。

执行步骤：
1. 解析参数：`targetFile/testFile/mode/options/spec/tier`
2. 调用 `process-gatekeeper`（`command=unified-test`）
3. 若阻断：输出阻断报告并停止
4. 若通过，执行：
   - `full`：生成 -> 执行 -> 修复 -> 覆盖率 -> 迭代
   - `generate`：仅生成
   - `execute`：仅执行/修复
   - `coverage`：仅覆盖率迭代
5. 输出结构化总结
6. 若目标不是 `.vue/.go`，提示改用 `/test-gen`

$ARGUMENTS
