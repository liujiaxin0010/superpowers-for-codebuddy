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

## 4. 需求澄清结论（补填）

- 业务目标与成功标准: 同一权限场景仅存在一套接口语义与错误码
- 用户/调用方与使用场景: 前端网关、内部服务统一调用鉴权接口
- 触发入口与交互路径（API/CLI/定时/UI/任务）: 服务调用鉴权 API -> 统一结果码映射
- 交付形态（接口/命令/任务/页面/配置）: 鉴权 API 契约收敛 + 文档更新
- 关键数据对象与范围边界（新增/修改/不改）: 修改请求响应字段映射，不改用户/角色核心表
- 外部契约与兼容影响: 存在契约变更，需要灰度与公告
- 非功能约束（性能/安全/稳定性/合规）: 鉴权延迟不退化，安全策略不降级
- 观测与运维要求（日志/监控/告警）: 鉴权失败分类统计，关键错误码告警
- 日志实现策略（旧项目沿用结构 / 新项目框架选型）: 沿用既有鉴权日志结构
- 日志字段规范（示例：traceId/module/action/result/errorCode/durationMs）: traceId/module/action/result/errorCode/durationMs
- 日志语言约束（English only）: English only
- 控制台输出策略（默认禁止，除非用户明确要求）: 默认禁止

## 5. 方案方向确认（补填）

### 5.1 候选方向

| 方向 | 核心思路 | 优点 | 风险/代价 | 适用前提 |
|---|---|---|---|---|
| A | 统一接口契约并同步改造调用方 | 语义一致性强 | 变更范围较大 | 可安排灰度窗口 |
| B | 兼容层转换，渐进迁移 | 迁移平滑 | 增加中间层复杂度 | 允许兼容代码 |

### 5.2 用户确认结果

- selectedDirection: A
- rejectedDirections: B
- rejectionReason: 当前规则禁止默认兼容性代码
- userHardConstraints: 必须统一错误码；必须保留鉴权安全基线
- alternativeDirection: N/A
- unresolvedItems:

## 6. 风险与缓解

| 风险 | 等级(low/med/high) | 缓解措施 |
|---|---|---|
| 老客户端错误码兼容风险 | high | 提前发布变更公告，保留灰度窗口 |

## 7. 验收标准

- [x] 功能验收：新旧角色场景返回一致
- [x] 测试验收：鉴权分支覆盖率 >= 80%
- [x] 文档验收：鉴权接口文档同步完成

## 8. 回滚方案

回滚到上一版接口协议并恢复原错误码映射表。

## 9. 分级输入

- estimatedChangedFiles: 5
- impactedModules: 2
- hasContractChange: true
- hasSecurityOrPermissionImpact: true
- hasDataOrStateMigration: false
- hasCriticalPathPerformanceImpact: false
- isProductionIncidentFix: false

## 10. GateContext

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
  nextCommand: "/brainstorm RBAC 接口收敛 spec=docs/specs/2026-03-02-rbac-api-spec-lite.md tier=H"
  message: "H-tier requires brainstorm evidence before planning"
```

## 12. 追踪链接

- researchPath: spec/AI2AI/research.md
- brainstormPath: docs/plans/2026-03-02-rbac-api-需求预分析.md
- designPath: spec/AI2AI/Design.md
- testStrategyPath: spec/AI2AI/test.md
- planPath: docs/plans/2026-03-02-rbac-api-plan.md
- testcasePath: spec/AI2AI/testcase.md
- testcaseAnalysisPath: spec/AI2AI/testcase_analysis.md
- implementationProgressPath: spec/AI2AI/IMPLEMENTATION_PROGRESS.md
- implementationSummaryPath: spec/AI2AI/IMPLEMENTATION_SUMMARY.md
- reviewReportPath:
