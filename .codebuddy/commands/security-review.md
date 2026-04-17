请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/security-review/SKILL.md`（安全审查）
3. `.codebuddy/skills/xlsx/SKILL.md`（XLSX 输出）

**务必遵守四条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码
4. 涉及生产数据 / schema / 批量删改必须先有 `data-safety` 合同（若触发）

**你的任务是：**
在门禁约束下执行安全审查，输出结构化缺陷报告与修复建议。

执行步骤：

1. 解析参数：`/security-review [scope=<paths>] [spec=<path>] [plan=<path>] [threatModelPath=<path>]`
2. 调用 `process-gatekeeper`（`command=security-review`）
3. 若阻断：输出阻断报告并停止
4. 检测触发条件（`security-review/SKILL.md#触发条件`）；未命中任何条件时允许 Boss 显式强制执行
5. 按 9 个维度审查：威胁建模 / OWASP / 输入输出 / 鉴权授权 / 加密密钥 / 日志审计 / 依赖审计 / 秘密扫描 / 合规隐私
6. 每个维度必须有"不涉及 / 涉及但已缓解 / 涉及且有风险"三态判定
7. 依赖审计实际运行扫描工具（npm audit / pip-audit / govulncheck / cargo audit 等），输出摘要写入报告
8. 秘密扫描实际运行（gitleaks 或 grep 等），证据写入报告
9. 输出 `docs/quality/security-review-report.md` + `docs/quality/security-review-report.xlsx`，回填 spec 的 `securityReviewReportPath`
10. 🔴 严重问题存在 → 阻断；通过才允许进入 `/unified-test` / `/system-test` / `/release`
11. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
