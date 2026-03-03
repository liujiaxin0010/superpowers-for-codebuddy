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

## 4. 风险与缓解

| 风险 | 等级(low/med/high) | 缓解措施 |
|---|---|---|
| 迁移中断导致状态不一致 | high | 先灰度回放，按批次迁移并保留回滚点 |

## 5. 验收标准

- [x] 功能验收：重复回放不产生重复状态
- [x] 测试验收：迁移关键路径覆盖率 >= 80%
- [x] 文档验收：迁移说明与回滚文档同步

## 6. 分级输入

- estimatedChangedFiles: 7
- impactedModules: 3
- hasContractChange: false
- hasSecurityOrPermissionImpact: false
- hasDataOrStateMigration: true
- hasCriticalPathPerformanceImpact: true
- isProductionIncidentFix: true

## 7. GateContext

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
    - acceptance_defined
    - risks_defined
    - brainstorm_evidence
  completedChecks:
    - spec_exists
    - acceptance_defined
    - risks_defined
    - brainstorm_evidence
  gateStatus: "pass"
```
