请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/data-safety/SKILL.md`（数据安全）
3. `.codebuddy/skills/data-safety/templates/data-migration-plan.md`（计划模板）

**务必遵守四条铁律（见 CODEBUDDY.md §1）。**

**你的任务是：**
对即将发生的触达生产数据 / 共享存储 / 表结构的操作执行数据安全审查，产出四件套并由 Boss 签字。

执行步骤：

1. 解析参数：`/data-safety-check operation=<描述> [env=prod|staging|dev] [rows=<估计>] [planPath=<path>]`
2. 调用 `process-gatekeeper`（`command=data-safety-check`）
3. 若阻断：输出阻断报告并停止
4. 判定是否命中触发条件（`data-safety/SKILL.md#触发条件`）；未命中 → 仍需 Boss 确认 "不命中" 才放行
5. 按模板依次产出四件套：
   - 行数 / 作用域预估（实际执行只读统计命令，附输出）
   - 备份 / 快照（实际创建或引用已存在的可用快照，附验证证据）
   - dry-run 证据（实际执行，附输出摘要）
   - 回滚脚本（存档到 `docs/plans/<...>-rollback.sql` 或等价路径；staging 演练一次）
6. 输出计划到 `docs/plans/YYYY-MM-DD-<op-name>-data-safety.md`
7. 请求 Boss 显式签字；未签字 → BLOCKED
8. 签字原文 + 时间戳同步写入 `docs/progress.md`；如有新的风险模式写入 `docs/findings.md`
9. 仅当签字完成后，才允许 `/execute-plan` / `/release` 真正执行数据操作
10. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
