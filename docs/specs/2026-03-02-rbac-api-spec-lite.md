# RBAC 接口收敛 Spec-Lite

## 1. 目标

统一角色鉴权接口的输入参数与错误码，减少前后端分支处理。

## 2. 范围外

- 不调整账号体系
- 不引入新权限模型

## 3. 接口与数据影响

- API/LAPI/OpenAPI: 调整 `POST /auth/check` 返回结构
- DB/Redis/Event/Config: 无结构变更
- 外部契约是否变化: 是

## 4. 风险与缓解

| 风险 | 等级(low/med/high) | 缓解措施 |
|---|---|---|
| 老客户端错误码兼容风险 | high | 提前发布变更公告，保留灰度窗口 |

## 5. 验收标准

- [x] 功能验收：新旧角色场景返回一致
- [x] 测试验收：鉴权分支覆盖率 >= 80%
- [x] 文档验收：鉴权接口文档同步完成

## 6. 分级输入

- estimatedChangedFiles: 5
- impactedModules: 2
- hasContractChange: true
- hasSecurityOrPermissionImpact: true
- hasDataOrStateMigration: false
- hasCriticalPathPerformanceImpact: false
- isProductionIncidentFix: false

## 7. GateContext

```yaml
GateContext:
  taskId: "20260302-rbac-api"
  recommendedTier: "H"
  finalTier: "H"
  overrideReason: ""
  specPath: "docs/specs/2026-03-02-rbac-api-spec-lite.md"
  planPath: "docs/plans/2026-03-02-rbac-api-plan.md"
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
