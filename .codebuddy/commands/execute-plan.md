请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/executing-plans/SKILL.md`（计划执行）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
先过门禁，再执行计划。

执行步骤：
1. 解析参数：`planPath`，可选 `spec=<path>`、`tier=<L|M|H>`
2. 调用 `process-gatekeeper`（`command=execute-plan`）
3. 若阻断：输出阻断报告并停止
4. 若通过：按批次执行，并展示测试证据
5. 执行质量门禁脚本：
   - PowerShell: `powershell -ExecutionPolicy Bypass -File .codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1`
   - Shell: `bash .codebuddy/skills/process-gatekeeper/scripts/check-quality.sh`
6. 若质量门禁 `BLOCKED`：停止收尾并返回修复项；通过后才允许宣告完成

$ARGUMENTS
