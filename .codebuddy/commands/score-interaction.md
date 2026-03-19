请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/ai-interaction-scoring/SKILL.md`（评分维度与规则）
2. `.codebuddy/skills/ai-interaction-scoring/scoring-rules.json`（评分配置）
3. `.codebuddy/skills/ai-interaction-scoring/templates/score-report-template.md`（报告模板）
4. `.codebuddy/skills/xlsx/SKILL.md`（XLSX 输出）

你的任务是：
评估一段 AI 编码助手的对话，生成结构化的质量评分报告。

执行步骤：
1. 解析可选参数：`task=<任务描述>`、`outputDir=<输出路径>`
2. 接收对话内容（粘贴文本、文件路径或当前对话上下文）
3. 识别任务类型，确定 5 个与任务相关的核心交付物
4. 在 4 个评分维度中收集证据：
   - **维度一（Spec-Coding 规范，10 分）**：检查需求澄清、方向评估、规格文档、实施计划、持久化文档、门禁检查
   - **维度二（Skills/Agent 使用，5 分）**：统计不同技能/Agent 的调用次数（去重）
   - **维度三（项目完成度，10 分）**：按证据级别（完整/部分/无）评估每个交付物。用户反馈的故障优先于代码证据
   - **维度四（扩展功能与美化，5 分）**：检查是否有超出基本需求的功能和界面美化
5. 检测反模式：虚假完成、过早编码、Bug 修复循环、忽略用户反馈
6. 计算各维度得分及总分
7. 识别亮点（优势与不足）
8. 生成改进建议
9. 使用模板输出 `ai-interaction-scoring-report.md`
10. 使用 xlsx 技能输出 `ai-interaction-scoring-report.xlsx`

评分约束：
- 基于**对话中的证据**评分，而非假设
- 证据模糊时，采用保守评分（偏低）
- 用户关于功能的陈述优先于代码分析
- 编译成功**不**足以作为"功能正常"的充分证据
- 各维度独立评分
- 报告中每个得分必须有可追溯的证据引用
- 反模式即使不影响评分也必须标记

输出要求：
- 报告语言与对话语言一致（中文对话 = 中文报告）
- XLSX 内容使用中文表头和描述
- 所有得分必须有可追溯的证据
- 改进建议必须具体、可操作

$ARGUMENTS
