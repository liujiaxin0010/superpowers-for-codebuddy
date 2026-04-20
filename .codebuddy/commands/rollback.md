请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/release-and-rollback/SKILL.md`（发布与回滚）
3. `.codebuddy/skills/release-and-rollback/templates/rollback-playbook.md`

**务必遵守四条铁律（见 CODEBUDDY.md §1）。**

**你的任务是：**
准备或执行回滚。默认策略：仅做回滚准备 + dry-run 演练；真实回滚必须 Boss 显式签字。

执行步骤：

1. 解析参数：`/rollback target=<version> [reason=<text>] [mode=dry-run|real]`
2. 调用 `process-gatekeeper`（`command=rollback`）
3. 若阻断：输出阻断报告并停止
4. 读取对应的 `docs/runbooks/<feature>-rollback.md`
5. 校验快照点仍有效（commit / tag / 备份）
6. 通知链预通知（运维 / 业务 / 值守人）
7. 若 `mode=dry-run`：在 staging 按脚本执行一次，输出演练记录
8. 若 `mode=real`：
   - 必须存在 Boss 显式签字（签字原文 + 时间戳）
   - 缺签字 → BLOCKED
   - 执行并实时记录到 `docs/runbooks/<feature>-rollback-<YYYYMMDD-HHmm>.md`
9. 回滚完成后 24 小时内提交复盘 → `docs/findings.md`
10. 若实际 RTO / RPO 超出预估 → 在 `docs/findings.md` 单列一条根因
11. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
