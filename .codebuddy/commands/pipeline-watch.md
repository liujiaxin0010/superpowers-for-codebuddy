请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/ci-integration/references/pipeline-self-heal.md`（流水线自愈协议：循环/失败分类/停止条件/安全）
2. `.codebuddy/skills/gitlab-bridge/SKILL.md`（`pipeline.status` 监听 + 取 job 日志、`mr.*` 回贴/合并）
3. `.codebuddy/skills/systematic-debugging/SKILL.md` 与 `.codebuddy/skills/bug-fix/SKILL.md`（根因定位与最小修复）
4. `.codebuddy/skills/data-safety/SKILL.md`（修复触达数据时的门禁）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
经 `gitlab-bridge` 监听指定 MR 的流水线；失败则取报错日志、定位根因、最小修复、合规提交、推源分支重触发，循环重试**直到通过**；到达修复上限或判定不可自修则**停止并升级人工**。

执行步骤：

1. 解析参数：`mr=<iid>`（不填则用当前分支 → `mr.status` 定位其 open MR；定位不到 → `BLOCKED`）；可选 `maxFixes=<N，默认 3>`、`interval=<秒，默认 30>`、`maxPolls=<默认 40>`、`autoMerge=<true|false，默认 false>`。
2. `bridge.probe`；MCP 不可用 → 降级：用 `scheduled-automation/templates/ci-poll.sh` 本地轮询并提示人工修，不阻断。
3. **监听**：`pipeline.status` 轮询到终态（`success`/`failed`/`canceled`），最多 `maxPolls×interval`。
4. **成功** → 回贴绿状态（`commit.status`）；`autoMerge=true` 且无冲突 → `mr.merge`；输出报告，结束。
5. **失败** → 取失败 job 日志（`pipeline.status` 含 `get_pipeline_job_output`）→ 按 `pipeline-self-heal.md §3` **先分类**：代码问题 vs 基础设施/flaky。
   - 基础设施/flaky → 重试一次流水线；仍失败 → 升级人工，结束。
6. **代码问题** → 走 `systematic-debugging`/`bug-fix` 最小修复 → **合规 commit**（`fix:`/`AC<数字>:`）→ push **源分支**（重触发流水线）。
7. **回到第 3 步**，直到：通过 / 达 `maxFixes` / 同一错误修复后复现 / 改动越界 / 命中数据·安全门禁 → 任一即**停止 + 升级人工 + 报告**（见 `§4 停止条件`）。
8. 每轮更新 `docs/progress.md`（轮次、失败 job、根因、改动、退出码、重试结果）；关键自愈结论可 `mr.discussion` 行内回贴。

补充约束：
- **有界**：默认最多修 3 次；绝不无限循环（无上限会无限烧 CI、越改越坏）。
- **只 push 源分支，绝不直推 main**；幂等键 `MR iid + 最新 sha`，同 commit 不重复自愈。
- **触发身份**：自愈 push 用能触发 MR 流水线的身份（PAT / Project Access Token），否则不触发、循环失效。
- 修复触达**数据/迁移** → 走 `data-safety`；命中**安全条件** → 走 `security-review`；不自动改，升级确认。
- 删测试"让它绿"属作弊，**禁止**；测试失败要么改实现、要么修正错误的测试。
- 报告须含失败 job + 日志摘录 + 改动 + 重试证据，不只给结论；凭据不落盘。

$ARGUMENTS
