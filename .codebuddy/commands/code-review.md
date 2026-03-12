请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/code-review-standards/SKILL.md`（通用审查）
3. `.codebuddy/skills/web-code-review/SKILL.md`（Web 专项审查）
4. `.codebuddy/skills/xlsx/SKILL.md`（XLSX 输出）

你的任务是：
在门禁约束下执行统一代码审查。

执行步骤：
1. 解析可选参数：`spec=<path>`、`tier=<L|M|H>`、`plan=<path>`
2. 调用 `process-gatekeeper`（`command=code-review`）
3. 若阻断：输出阻断报告并停止
4. 若通过：执行通用五维审查；对前端文件追加 Web 专项审查
5. 审查阶段严格只读：先输出问题清单（按严重程度分组），**不得直接修改代码**
6. 输出“修复建议列表 + 建议命令”，等待 Boss 明确确认后再进入修复流程
7. 强制检查日志规范：
   - 是否沿用项目日志结构与字段
   - 是否存在中文日志内容
   - 是否残留控制台输出（console/print/System.out/fmt.Print）
8. 输出时额外声明：
   - 证据是否完整
   - 是否存在越界修改
   - 未声明风险
   - merge / handoff owner
9. 输出 `code-review-report.md`、`code-review-report.xlsx`，以及可选 `web-code-review-report.json`

补充约束：
- `/code-review` 默认不承担自动修复职责
- 若 Boss 要求修复，先确认修复范围，再转入对应执行命令（如 `/execute-plan`、`/fix-bug` 或 `/code-self-check applyFix=true`）

$ARGUMENTS
