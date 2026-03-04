请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/brainstorming/SKILL.md`（七阶段头脑风暴）
3. `.codebuddy/skills/brainstorming/requirement-doc-template.md`（需求预分析模板）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
执行完整七阶段头脑风暴流程。

执行步骤：
1. 先执行 `process-gatekeeper` 上下文检查（`command=brainstorm`）
2. 若 `finalTier=H`，必须执行完整七阶段
3. 若 `finalTier=L/M`，可按需执行完整流程
4. 在可维护性设计中明确日志方案（沿用结构或新项目框架选型、English only、禁控制台）
5. 输出需求预分析文档，并与后续计划执行链路关联
6. 同步兼容文档：
   - `spec/AI2AI/Design.md`
   - `spec/AI2AI/test.md`
7. 若提供 `spec=<path>`，回填追踪链接：
   - `designPath: spec/AI2AI/Design.md`
   - `testStrategyPath: spec/AI2AI/test.md`
8. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
