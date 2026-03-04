请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/testcase/SKILL.md`（测试用例产出）
3. `.codebuddy/skills/file-based-memory/SKILL.md`（持久化记忆）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

你的任务是：
在门禁约束下产出测试用例与覆盖分析文档。

执行步骤：
1. 解析参数：`target=<pathOrModule> spec=<path> plan=<path> [tier=<L|M|H>]`
2. 调用 `process-gatekeeper`（`command=testcase`）
3. 若阻断：输出阻断报告并停止
4. 校验输入文档：`spec/AI2AI/Design.md`、`spec/AI2AI/Architecture_Info.md`、`spec/AI2AI/Protocol_and_Data.md`
5. 生成测试用例文档：`spec/AI2AI/testcase.md`
6. 生成覆盖分析文档：`spec/AI2AI/testcase_analysis.md`
7. 回填 spec 追踪链接：`testcasePath`、`testcaseAnalysisPath`
8. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
