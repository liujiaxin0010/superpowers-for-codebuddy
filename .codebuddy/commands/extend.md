请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/extending-project/SKILL.md`（项目扩展工作流）
3. `.codebuddy/skills/project-reading/SKILL.md`（项目阅读）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在门禁约束下执行“先判档再选流程”的扩展入口编排。

执行步骤：
1. 解析参数：`spec=<path>`、`tier=<L|M|H>`
2. 若缺少 `spec` 或 `tier`：直接输出 `BLOCKED`，并引导执行 `/spec-lite <需求描述>`
3. 调用 `process-gatekeeper`（`command=extend`）
4. 若门禁阻断：输出阻断报告并停止
5. 若通过：按等级分流
   - `L/M`：进入 `/write-plan spec=<specPath> tier=<finalTier>`
   - `H`：先执行 `/brainstorm <需求描述>`（完整七阶段）再进入计划编排

$ARGUMENTS
