请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/performance-baseline/SKILL.md`（性能基线）

**务必遵守四条铁律（见 CODEBUDDY.md §1）。**

**你的任务是：**
基于基线对本次变更做性能回归判定。

执行步骤：

1. 解析参数：`/perf-check scope=<name> [baseline=<path>] [threshold=5|10] [env=prod|staging|dev]`
2. 调用 `process-gatekeeper`（`command=perf-check`）
3. 若阻断：输出阻断报告并停止
4. 读取基线：`.codebuddy/state/perf-baseline/<scope>.json`
   - 不存在 → 进入"建立基线"子流程（固定负载 / 机型 / 至少 3 次运行取中位数）
5. 执行本次压测 / benchmark，记录 p50 / p95 / p99 / QPS / 错误率 / CPU / 内存
6. 生成对比报告：`docs/quality/perf-report-<scope>.md`
7. 判定：
   - 任一关键指标回归超 `thresholdPct` → 🔴 BLOCKED
   - 阈值内但趋势不好 → 🟠 建议审查
   - 无回归 → ✅ 通过
8. 若 🔴：输出根因初判 + 修复建议；或 Boss 显式签字豁免
9. 通过 / 签字后，若本次是"建立基线"或"刷新基线"，更新 `.codebuddy/state/perf-baseline/<scope>.json`（含 `updatedAt` 与变更原因）
10. 回填 spec 中的 `perfReportPath`
11. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
