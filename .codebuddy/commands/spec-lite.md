请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/spec-lite/SKILL.md`（轻量规格生成与 L/M/H 分级）
2. `.codebuddy/skills/task-contracts/SKILL.md`（统一任务合同）
3. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
4. `.codebuddy/skills/file-based-memory/SKILL.md`（持久化记忆）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
执行 `/spec-lite`，并输出 `GateContext` 与 `GateResult`。

执行步骤：
1. 解析参数：`/spec-lite <需求描述> [tierOverride=L|M|H] [overrideReason=...] [explore=true|false]`
2. 先识别任务类型：`new-feature|bugfix|refactor|test|research|review-pr|issue-draft-pr|parallel-delivery`
3. 再执行“通用需求澄清”：
   - 业务目标与成功标准
   - 用户/调用方与使用场景
   - 触发入口与交互路径（API/CLI/定时/UI/任务）
   - 交付形态（接口/命令/任务/页面/配置）
   - 关键数据对象与边界（新增/修改/不改）
   - 非功能约束（性能/安全/稳定性/合规）
   - 日志策略（沿用现有日志结构/新项目日志框架选型、英文日志、禁控制台）
4. AI 需发散给出 2-3 个可行实现方向（含优缺点与风险），让用户确认
5. 若用户不接受已有方向，必须明确“替代方向或硬约束”；否则返回 `BLOCKED`
6. 若澄清项或方向确认仍缺失、模糊或为 `TBD/待定`：返回 `BLOCKED` 并停止，不得进入计划阶段
7. 根据任务类型选择 `.codebuddy/templates/task-contracts/*.md` 生成 `TaskContract`
8. 将合同压缩成 agent 最小合同：目标、边界、验证、证据、owner、超边界处理
9. 生成 `docs/specs/YYYY-MM-DD-<需求名称>-spec-lite.md`
10. 计算 `recommendedTier`
11. 若存在 `tierOverride` 但缺少 `overrideReason`，返回 `BLOCKED` 并停止
12. 将 `GateContext` 与 `TaskContract` 写入规格文档
13. 初始化并写入“追踪链接”字段（允许占位；`spec/AI2AI/*` 由后续阶段按需回填，不要求在 spec 阶段一次性创建完毕）：
   - `brainstormPath`（若当前需求已先完成 `/brainstorm`，优先回填）
   - `researchPath`
   - `designPath`
   - `testStrategyPath`
   - `testcasePath`
   - `testcaseAnalysisPath`
   - `implementationProgressPath`
   - `implementationSummaryPath`
14. 返回 `GateResult` 与下一条推荐命令：
   - `L/M`：`/write-plan spec=<specPath> tier=<finalTier>`
   - `H`：`/brainstorm <需求描述> spec=<specPath> tier=H`（强制完整七阶段；若已先做过 brainstorm，则需确保 `brainstormPath` 已回填）
15. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
