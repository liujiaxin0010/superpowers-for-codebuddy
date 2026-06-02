# 流水线自愈协议（监听 → 失败修复 → 重试 → 直到通过/升级）

回答：**怎样经 GitLab MCP（gitlab-bridge）监听某条 MR 流水线，失败时读报错、改代码、重推、重试，直到通过。** 命令入口：`/pipeline-watch`。

> ⚠️ "直到通过"必须**有界**：无上限循环会无限烧 CI、且可能一错再错越改越坏。本协议默认最多修 **3 次**，到顶或判定不可自修即**停止并升级人工**——这是特性不是缺陷。

## 1. 循环骨架

```text
定位 MR（mr= 或当前分支 → mr.status）
  └─ 轮询 pipeline.status 到终态（success/failed/canceled；最多 40×30s）
       ├─ success → 完成：回贴绿状态，（可选）mr.merge
       └─ failed  → 取失败 job 日志（pipeline.status 含 get_pipeline_job_output）
                    → 按"失败类型→修复策略"定位根因
                    → 可自修？
                        ├─ 是 → 最小修复 + 合规 commit + push 源分支（重触发流水线）→ 回到轮询
                        └─ 否 / 已达 maxFixes / 同错复现 → 停止 + 升级人工 + 报告
```

每轮结束更新 `docs/progress.md`（第几次、失败 job、根因、改了什么、退出码）。

## 2. 用到的 gitlab-bridge 动作

| 动作 | 用途 |
|---|---|
| `mr.status` | 由 MR iid / 当前分支定位 MR 与其最新流水线 |
| `pipeline.status` | 轮询流水线/ job 状态；**含 `get_pipeline_job_output` 取失败 job 完整日志** |
| `mr.discussion` / `commit.status` | 把"自愈中/已修复/需人工"回贴到 MR（行内 + 状态）|
| `mr.merge` | （可选）绿后合并 |

MCP 不可用 → 降级：本地 `scheduled-automation/templates/ci-poll.sh` 轮询 + 人工修。

## 3. 失败类型 → 修复策略（对应 5 阶段）

| 失败 job | 典型根因 | 修复策略 | 是否改代码 |
|---|---|---|---|
| `build:compile` | 编译/语法/依赖错 | 读编译错误定位文件行 → 最小修正 | ✅ |
| `test:unit` | 单测失败 | 走 `systematic-debugging` / `/fix-bug`：读失败用例 → 改实现或修正测试（不是删测试）| ✅ |
| `quality:check` | 通过率/覆盖率不达标、文档不同步 | 补测试提覆盖 / `/doc-sync` 同步 CONTEXT.md | ✅ |
| `verify:commit-msg` | commit message 不合规 | rebase 改 message 为 `AC<数字>:` 或 `<type>:` 格式 | ⚠️ 改历史，非源码 |
| `gate:process` | 门禁资产/接线缺失 | 补 spec/plan/证据后重推 | ⚠️ 补产物 |
| `review:ai`（启用时）| 🔴 严重问题 | 按审查意见最小修复 | ✅ |
| **基础设施/flaky** | runner 离线、网络、间歇失败 | **不改代码**：重试一次流水线；仍失败→升级人工（误把环境问题当代码问题改，只会越改越乱）| ❌ |

> 第一步永远是**分类**：先判断"代码问题"还是"环境/flaky 问题"。后者不该触发改代码。

## 4. 停止条件（任一命中即停 + 升级）

1. 流水线 **success** → 成功收尾。
2. 已达 `maxFixes`（默认 3）。
3. **同一错误修复后复现** → 说明修复无效/方向错，立即升级（防原地打转）。
4. 改动**越界**（> 约定文件数 / 跨层架构 / 核心流程重构）。
5. 判定为**基础设施/flaky**，重试一次仍失败。
6. 修复会**触达数据/迁移**（走 `data-safety`）或**命中安全条件**（走 `security-review`）→ 不自动改，升级确认。

## 5. 安全与幂等

1. **只 push MR 源分支，绝不直推 main**。
2. **幂等键** `MR iid + 最新 commit sha`，与 `event-triggers` / `scheduled-automation` 共用——同一 commit 不重复自愈。
3. **触发身份核对（CI_JOB_TOKEN）**：自愈 push 必须用能触发 MR 流水线的身份（PAT / Project Access Token），否则新 commit 不触发流水线，循环失效（见 `ci-integration/SKILL.md` 禁止事项）。
4. **commit 必合规**：自愈提交本身要过 `verify:commit-msg`（用 `fix:`/`AC<数字>:`），否则下一轮反被自己卡红。
5. **证据透明**：每轮报告失败 job + 日志摘录 + 改动 + 重试结果，不只给结论。
6. 凭据/令牌不落盘。

## 6. 与既有体系的关系

- **按需单 MR** → `/pipeline-watch`（本协议）。
- **批量/无人值守** → `scheduled-automation` Task #17（每小时扫所有 open MR，同一自愈循环）。
- **事件实时** → `event-triggers` 的 `pipelineFailed` 触发 → 自动调 `/pipeline-watch`。

三者是**同一自愈循环**的不同触发方式，共用失败分类、停止条件与幂等键。
