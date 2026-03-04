# 支付状态迁移修复 Spec-Lite

## 1. 目标

修复支付状态迁移流程中的重复写入问题，保证幂等与可回滚。

## 2. 范围外

- 不调整支付渠道对接
- 不重构交易核心模型

## 3. 接口与数据影响

- API/LAPI/OpenAPI: 无外部接口变化
- DB/Redis/Event/Config: 涉及状态迁移脚本与事件重放
- 外部契约是否变化: 否

## 4. 需求澄清结论（补填）

- 业务目标与成功标准: 迁移重复回放不产生重复状态写入，账务状态一致
- 用户/调用方与使用场景: 运维批量迁移任务、支付服务事件重放链路
- 触发入口与交互路径（API/CLI/定时/UI/任务）: 迁移任务入口 -> 状态转换 -> 落库与审计
- 交付形态（接口/命令/任务/页面/配置）: 迁移逻辑修复 + 回滚脚本 + 验证任务
- 关键数据对象与范围边界（新增/修改/不改）: 修改迁移状态机与幂等键，不改支付渠道接口
- 外部契约与兼容影响: 对外接口无变化
- 非功能约束（性能/安全/稳定性/合规）: 迁移窗口内系统稳定，故障可快速回滚
- 观测与运维要求（日志/监控/告警）: 迁移批次日志、失败告警、重复写入计数监控
- 日志实现策略（旧项目沿用结构 / 新项目框架选型）: 沿用现有支付链路日志规范
- 日志字段规范（示例：traceId/module/action/result/errorCode/durationMs）: traceId/module/action/result/errorCode/durationMs/batchId
- 日志语言约束（English only）: English only
- 控制台输出策略（默认禁止，除非用户明确要求）: 默认禁止

## 5. 方案方向确认（补填）

### 5.1 候选方向

| 方向 | 核心思路 | 优点 | 风险/代价 | 适用前提 |
|---|---|---|---|---|
| A | 迁移状态机加幂等键并批次回放 | 风险可控、可回滚 | 需要补充迁移脚本与验证用例 | 有可用灰度窗口 |
| B | 全量重建迁移流程 | 一次性彻底重做 | 成本高、发布风险高 | 有较长停机窗口 |

### 5.2 用户确认结果

- selectedDirection: A
- rejectedDirections: B
- rejectionReason: 重建方案成本高且不满足当前窗口
- userHardConstraints: 必须可回滚；必须保留审计链路
- alternativeDirection: N/A
- unresolvedItems:

## 6. 风险与缓解

| 风险 | 等级(low/med/high) | 缓解措施 |
|---|---|---|
| 迁移中断导致状态不一致 | high | 先灰度回放，按批次迁移并保留回滚点 |

## 7. 验收标准

- [x] 功能验收：重复回放不产生重复状态
- [x] 测试验收：迁移关键路径覆盖率 >= 80%
- [x] 文档验收：迁移说明与回滚文档同步

## 8. 回滚方案

按批次回滚迁移状态并恢复上一版迁移脚本，保留审计记录。

## 9. 分级输入

- estimatedChangedFiles: 7
- impactedModules: 3
- hasContractChange: false
- hasSecurityOrPermissionImpact: false
- hasDataOrStateMigration: true
- hasCriticalPathPerformanceImpact: true
- isProductionIncidentFix: true

## 10. GateContext

```yaml
GateContext:
  taskId: "20260302-payment-migration"
  recommendedTier: "H"
  finalTier: "H"
  overrideReason: ""
  specPath: "docs/specs/2026-03-02-payment-migration-spec-lite.md"
  planPath: "docs/plans/2026-03-02-payment-migration-plan.md"
  requiredChecks:
    - spec_exists
    - clarification_defined
    - solution_direction_confirmed
    - acceptance_defined
    - risks_defined
    - brainstorm_evidence
  completedChecks:
    - spec_exists
    - clarification_defined
    - solution_direction_confirmed
    - acceptance_defined
    - risks_defined
    - brainstorm_evidence
  gateStatus: "pass"
```

## 11. GateResult

```yaml
GateResult:
  status: "pass"
  tier: "H"
  missing: []
  nextCommand: "/brainstorm 支付状态迁移并修复重复写入 spec=docs/specs/2026-03-02-payment-migration-spec-lite.md tier=H"
  message: "H-tier requires brainstorm evidence before planning"
```

## 12. 追踪链接

- researchPath: spec/AI2AI/research.md
- brainstormPath: docs/plans/2026-03-02-payment-migration-需求预分析.md
- designPath: spec/AI2AI/Design.md
- testStrategyPath: spec/AI2AI/test.md
- planPath: docs/plans/2026-03-02-payment-migration-plan.md
- testcasePath: spec/AI2AI/testcase.md
- testcaseAnalysisPath: spec/AI2AI/testcase_analysis.md
- implementationProgressPath: spec/AI2AI/IMPLEMENTATION_PROGRESS.md
- implementationSummaryPath: spec/AI2AI/IMPLEMENTATION_SUMMARY.md
- reviewReportPath:
