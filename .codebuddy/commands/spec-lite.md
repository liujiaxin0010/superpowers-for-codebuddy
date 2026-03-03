请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/spec-lite/SKILL.md`（轻量规格生成与 L/M/H 分级）
2. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
3. `.codebuddy/skills/file-based-memory/SKILL.md`（持久化记忆）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
执行 `/spec-lite`，并输出 `GateContext` 与 `GateResult`。

执行步骤：
1. 解析参数：`/spec-lite <需求描述> [tierOverride=L|M|H] [overrideReason=...] [explore=true|false]`
2. 先执行“通用需求澄清”：
   - 业务目标与成功标准
   - 用户/调用方与使用场景
   - 触发入口与交互路径（API/CLI/定时/UI/任务）
   - 交付形态（接口/命令/任务/页面/配置）
   - 关键数据对象与边界（新增/修改/不改）
   - 非功能约束（性能/安全/稳定性/合规）
   - 日志策略（沿用现有日志结构/新项目日志框架选型、英文日志、禁控制台）
3. AI 需发散给出 2-3 个可行实现方向（含优缺点与风险），让用户确认
4. 若用户不接受已有方向，必须明确“替代方向或硬约束”；否则返回 `BLOCKED`
5. 若澄清项或方向确认仍缺失、模糊或为 `TBD/待定`：返回 `BLOCKED` 并停止，不得进入计划阶段
6. 生成 `docs/specs/YYYY-MM-DD-<需求名称>-spec-lite.md`
7. 计算 `recommendedTier`
8. 若存在 `tierOverride` 但缺少 `overrideReason`，返回 `BLOCKED` 并停止
9. 将 `GateContext` 写入规格文档
10. 返回 `GateResult` 与下一条推荐命令：
   - `L/M`：`/write-plan spec=<specPath> tier=<finalTier>`
   - `H`：`/brainstorm <需求描述>`（强制完整七阶段）

$ARGUMENTS
