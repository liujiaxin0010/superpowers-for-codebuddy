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

## 4. 需求澄清结论（补填）

- 业务目标与成功标准: 业务侧可按筛选条件导出订单，首屏导出成功率 100%
- 用户/调用方与使用场景: 运营与财务在订单后台列表页按筛选条件导出
- 触发入口与交互路径（API/CLI/定时/UI/任务）: UI 按钮触发 -> 后端导出 API -> 浏览器下载
- 交付形态（接口/命令/任务/页面/配置）: 新增后端导出接口 + 前端导出按钮
- 关键数据对象与范围边界（新增/修改/不改）: 仅复用既有订单聚合数据，不新增持久化对象
- 外部契约与兼容影响: 不影响现有查询 API；新增导出接口不破坏兼容
- 非功能约束（性能/安全/稳定性/合规）: 单次导出超时受控、权限复用现有鉴权
- 观测与运维要求（日志/监控/告警）: 记录导出耗时与失败原因，接入现有告警
- 日志实现策略（旧项目沿用结构 / 新项目框架选型）: 沿用现有结构化日志框架
- 日志字段规范（示例：traceId/module/action/result/errorCode/durationMs）: traceId/module/action/result/durationMs/errorCode
- 日志语言约束（English only）: English only
- 控制台输出策略（默认禁止，除非用户明确要求）: 默认禁止

## 5. 方案方向确认（补填）

### 5.1 候选方向

| 方向 | 核心思路 | 优点 | 风险/代价 | 适用前提 |
|---|---|---|---|---|
| A | 同步导出并限制数据规模 | 实现快、改动小 | 大数据量响应慢 | M 级需求、单次导出量可控 |
| B | 异步任务导出+回调下载 | 大规模更稳 | 成本高、改动大 | H 级或高并发导出 |

### 5.2 用户确认结果

- selectedDirection: A
- rejectedDirections: B
- rejectionReason: 当前不需要异步导出链路
- userHardConstraints: 不改现有查询逻辑；不新增队列
- alternativeDirection: N/A
- unresolvedItems:

## 6. 风险与缓解

| 风险 | 等级(low/med/high) | 缓解措施 |
|---|---|---|
| 导出耗时影响接口响应 | med | 增加分页上限、压测与超时保护 |

## 7. 验收标准

- [x] 功能验收：导出文件字段与筛选条件一致
- [x] 测试验收：相关单元测试通过，覆盖率达标
- [x] 文档验收：接口与模块文档同步

## 8. 回滚方案

关闭前端导出入口并回滚导出 API 路由，恢复到仅查询能力。

## 9. 分级输入

- estimatedChangedFiles: 3
- impactedModules: 2
- hasContractChange: true
- hasSecurityOrPermissionImpact: false
- hasDataOrStateMigration: false
- hasCriticalPathPerformanceImpact: true
- isProductionIncidentFix: false

## 10. GateContext

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
    - clarification_defined
    - solution_direction_confirmed
    - acceptance_defined
    - risks_defined
  completedChecks:
    - spec_exists
    - clarification_defined
    - solution_direction_confirmed
    - acceptance_defined
    - risks_defined
  gateStatus: "pass"
```

## 11. GateResult

```yaml
GateResult:
  status: "pass"
  tier: "M"
  missing: []
  nextCommand: "/write-plan spec=docs/specs/2026-03-02-order-export-spec-lite.md tier=M"
  message: "ready for planning"
```

## 12. 追踪链接

- researchPath: spec/AI2AI/research.md
- brainstormPath:
- designPath: spec/AI2AI/Design.md
- testStrategyPath: spec/AI2AI/test.md
- planPath: docs/plans/2026-03-02-order-export-plan.md
- testcasePath: spec/AI2AI/testcase.md
- testcaseAnalysisPath: spec/AI2AI/testcase_analysis.md
- implementationProgressPath: spec/AI2AI/IMPLEMENTATION_PROGRESS.md
- implementationSummaryPath: spec/AI2AI/IMPLEMENTATION_SUMMARY.md
- reviewReportPath:
