---
name: delivery-metrics
description: 交付效能度量技能。聚合 git 历史、质量门禁产物、自动化任务台账（jobs.jsonl）、决策台账，产出交付效能报告与 Top 摩擦点（门禁阻断/超时/挂起决策/提交合规）；含自动修复接受率（git revert 零埋点）、各阶段周期时间（stage-event 埋点）、缺陷逃逸率（foundPhase 约定）。用户提到"效能度量/metrics/交付效率/摩擦点/接受率/逃逸率/阶段耗时/DORA"时触发。
---

# 交付效能度量（Delivery Metrics）

本技能回答的是：**这条流水线跑得好不好——用系统已产出的真实数据说话，而不是拍脑袋。**

## 核心心智

1. **指标锚定现有产物**：优先零埋点可算（git/门禁 JSON/jobs.jsonl）；需埋点的指标未埋点一律标 `N/A`，**绝不造数**。
2. **只读纯聚合**：同输入同输出，无副作用；不触发其它命令。
3. **可行动优先**：每个指标对应一个优化动作（映射 `docs/optimization-backlog.md` 的 OPT 项），不堆虚荣指标。
4. **口径分层**：Tier 0 零埋点 / Tier 1 轻埋点（接受率走 git revert 例外，零埋点）/ Tier 2 集成（DORA），详见设计 spec。

## 资源加载规则

- 执行度量聚合时，运行 `scripts/metrics.js`（入口 `/metrics` 命令）
- 阶段计时埋点（供 §6 各阶段周期）用 `scripts/stage-event.js <phase> <start|end> [--task=<id>]`，事件写 `.codebuddy-runtime/stage-events.jsonl`
- 指标定义、数据源、分期口径，读 `docs/specs/2026-06-09-delivery-metrics-design.md`

## 何时使用

1. 周期性看板（`scheduled-automation` 低频任务产周报）
2. 流程优化前后对比（验证 backlog 某 OPT 项是否真有效）
3. 排查摩擦点（哪个门禁最常阻断、哪个自动任务超时、决策挂多久）

## 何时不用

1. 单任务状态 → `/status`
2. AI 交互质量评分 → `/score-interaction`
3. 生产监控/SLO → 运维侧 APM，本技能不接

## 禁止事项

1. 不要在数据缺失时估出数字填上——标 `N/A` 并说明补齐方式
2. 不要把历史欠账解读成当前失控（如规则中途引入导致的全史低合规率，需用 `--since` 窗口区分）
3. 不要让度量产生副作用（写报告到 `docs/quality/metrics-*.md` 即止，已 .gitignore）
