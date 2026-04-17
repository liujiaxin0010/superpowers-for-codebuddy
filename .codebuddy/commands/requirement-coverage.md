请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/requirement-coverage-check/SKILL.md`（需求覆盖审查）
3. `.codebuddy/agents/spec-reviewer.md`（独立验证原则）
4. `.codebuddy/skills/xlsx/SKILL.md`（XLSX 输出）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在系统测试启动前，独立验证 AI 已写代码与需求分析文档的差异，给出"通过 / 不通过"判定。

执行步骤：

1. 解析参数：`/requirement-coverage requirementDoc=<path> [specDoc=<path>] [planDoc=<path>] [vcs=auto|git|svn]`
2. 调用 `process-gatekeeper`（`command=requirement-coverage`）
3. 若阻断：输出阻断报告并停止
4. 加载需求分析文档与覆盖矩阵；任一缺失 → BLOCKED
5. **以独立第三方视角**逐项验证：
   - 打开实现位置阅读代码
   - 运行验证用例 / 命令并展示完整输出
   - 判定 ✅ / 🟡 / 🔴 / 🟠
6. 扫描越界实现与兼容性代码（铁律三）
7. 输出 `docs/quality/requirement-coverage-report.md` 与 `docs/quality/requirement-coverage-report.xlsx`
8. 通过 → 推荐进入 `/unified-test` 或系统测试
9. 不通过 → 列出阻断项 + 退回命令（`/execute-plan` / `/fix-bug` / `/code-self-check applyFix=true`）；同步更新 `docs/progress.md` 与 `docs/findings.md`
10. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

补充约束：

- 本命令默认只读，不修改业务代码
- 不可由实现者自审；如实现者也是当前会话主体，必须以独立子代理（推荐 `spec-reviewer`）执行验证

$ARGUMENTS
