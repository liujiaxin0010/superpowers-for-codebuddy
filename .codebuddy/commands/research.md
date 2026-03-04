请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/research/SKILL.md`（工程研究）
3. `.codebuddy/skills/file-based-memory/SKILL.md`（持久化记忆）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

你的任务是：
执行 research 阶段，输出工程研究结果并回填兼容文档。

执行步骤：
1. 解析参数：`/research <需求或模块> [spec=<path>] [tier=<L|M|H>]`
2. 调用 `process-gatekeeper`（`command=research`）
3. 若阻断：输出阻断报告并停止
4. 读取 `spec/Me2AI/需求描述.md` 与 `spec/Me2AI/技术约束.md`（存在则优先）
5. 对目标工程做只读分析（架构、规范、风格、候选改动点）
6. 输出并更新 `spec/AI2AI/research.md`
7. 若提供 `spec=<path>`，回填该 spec 的追踪链接 `researchPath`

$ARGUMENTS
