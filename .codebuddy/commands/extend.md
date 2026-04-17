请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/extending-project/SKILL.md`（项目扩展工作流）
3. `.codebuddy/rules/project-reading.md`（项目阅读：三层文档→GitNexus→手动 优先级铁律）
4. `.codebuddy/rules/gitnexus-code-intelligence.md`（含模式 G 基线刷新）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在门禁约束下执行"先理解原实现 → 沉淀历史规格 → 头脑风暴 → 输出扩展需求分析规格 → 再选实施流程"的扩展入口编排。

执行步骤：

1. 解析参数：`spec=<path>`、`tier=<L|M|H>`、`requirement=<扩展需求描述>`
2. 若缺少 `requirement`：直接输出 `BLOCKED`，要求补充扩展需求描述
3. **Step 0.1 项目理解（强制）**：
   - 严格按 `project-reading.md` 的优先级：三层文档 → GitNexus（先做模式 G 基线对比/刷新） → 手动阅读
   - 在 `docs/progress.md` 写入：信息源、降级原因、覆盖率
   - 若 GitNexus 基线漂移 `riskLevel=high` 且未刷新 → BLOCKED
4. **Step 0.2 生成历史实现规格 spec（强制）**：
   - 路径：`docs/specs/YYYY-MM-DD-<模块名>-historical-spec.md`
   - 模板：`.codebuddy/skills/extending-project/templates/historical-spec-template.md`
   - 内容必须详细、来源可追溯，**完整提交 Boss 核实**
   - Boss 未打勾确认前 → BLOCKED，并在 `docs/progress.md` 记录阻断
5. **Step 0.3 头脑风暴（强制）**：
   - 触发 `/brainstorm <扩展需求> historicalSpec=<historicalPath>`
   - 七阶段中必须显式列出与历史规格的"复用 / 扩展 / 替换 / 废弃"决策
   - 输出：`docs/plans/YYYY-MM-DD-<需求名称>-需求预分析.md`
6. **Step 0.4 生成扩展需求分析规格 spec（强制）**：
   - 路径：`docs/specs/YYYY-MM-DD-<需求名称>-requirement-analysis.md`
   - 模板：`.codebuddy/skills/extending-project/templates/requirement-analysis-template.md`
   - 必须包含"需求 → 设计 → 实现 → 验证"追溯矩阵
   - **完整提交 Boss 核实**，未打勾前 → BLOCKED
7. 若 `tier` 缺失：调用 `/spec-lite` 完成轻量规格与分级，并将 `requirement-analysis.md` 作为输入挂到 `brainstormPath` 之外的"需求分析 spec"位置（`requirementAnalysisPath` 字段，允许新增）
8. 调用 `process-gatekeeper`（`command=extend`）
9. 若门禁阻断：输出阻断报告并停止
   - 同步更新 `docs/progress.md`：阻断项 / 修复动作 / 重试命令
   - 同步更新 `docs/findings.md`：新的阻断模式或门禁观察结论
10. 若通过：按等级分流
    - `L/M`：进入 `/write-plan spec=<requirementAnalysisPath> tier=<finalTier>`
    - `H`：直接进入 `/write-plan spec=<requirementAnalysisPath> tier=H`（头脑风暴已在 Step 0.3 完成）
11. 同步更新 `docs/progress.md`：记录 finalTier、分流结果、下一条命令
12. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

补充约束：

- 任何一步缺失 Boss 核实 → BLOCKED，绝不能"为效率"跳过
- `/extend` 不直接写实现代码，只编排前置流程

$ARGUMENTS
