请阅读以下技能并严格遵循：
1. `.codebuddy/skills/code-documentation/SKILL.md`（三层代码自文档体系）
2. `.codebuddy/skills/project-reading/SKILL.md`（项目阅读与理解）

**务必遵守三条铁律：**
1. 每次回复先称呼 "Boss"
2. 不确定的设计问题必须先问 Boss
3. 不写兼容性代码，除非 Boss 主动要求

**你的任务是：为项目初始化三层代码自文档体系。**

执行步骤：
1. **调用 code-explorer agent 进行全量代码阅读**：
   - 将目标路径（或整个项目）交给 code-explorer agent
   - agent 使用 list_files 列出所有源码文件清单
   - agent 使用 read_file 逐个完整阅读所有源码文件（遵守 project-reading 规则，禁止抽样）
   - agent 返回结构化的逐文件分析结果（详见下方输出格式）
2. 基于 agent 返回的分析结果，识别所有需要注释的源码文件（排除自动生成代码、第三方代码）
3. 识别所有需要 CONTEXT.md 的业务目录
4. **检查幂等性**：已有 INPUT/OUTPUT/POS 注释的文件更新内容，不重复添加
5. 基于 agent 的逐文件分析结果，为每个源码文件生成头部三行注释
6. 基于 agent 的目录分析结果，为每个业务模块目录生成 CONTEXT.md
7. 自底向上逐级汇总，生成上层目录的 CONTEXT.md
8. 向 Boss 展示文档结构，确认无误后批量写入

**如果指定了路径参数，则只初始化该路径下的文件和目录。**

$ARGUMENTS
