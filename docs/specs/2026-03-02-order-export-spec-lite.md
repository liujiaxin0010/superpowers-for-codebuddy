# 订单导出能力 Spec-Lite

## 1. 目标

在订单列表新增 Excel 导出能力，不影响现有查询与分页逻辑。

## 2. 范围外

- 不改动订单创建/支付流程
- 不新增异步导出队列

## 3. 接口与数据影响

- API/LAPI/OpenAPI: 新增 `GET /orders/export`
- DB/Redis/Event/Config: 无结构变更
- 外部契约是否变化: 否

## 4. 风险与缓解

| 风险 | 等级(low/med/high) | 缓解措施 |
|---|---|---|
| 导出耗时影响接口响应 | med | 增加分页上限、压测与超时保护 |

## 5. 验收标准

- [x] 功能验收：导出文件字段与筛选条件一致
- [x] 测试验收：相关单元测试通过，覆盖率达标
- [x] 文档验收：接口与模块文档同步

## 6. 分级输入

- estimatedChangedFiles: 3
- impactedModules: 2
- hasContractChange: true
- hasSecurityOrPermissionImpact: false
- hasDataOrStateMigration: false
- hasCriticalPathPerformanceImpact: true
- isProductionIncidentFix: false

## 7. GateContext

```yaml
GateContext:
  taskId: "20260302-order-export"
  recommendedTier: "M"
  finalTier: "M"
  overrideReason: ""
  specPath: "docs/specs/2026-03-02-order-export-spec-lite.md"
  planPath: "docs/plans/2026-03-02-order-export-plan.md"
  requiredChecks:
    - spec_exists
    - acceptance_defined
    - risks_defined
  completedChecks:
    - spec_exists
    - acceptance_defined
    - risks_defined
  gateStatus: "pass"
```
