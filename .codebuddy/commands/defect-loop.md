请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/defect-tracking/SKILL.md`（缺陷生命周期闭环）
3. `.codebuddy/skills/gitlab-bridge/SKILL.md`（GitLab 对接层）
4. `.codebuddy/skills/using-git-worktrees/SKILL.md`（Worktree 隔离）
5. `.codebuddy/skills/bug-fix/SKILL.md`（单次修复方法论）

**务必遵守四条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码
4. 触达生产数据 / schema 的修复必须先有 data-safety 合同并经 Boss 签字

**你的任务是：**
扫描缺陷源，自动分类、择一修复、验证、走 MR 流程合入，并维护 `bugfix:*` 标签状态机与 `.codebuddy`↔GitLab Issue 双向同步。**每次只修 1 个缺陷。**

执行步骤：

1. **门禁与探测**：
   - 调用 `process-gatekeeper`（`command=defect-loop`）；阻断则输出阻断报告并停止
   - 经 `gitlab-bridge` 执行 `bridge.probe`，确认 `issue.*` / `mr.*` 写动作可用性
   - 写动作不可用且只读 → 走本地 `docs/backlog/` / `.codebuddy-runtime/issues/` 降级，并提示 Boss 放开 `GITLAB_READ_ONLY_MODE`

2. **发现与收录**（按 `source` 参数，默认全部）：
   - `source=codebuddy`：扫 `.codebuddy-runtime/issues/` 下 open Issue
   - `source=gitlab`：`intake.list` 扫 GitLab open Issue
   - `source=ci`：解析最近失败流水线日志 → `issue.create`

3. **分类与评级**：对未分类 Issue 按 `label-state-machine.md` 判定 bug / enhancement / question / 不确定，经 `issue.update` 打标签；非 bug 跳过

4. **评估与选择**：bug 队列按创建时间先入先出，择 1 个；命中放弃标准（>5 文件 / 跨层 / 核心重构 / 信息不足）→ 打 `bugfix:needs-design` + 评论原因，结束本轮

5. **Worktree 隔离修复**：
   - `git worktree add .worktrees/bugfix-{iid} -b fix/issue-{iid} <主分支>`
   - `issue.update` 打 `bugfix:in-progress`
   - 调 `bug-fix` 方法论实施最小化修复 + 补回归测试（覆盖 bug 触发条件）

6. **验证**：后端 → 测试全绿；前端 UI → 浏览器自动化；无法验证 → `bugfix:needs-verification`；失败 → `bugfix:failed` 并 `git checkout -- .` 回滚

7. **MR 流程**：commit（按 `bug-fix/templates/bugfix-commit-message.md`）→ push → `mr.create`（描述含 `Fixes #{iid}`）→ 轮询 `pipeline.status`（最多 40×30s）→ CI 失败在同 Worktree 修复（最多 3 次）→ `mr.merge`（squash + remove-source-branch）

8. **清理与报告**：`git worktree remove .worktrees/bugfix-{iid}`（无论成败必清理）→ 更新 Issue 状态 / 双向同步 → 按 `defect-tracking/templates/fix-report.md` 输出报告

补充约束：
- 所有 GitLab 交互只经 `gitlab-bridge` 抽象动作，不直调 glab / MCP
- 不重复处理已带 `bugfix:*` 标签的 Issue
- 修复必须最小化，不做无关重构、不改 docs/
- 无验证证据不关 Issue

参数：`source=<codebuddy|gitlab|ci|all>`（默认 all）、`max=<本轮最多修复个数>`（默认 1）

$ARGUMENTS
