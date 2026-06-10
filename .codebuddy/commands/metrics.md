请先阅读并遵循：
1. `docs/specs/2026-06-09-delivery-metrics-design.md`（度量设计、指标定义、分期口径）
2. 聚合器实现 `scripts/metrics.js`（Tier 0，只读纯聚合）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
聚合当前项目现有产物，产出一份交付效能度量报告，并指出 Top 摩擦点。**只读**——不改源码、不触发其它命令、不臆造数据（缺失数据一律标 `N/A`）。

执行步骤：

1. **运行聚合器**：
   - `node scripts/metrics.js [--since=YYYY-MM-DD] [--format=md|json] [--jobs=<jobs.jsonl 路径>]`
   - 默认窗口最近 30 天、md 格式、报告写入 `docs/quality/metrics-<date>.md`
   - 业务项目若接了 event-triggers，`--jobs` 指向接收器 `stateDir/jobs.jsonl` 以纳入自动化 ROI
   - Tier 1：`--stages` 指向阶段计时台账、`--defects` 指向缺陷台账（默认探测 `.codebuddy-runtime/`）；自动修复接受率从 git revert 关系算，零埋点即真实

2. **解读而非堆数字**：
   - 先讲 **Top 摩擦点**（阻断最多的门禁 / 超时最多的任务 / 最久挂起的决策 / 不合规提交），每条对应一个可行动建议
   - 标注数据口径与局限：Tier 0 的合规率/覆盖率等是窗口内现状；若仓库中途才引入某规则（如 AI 标签），需说明历史提交会拉低合规率，不等于当前流程失控
   - 门禁数据若 `checkedAt` 过期，明确提示"指标可能不反映当前状态"，建议重跑 `check-quality`

3. **给出下一步**：
   - 把摩擦点映射到 `docs/optimization-backlog.md` 的对应 OPT 项
   - 数据缺口（如无 `jobs.jsonl` / 无 `pending-decisions.md`）说明补齐方式，不阻断报告

补充约束：
- 纯聚合、可复现：同输入同输出，无副作用
- 不接生产监控/APM（那是运维侧）；不替代 `/score-interaction`（那是 AI 交互质量，本命令是交付吞吐与质量）
- 报告默认中文

$ARGUMENTS
