# 质量门禁说明

质量门禁脚本位置：

- `.codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1`
- `.codebuddy/skills/process-gatekeeper/scripts/check-quality.sh`

默认检查项：

1. 测试通过率阈值（默认 `100%`）
2. 覆盖率阈值（默认 `80%`）
3. 文档同步状态（`doc-sync-report.json` 为 pass/synced/ok 或 `inSync=true`）
4. `docs/findings.md` 与 `docs/progress.md` 文件存在性

默认输入文件：

- `docs/quality/test-summary.json`
- `docs/quality/doc-sync-report.json`

默认输出文件：

- `docs/quality/last-quality-gate.json`

## test-summary.json 格式

```json
{
  "total": 120,
  "passed": 120,
  "passRate": 100,
  "coverage": {
    "branches": 85.6
  }
}
```

`passRate` 与 `passed/total` 二选一可用；覆盖率可使用 `coverage` 数值，或 `coverage.branches` / `coverage.statements`。

## doc-sync-report.json 格式

```json
{
  "status": "pass",
  "inSync": true
}
```
