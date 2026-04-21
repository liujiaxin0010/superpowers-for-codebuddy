请阅读以下技能并严格遵循：
1. `.codebuddy/rules/code-documentation.md`（三层代码自文档体系）
2. `.codebuddy/rules/gitnexus-code-intelligence.md`（GitNexus 代码智能）
3. `.codebuddy/rules/project-reading.md`（项目阅读与理解 → 仅在降级时使用）

**务必遵守三条铁律：**
1. 每次回复先称呼 "Boss"
2. 不确定的设计问题必须先问 Boss
3. 不写兼容性代码，除非 Boss 主动要求

**你的任务是：为项目初始化三层代码自文档体系（CONTEXT.md 为主力，源码头部注释为可选标签）。**

**第零步：环境检查**
1. 执行 GitNexus 可用性检查（见 gitnexus-code-intelligence 规则）
2. 若不可用，提示 Boss 执行 `npx gitnexus analyze && npx gitnexus setup`
3. 若 Boss 选择不使用 GitNexus，则降级到手动方案（加载 project-reading.md，按 `四步法` 全量阅读目标范围代码）

**第零点五步：向 Boss 询问两项初始化决策**
1. **是否写入源码头部三行注释？**
   - ✅ 是：作为"一次性初始化标签"写入；**后续 `/doc-sync` 不再更新**，只有再次 `/doc-init --rebuild` 才会刷新
   - ❌ 否：跳过源码修改，只生成 `CONTEXT.md`（推荐默认选项，保持源码干净）
2. **核心模块标注**：根据 GitNexus 模式 E 的 blast radius，AI 提出哪些目录属于 L1 核心模块（Controller/Service/领域核心），请 Boss 确认
   - 记录到 `.codebuddy/state/doc-level.json`：`{ "src/user": "L1", "src/common/utils": "L0", ... }`
   - `/doc-sync` 后续按此文件决定哪些目录追加 L1 节（⑦ 数据流 / ⑧ 扩展点 / ⑨ 故障模式）

**第一步：通过 GitNexus 获取项目全局结构**
- 使用 **模式 E**（全局结构查询）获取项目模块划分
- 使用 **模式 B**（模块全景查询）获取各目录下的文件清单和关系
- 识别所有需要文档的源码文件（排除自动生成代码、第三方代码）
- 识别所有需要 `CONTEXT.md` 的业务目录

**第二步：批量提取 INPUT/OUTPUT/POS（仅当 Boss 选择写入头部注释时）**
对每个源码文件：
1. 使用 **模式 A**（文件 360° 上下文）获取依赖/导出/定位
2. 按数据翻译规则将技术数据转为业务语言三行注释
3. 检查幂等性：已有注释的文件**跳过**（不重复添加），不存在时才写入
> 如果 Boss 在第零点五步选择不写入头部注释，本步骤完全跳过

**第三步：生成 `CONTEXT.md`（所有目录都要做）**
对每个业务模块目录，按 `code-documentation.md` 的 L0/L1/L2 分层规则生成：
1. 使用 **模式 B** 获取模块内全部文件和关系
2. **L0 六节**（所有目录）：地位 / 逻辑 / 约束 / Inventory / 调用关系（Mermaid 图）/ 设计决策与踩坑（首次为空）
3. **L1 三节**（标注为核心模块的目录追加）：数据流 / 扩展点 / 故障模式
4. **L2 三节**（按 Boss 需求）：可观测性 / 测试策略 / 变更锚点

**第四步：AI 精准补充（非全量阅读）**
仅针对 GitNexus 无法提供的信息：
1. 约束信息：阅读配置文件和校验逻辑代码段
2. 动态 import / 反射调用等 Tree-sitter 可能遗漏的场景
3. 业务比喻翻译中不确定的部分
4. § ⑧ 扩展点的"不动区"——必须提交 Boss 确认，不得 AI 自决

**第五步：向 Boss 展示文档结构，确认无误后批量写入**
- 列出本次将创建/修改的 `CONTEXT.md` 清单
- 列出本次是否写入源码头部注释（如 Boss 授权）
- 展示核心模块 L1 标注的 `.codebuddy/state/doc-level.json` 内容

**如果指定了路径参数，则只初始化该路径下的文件和目录。**

$ARGUMENTS
