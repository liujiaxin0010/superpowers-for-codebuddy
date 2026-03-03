请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/test-driven-development/SKILL.md`（TDD）
3. `.codebuddy/skills/custom-testing/SKILL.md`（自定义测试）
4. `.codebuddy/skills/test-driven-development/testing-anti-patterns.md`（测试反模式）
5. `.codebuddy/skills/unified-test/SKILL.md`（.vue/.go 统一测试）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
生成并执行测试，但必须先通过门禁。

执行步骤：
1. 解析参数：`target`，可选 `spec=<path>`、`tier=<L|M|H>`、`options.goProfile`
2. 调用 `process-gatekeeper`（`command=test-gen`）
3. 若阻断：输出阻断报告并停止
4. 按文件类型路由：
   - `.vue/.go` -> `unified-test`（推荐 `mode=full`）
   - 其他 -> `custom-testing`
5. 输出结构化结果（通过率、覆盖率、修复轮次）

$ARGUMENTS
