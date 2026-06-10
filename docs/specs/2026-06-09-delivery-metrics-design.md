# 交付效能度量（/metrics）设计

- 日期：2026-06-09
- 状态：Tier 0 已实现（`scripts/metrics.js` + `/metrics` 命令，已在本仓库自验证）；Tier 1/2 待排期
- 关联：流程治理白皮书、`process-gatekeeper`、`event-triggers`（`jobs.jsonl`）、`defect-tracking`（标签状态机）

## 1. 背景与问题

工具流有 27 命令覆盖全 SDLC，产出大量结构化产物，但**没有聚合层**把它们变成"这条流水线跑得好不好"的信号（全仓搜 `DORA/前置时间/周期时间/返工率` 零命中）。后果：

- 哪个门禁最常 BLOCK（最大摩擦点）无统计；门禁误报（如 commit-msg-lint 的 merge bug）拖到 CI 才暴露
- defect-loop / 定时任务自动改的 MR 接受率（被 revert 否）无跟踪 → 反复犯同类错
- 各阶段耗时、缺陷逃逸率全黑盒 → **流程无法自我校准，只能拍脑袋调**

## 2. 目标 / 非目标

**目标**：新增 `/metrics`，从**已有产物**聚合出交付效能视图；优先零新埋点可算的指标；为后续各阶段优化提供"是否有效"的判定基线。

**非目标**：不做实时监控大盘；不接 APM/生产 SLO（那是运维侧）；不替代 `/score-interaction`（那是 AI 交互质量，本命令是交付吞吐与质量）。

## 3. 数据源盘点（决定指标可行性的关键）

| 数据源 | 已有字段 | 可算什么 |
|---|---|---|
| `docs/quality/last-quality-gate.json` | `status` `passRate` `coverage.branches` `coverageThreshold` `docSyncStatus` `checkedAt` | 门禁通过率、覆盖率趋势、检查时间戳 |
| `docs/quality/test-summary.json` | `total` `passed` `failed` `passRate` `coverage` | 测试规模与通过率趋势 |
| 接收器 `jobs.jsonl` | `ts` `ev` `command` `mr` `code` `timedOut` `ms` | 自动化任务成功率、超时率、单任务耗时分布、命令频次 |
| git 历史 | 提交时间、AI 标签 `[AI-0/H/100]`、conventional type、merge 关系 | 自动化占比（AI-100 比例）、变更类型构成、提交→合并前置时间、revert 率 |
| `bugfix:*` 标签状态机 | `in-progress/awaiting-review/needs-verification/failed/...` | 缺陷闭环吞吐、停留时长、失败重修率 |
| `docs/pending-decisions.md` | `status=pending/partial` + 时间 | 决策挂起数与时效（aging） |
| CI commit-msg-lint | 每提交 pass/fail | 提交规范合规率、门禁误报率（结合 merge 豁免） |

## 4. 指标目录（按落地难度分三期）

### Tier 0 — 现有数据即可算（首期，无新埋点）

1. **门禁健康**：各门禁通过率 / 阻断率（`last-quality-gate.json` 历史 + CI 记录）；**误报率**=被 BLOCK 但下一提交未实质改动即过的比例
2. **覆盖率与测试趋势**：`passRate`、`coverage.branches` 随时间曲线；低于阈值的次数
3. **自动化 ROI**（`jobs.jsonl`）：各命令调用频次、成功/超时/失败占比、p50/p95 耗时；**超时率**直接反映"挂死类"故障是否复发
4. **自动化占比**：git AI 标签 `[AI-100]:[AI-H]:[AI-0]` 比例 = 人机协作结构画像
5. **缺陷闭环吞吐**（`bugfix:*` 标签）：进行中/待审/待验证数、`bugfix:failed` 重修率、平均停留时长
6. **决策时效**（pending-decisions）：挂起数、最长挂起天数、超 N 天未答项

### Tier 1 — 已实现（二期）

9. **自动修复接受率** ✅ 已实现，**零埋点**：解析 `Revert "..."` 提交体的 `This reverts commit <sha>`，回查被回滚提交的 AI 标签 → `AI-100` 接受率 = 1 − 被回滚/全部 AI-100 提交。git 关系即真实，立即可用。
8. **缺陷逃逸率** ✅ 聚合已实现，**需约定**：缺陷台账 `.codebuddy-runtime/defects.jsonl` 每行 `{id, foundPhase}`，`foundPhase ∈ {review, test, system-test, prod}`；逃逸 = review 后才发现。`defect-tracking` 写缺陷时带 `foundPhase`，无则标 N/A。
7. **各阶段周期时间** ✅ 聚合已实现，**需埋点**：`scripts/stage-event.js <phase> <start|end> [--task]` 在命令起止追加事件到 `.codebuddy-runtime/stage-events.jsonl`；`/metrics §6` 配对 start/end 算各阶段 p50/p95。接入择一：①命令 runbook 起止各调一次；②CodeBuddy hook 在命令前后触发。未埋点标 N/A。

### Tier 2 — 需集成（三期）

10. **DORA 雏形**：部署频率（release tag 频次）、变更前置时间（首次提交→合并/发布）、变更失败率（发布后 rollback 占比）、MTTR

## 5. 命令契约（/metrics）

```text
/metrics [scope=repo|sprint|task] [since=<date>] [format=md|json] [tier=0|1|all]
```

- 默认 `scope=repo since=最近30天 format=md tier=0`
- 只读：聚合现有产物，不改源码/不触发其它命令
- 输出：`docs/quality/metrics-<date>.md`（+ 可选 `.json`），含每指标的值、环比、和阈值/基线对比、**Top 摩擦点**（阻断最多的门禁、超时最多的任务、挂最久的决策）
- 数据缺失（如某项目无 `jobs.jsonl`）→ 该指标标 `N/A` 并说明，不阻断其余

## 6. 集成点

- `/status`（单任务态）补一行"效能摘要"链接到最近一次 `/metrics`
- `scheduled-automation` 加一个低频任务（如每周一）自动跑 `/metrics` 产周报，经 MR 提交
- 门禁误报率纳入引擎自检：误报率突增 = 门禁规则需修（呼应 commit-msg-lint 1.0.1 那类 bug）

## 7. 验收标准

1. 在本引擎仓库 `tier=0` 跑通：用 git 历史 + 现有 `docs/quality/*.json` 产出真实数字（非样例）
2. Top 摩擦点能正确指出已知问题（如本会话两次 CI 红的门禁）
3. 无 `jobs.jsonl` 的项目不报错，相关指标标 `N/A`
4. 报告可复现：同输入同输出，纯聚合无副作用

## 8. 风险与权衡

- **过度度量反成负担**：只暴露"可行动"指标，每指标必须对应一个优化动作；不堆虚荣指标
- **Tier 0 的近似性**：误报率/逃逸率在无埋点时是启发式估算，报告需标注"估算"并在 Tier 1 收敛为精确值
- **样本量小则噪声大**：小项目按周/月聚合，标注样本数，避免过度解读
