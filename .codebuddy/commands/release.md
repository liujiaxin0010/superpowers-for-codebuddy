请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/release-and-rollback/SKILL.md`（发布与回滚）
3. `.codebuddy/skills/release-and-rollback/templates/changelog-entry.md`
4. `.codebuddy/skills/release-and-rollback/templates/release-notes.md`
5. `.codebuddy/skills/release-and-rollback/templates/rollback-playbook.md`

**务必遵守四条铁律（见 CODEBUDDY.md §1）：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码
4. 发布若含数据操作，必须已有 `/data-safety-check` 签字报告

**你的任务是：**
在门禁约束下准备并执行发布。默认只准备，真实发布动作需 Boss 显式确认。

执行步骤：
0. 阶段计时（供 `/metrics` §6 周期时间，建议执行）：开始时 `node .codebuddy/skills/delivery-metrics/scripts/stage-event.js release start --task=<规格/任务名>`；本命令结束（含 BLOCKED）前同参数执行 `end`。脚本缺失则跳过，不阻断。

1. 解析参数：`/release version=<vX.Y.Z> [spec=<path>] [plan=<path>] [strategy=canary|full|batch]`
2. 调用 `process-gatekeeper`（`command=release`）
3. 若阻断：输出阻断报告并停止
4. 生成 / 更新三件套：
   - `docs/changelog/<version>.md`（依据 `changelog-entry.md` 模板）
   - `docs/release/<version>-release-notes.md`（依据 `release-notes.md` 模板）
   - `docs/runbooks/<feature>-rollback.md`（依据 `rollback-playbook.md` 模板）
5. 发布前 checklist：逐项确认 `/requirement-coverage` / `/security-review` / `/unified-test` / `/system-test` / `/perf-check` / `/data-safety-check` 通过态
6. 任何一项未通过 → BLOCKED，回退对应命令
7. Rollback playbook 必须在 staging 演练过一次，演练记录写入模板第 7 节
8. 输出"发布准备就绪"摘要：版本、策略、指标、阈值、回滚路径、值守人
9. Boss 显式确认 → 真实发布动作允许执行；否则停在"准备就绪"态
10. 发布完成后：签字原文 + 时间戳写入 `docs/progress.md`；异常写入 `docs/findings.md`
11. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
