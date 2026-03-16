请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/task-contracts/SKILL.md`（统一任务合同）
3. `.codebuddy/skills/issue-draft-pr/SKILL.md`（Issue -> Draft PR 工作流）
4. `.codebuddy/skills/writing-plans/SKILL.md`（实施计划编写）
5. `.codebuddy/skills/executing-plans/SKILL.md`（计划执行）
6. `.codebuddy/skills/requesting-code-review/SKILL.md`（审查发起）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
以工单为起点，生成可审查的 draft PR 交付链路；默认不直接合并。

执行步骤：
1. 解析参数：`/issue-draft-pr <issueLink> [spec=<path>] [plan=<path>] [tier=<L|M|H>] [owner=<name>]`
2. 按 `.codebuddy/templates/task-contracts/issue-draft-pr.md` 生成最小合同，至少补齐：
   - 工单链接
   - 目标 / 非目标
   - 相关仓库 / 目录
   - 验收标准
   - 人工确认点
   - PR 需要包含的说明
   - owner
3. 若工单目标或验收标准不清：直接 `BLOCKED`，引导先补 acceptance criteria 或回退 `/spec-lite <需求描述>`
4. 调用 `process-gatekeeper`（`command=issue-draft-pr`）
5. 若阻断：输出阻断报告并停止
6. 若未提供 `spec`：引导进入 `/spec-lite`
7. 若已有 `spec` 但未提供 `plan`：引导进入 `/write-plan spec=<specPath> tier=<finalTier>`
8. 若 `spec + plan` 已齐备：引导进入 `/execute-plan <planPath> spec=<specPath> tier=<tier>`
9. 收尾前必须执行 `/code-review`，并整理 draft PR 说明：
   - 工单目标映射
   - 验收证据
   - 越界风险
   - 剩余风险
   - merge / handoff owner
10. 输出 draft PR 建议内容，不宣告已合并

$ARGUMENTS
