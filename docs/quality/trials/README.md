# 质量门禁试运行记录（3 个需求）

## 场景列表

1. 订单导出能力（M）
2. RBAC 接口收敛（H）
3. 支付状态迁移修复（H）

## 统一命令

```powershell
powershell -ExecutionPolicy Bypass -File .codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1 `
  -TestReportPath <test-summary.json> `
  -DocSyncPath <doc-sync-report.json> `
  -OutputPath <quality-gate.json>
```

## 结果

- 3/3 场景 `PASS`
- 测试通过率均为 `100%`
- 覆盖率均 `>= 80%`
- 文档同步均为 `pass/synced/ok`
