请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/code-self-check/SKILL.md`（代码自检）
3. `.codebuddy/skills/requesting-code-review/SKILL.md`（审查规范）
4. `.codebuddy/skills/receiving-code-review/SKILL.md`（反馈处理）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

你的任务是：
基于 diff 执行代码自检，支持 Git/SVN 双模式。

执行步骤：
1. 解析参数：`/code-self-check [vcs=auto|git|svn] [diffPath=<path>] [applyFix=true|false]`
2. 调用 `process-gatekeeper`（`command=code-self-check`）
3. 若阻断：输出阻断报告并停止
4. 判断版本控制：
   - `vcs=git` -> 使用 `git diff`
   - `vcs=svn` -> 使用 `svn diff`
   - `vcs=auto` -> 自动检测 `.git/.svn`
5. 优先使用 `diffPath`（若提供且存在），否则实时生成 diff
6. 生成审查报告 `docs/quality/code-self-check-report.md`
7. 若 `applyFix=true`，按确认项修复并给出验证证据
8. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
