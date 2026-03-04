# <功能名称> Spec-Lite

## 元信息

- taskId: <YYYYMMDD-short-id>
- createdAt: <YYYY-MM-DD HH:mm>
- sourceCommand: /spec-lite
- explore: <true|false>

## 1. 目标

<期望达成的业务结果>

## 2. 范围外

<明确不做的事项>

## 3. 接口与数据影响

- API/LAPI/OpenAPI:
- DB/Redis/Event/Config:
- 外部契约是否变化:

## 4. 需求澄清结论（必填）

- 业务目标与成功标准:
- 用户/调用方与使用场景:
- 触发入口与交互路径（API/CLI/定时/UI/任务）:
- 交付形态（接口/命令/任务/页面/配置）:
- 关键数据对象与范围边界（新增/修改/不改）:
- 外部契约与兼容影响:
- 非功能约束（性能/安全/稳定性/合规）:
- 观测与运维要求（日志/监控/告警）:
- 日志实现策略（旧项目沿用结构 / 新项目框架选型）:
- 日志字段规范（示例：traceId/module/action/result/errorCode/durationMs）:
- 日志语言约束（English only）:
- 控制台输出策略（默认禁止，除非用户明确要求）:

## 5. 方案方向确认（必填）

### 5.1 候选方向（至少 2 项）

| 方向 | 核心思路 | 优点 | 风险/代价 | 适用前提 |
|---|---|---|---|---|
| A |  |  |  |  |
| B |  |  |  |  |

### 5.2 用户确认结果

- selectedDirection:
- rejectedDirections:
- rejectionReason:
- userHardConstraints:
- alternativeDirection: <若拒绝候选方向，必须明确替代方向>
- unresolvedItems: <若存在未决项需列出；为空才可进入 write-plan>

## 6. 风险与缓解

| 风险 | 等级(low/med/high) | 缓解措施 |
|---|---|---|
|  |  |  |

## 7. 验收标准

- [ ] 功能验收：
- [ ] 测试验收：
- [ ] 文档验收：

## 8. 回滚方案

<回滚步骤与影响范围>

## 9. 分级输入

- estimatedChangedFiles: <number>
- impactedModules: <number>
- hasContractChange: <true|false>
- hasSecurityOrPermissionImpact: <true|false>
- hasDataOrStateMigration: <true|false>
- hasCriticalPathPerformanceImpact: <true|false>
- isProductionIncidentFix: <true|false>

## 10. GateContext

```yaml
GateContext:
  taskId: ""
  recommendedTier: "L|M|H"
  finalTier: "L|M|H"
  overrideReason: ""
  specPath: "docs/specs/..."
  planPath: ""
  requiredChecks:
    - spec_exists
    - clarification_defined
    - solution_direction_confirmed
    - acceptance_defined
    - risks_defined
  completedChecks: []
  gateStatus: "pass|blocked"
```

## 11. GateResult

```yaml
GateResult:
  status: "pass|blocked"
  tier: "L|M|H"
  missing: []
  nextCommand: ""
  message: ""
```

## 12. 追踪链接

- researchPath: <研究阶段回填>
- brainstormPath: <H 级任务必填>
- designPath: <方案设计文档回填>
- testStrategyPath: <测试策略文档回填>
- planPath: <规划后回填>
- testcasePath: <测试用例文档回填>
- testcaseAnalysisPath: <测试分析文档回填>
- implementationProgressPath: <执行阶段回填>
- implementationSummaryPath: <执行阶段回填>
- reviewReportPath: <审查后回填>
