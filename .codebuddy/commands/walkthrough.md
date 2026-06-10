请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/walkthrough/SKILL.md`（串讲设计对齐）
3. `.codebuddy/skills/pending-decisions/SKILL.md`（待决策项持久化）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在编码前主持设计串讲，对齐架构方向 / 模块边界（概要）或接口契约 / 数据流 / 联调风险（详细），产出 committed 串讲纪要。**串讲必须有 Boss 对每个议题的确认结论，不得自问自答。**

执行步骤：

1. 解析参数：`layer=<概要|详细>`（默认按上下文判断）、`spec=<path>`
2. 判定串讲层级：
   - 概要：方案设计后、`/write-plan` 前 → 对齐架构方向 + 模块边界
   - 详细：`/write-plan` 后、`/execute-plan` 前 → 锁定接口契约 + 数据流 + 联调风险
3. 门禁检查：无有效 spec（概要）或无计划草案（详细）→ 输出阻断并回退上游
4. 读 spec，按 `walkthrough/references/two-layer-walkthrough.md` 列出本层议题清单
5. **逐议题主持**（一次一个）：展示现状 + AI 提案 → 等 Boss 确认 / 质疑 → 记录结论
6. 出现 ≥2 项未决议题 → 立即落 `docs/pending-decisions.md`（经 `/pending`）
7. 按 `walkthrough/templates/walkthrough-minutes.md` 产出纪要，committed 到 `docs/specs/{date}-{slug}-walkthrough.md`
7.5 **ADR 沉淀（OPT-P2）**：经 Boss 确认的**架构级**结论（选型 / 模块边界 / 契约约定——会约束后续多个计划的那类）按 `walkthrough/templates/adr-template.md` 落 `docs/adr/NNN-<slug>.md`，纪要中引用 ADR 编号；普通实现细节结论留在纪要即可，**不要为每条结论都开 ADR**
8. 回填 spec-lite 追踪字段：概要 → `walkthroughPath`；详细 → `detailWalkthroughPath`
9. 输出下一步：概要 → `/write-plan`；详细 → `/execute-plan`

补充约束：
- 概要层只对齐方向与边界，不陷入实现细节；接口契约留到详细层
- 接口契约必须精确到字段（入参/出参/错误码），内部实现路径留白
- 每条结论标注是否经 Boss 确认；未确认不算对齐
- 关键分歧未决（≥2 项）时不得放行下游命令

$ARGUMENTS
