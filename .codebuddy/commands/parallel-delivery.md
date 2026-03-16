请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/task-contracts/SKILL.md`（统一任务合同）
3. `.codebuddy/skills/parallel-delivery/SKILL.md`（并行交付工作流）
4. `.codebuddy/skills/dispatching-parallel-agents/SKILL.md`（并行子代理分发）
5. `.codebuddy/skills/using-git-worktrees/SKILL.md`（Git worktree 隔离开发）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
把长任务编排成可并行交付的多 lane 工作流，并为每个 lane 明确边界、验证和最终收口 owner。

执行步骤：
1. 解析参数：`/parallel-delivery spec=<path> plan=<path> [tier=<L|M|H>] [owner=<name>]`
2. 按 `.codebuddy/templates/task-contracts/parallel-delivery.md` 生成或补齐并行合同，至少包含：
   - 总目标
   - 子任务拆分
   - 每个子任务允许修改目录
   - 每个子任务验证命令
   - 禁止共享的文件或可变状态
   - 最终收口负责人
3. 调用 `process-gatekeeper`（`command=parallel-delivery`）
4. 若阻断：输出阻断报告并停止
5. 若计划未明确并行组，或多个子任务共享同一文件：直接 `BLOCKED`，引导先回 `/write-plan`
6. 判断版本控制：
   - Git -> 推荐按 `using-git-worktrees` 为每个 lane 建独立 worktree
   - SVN / 非 Git -> 使用独立 session 并严格文件边界
7. 为每个 lane 输出执行摘要：
   - lane 目标
   - 允许修改目录
   - 禁止触碰目录 / 文件
   - 验证命令
   - 上游依赖
8. 所有 lane 完成后，由 owner 统一执行：
   - 冲突检查
   - 集成验证
   - `/code-review`
   - 质量门禁脚本
9. 输出并行交付总览：lane 结果、合流说明、剩余风险、最终 handoff 建议

$ARGUMENTS
