请阅读以下技能并严格遵循：
1. `.codebuddy/rules/code-documentation.md`（三层代码自文档体系）
2. `.codebuddy/rules/gitnexus-code-intelligence.md`（GitNexus 代码智能）
3. `.codebuddy/rules/project-reading.md`（项目阅读与理解 → 仅在降级时使用）

**务必遵守三条铁律：**
1. 每次回复先称呼 "Boss"
2. 不确定的设计问题必须先问 Boss
3. 不写兼容性代码，除非 Boss 主动要求

**你的任务是：为项目初始化三层代码自文档体系。**

**第零步：环境检查**
1. 执行 GitNexus 可用性检查（见 gitnexus-code-intelligence 规则）
2. 若不可用，提示 Boss 执行 `npx gitnexus analyze && npx gitnexus setup`
3. 若 Boss 选择不使用 GitNexus，则降级到手动方案（加载 project-reading.md，走 code-explorer agent 全量阅读流程）

**第一步：通过 GitNexus 获取项目全局结构**
- 使用 **模式 E**（全局结构查询）获取项目模块划分
- 使用 **模式 B**（模块全景查询）获取各目录下的文件清单和关系
- 识别所有需要注释的源码文件（排除自动生成代码、第三方代码）
- 识别所有需要 CONTEXT.md 的业务目录

**第二步：批量提取 INPUT/OUTPUT/POS**
对每个源码文件：
1. 使用 **模式 A**（文件 360° 上下文）获取依赖/导出/定位
2. 按数据翻译规则将技术数据转为业务语言三行注释
3. 检查幂等性：已有注释的文件更新内容，不重复添加

**第三步：生成 CONTEXT.md**
对每个业务模块目录：
1. 使用 **模式 B** 获取模块内全部文件和关系
2. 地位 → 模块的 Community 角色 + 连接度
3. 逻辑 → 模块内的执行流（Process 节点）
4. 约束 → **需要 AI 补充阅读**（GitNexus 不分析业务约束规则）
5. 业务域清单 → 模块内文件/符号列表

**第四步：AI 精准补充（非全量阅读）**
仅针对 GitNexus 无法提供的信息：
1. 约束信息：阅读配置文件和校验逻辑代码段
2. 动态 import/反射调用等 Tree-sitter 可能遗漏的场景
3. 业务比喻翻译中不确定的部分

**第五步：向 Boss 展示文档结构，确认无误后批量写入**

**如果指定了路径参数，则只初始化该路径下的文件和目录。**

$ARGUMENTS
