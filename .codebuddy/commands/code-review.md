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
5. 强制检查日志规范：
   - 是否沿用项目日志结构与字段
   - 是否存在中文日志内容
   - 是否残留控制台输出（console/print/System.out/fmt.Print）
6. 输出 `code-review-report.md`、`code-review-report.xlsx`，以及可选 `web-code-review-report.json`

$ARGUMENTS
