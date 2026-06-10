请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/task-contracts/SKILL.md`（统一任务合同）
3. `.codebuddy/skills/writing-plans/SKILL.md`（实施计划编写）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
计划编写前先过门禁，不通过则阻断。

执行步骤：
0. 阶段计时（供 `/metrics` §6 周期时间，建议执行）：开始时 `node .codebuddy/skills/delivery-metrics/scripts/stage-event.js plan start --task=<规格/任务名>`；本命令结束（含 BLOCKED）前同参数执行 `end`。脚本缺失则跳过，不阻断。
1. 解析参数：`spec=<path>`、`tier=<L|M|H>`
2. 若缺少 `spec` 或 `tier`：直接输出 `BLOCKED` 并引导回 `/spec-lite <需求描述>`
3. 读取 spec 中"需求澄清结论""方案方向确认""TaskContract"段落：
   - 若存在 `TBD/待定/未确认`：直接 `BLOCKED`
   - 若无 `selectedDirection` 或 `unresolvedItems` 非空：直接 `BLOCKED`
   - 若用户拒绝候选方向但未给出明确替代方向/硬约束：直接 `BLOCKED`
   - 若 `tier=H` 且 spec 的"追踪链接"中 `brainstormPath` 为空：直接 `BLOCKED` 并回退 `/brainstorm <需求描述> spec=<specPath> tier=H`
   - 若日志策略缺失（未说明沿用结构/框架选型、英文日志约束、禁控制台策略）：直接 `BLOCKED`
   - 若合同缺少目标、边界、验证、证据、owner：直接 `BLOCKED`
3.5 跑 `/pending sweep`（或读取 `docs/pending-decisions.md`）：若存在 `status in (pending, partial)` 项 → 直接 `BLOCKED`，并提示需先 `/pending answer|defer|drop` 收敛
4. 调用 `process-gatekeeper`（`command=write-plan`）
5. 若 `GateResult.status=blocked`：输出阻断报告并停止
6. 若通过：生成 `docs/plans/YYYY-MM-DD-<功能名称>.md`
7. 在计划中写入元信息：`specPath`、`finalTier`、`gateStatus`、`taskType`
8. 将 spec 中的 TaskContract 压缩为“执行合同摘要”，写入计划中
9. 同步兼容产物：
   - `spec/AI2AI/plan.md`
   - `spec/AI2AI/summary.md`
10. 回填 spec 追踪链接：
   - `planPath`
   - `implementationProgressPath`（预留）
   - `implementationSummaryPath`（预留）
11. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
