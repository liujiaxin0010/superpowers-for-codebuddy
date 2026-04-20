请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/session-handoff/SKILL.md`（会话交接）
3. `.codebuddy/skills/file-based-memory/SKILL.md`（文件记忆）

**务必遵守四条铁律（见 CODEBUDDY.md §1）。**

**你的任务是：**
基于 `.codebuddy/state/session-handoff.json` 快照精准恢复上次会话的任务上下文，并运行到下一步。

执行步骤：

1. 读取 `.codebuddy/state/session-handoff.json`
   - 文件缺失 → 提示"无快照可恢复"，改走 `scripts/session-catchup.py` 路径
   - 文件存在 → 依据 schema 校验字段完整性
2. 调用 `process-gatekeeper`（`command=resume`）
3. 若阻断：输出阻断报告并停止
4. 读取关联文件：
   - `docs/progress.md`（当前阶段 + 下一步）
   - `docs/findings.md`（已有结论、失败模式、决策）
   - 快照里的 `specPath` / `planPath`
5. 逐项校验 `pendingGates`：
   - 若某个 `blocker=true` 的门禁实际已通过 → 更新快照为 `completed`
   - 若某个 `blocker=false` 的门禁实际已阻断 → 升级为 `blocker=true` 并给出原因
6. 运行 `bash .codebuddy/skills/file-based-memory/scripts/lint-memory.sh`，确认记忆结构契约仍满足
7. 输出"会话恢复摘要"：
   - 当前 taskType / taskTier
   - 上次最后命令
   - 剩余待决门禁（按 blocker 优先）
   - 下一步动作（快照 `nextAction`）
   - 开放问题（`openQuestions`）
8. 用户确认后，自动跳转到 `nextAction` 对应的斜杠命令
9. 本次执行结束前，刷新快照（至少更新 `lastUpdatedAt` 与 `lastCommand`）
10. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
