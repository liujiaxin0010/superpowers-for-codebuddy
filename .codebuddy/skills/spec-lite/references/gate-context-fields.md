# Spec-Lite 字段定义

## GateContext 字段

1. taskId
2. taskType
3. workflow
4. recommendedTier
5. finalTier
6. overrideReason
7. specPath
8. planPath
9. requiredChecks
10. completedChecks
11. gateStatus (`pass|blocked`)
12. coverageMatrixPath（结构化覆盖矩阵 YAML/JSON 块的定位；上游有 requirement-analysis/brainstorm 时必填）
13. coverageRowCount（覆盖矩阵行数，与 requirement-analysis 的 REQ 数一致）
14. unmatchedReqs[]（尚未填齐 specSection/planTaskId/verificationTestId 的 REQ ID 列表；非空则阻断 /write-plan）
15. historicalSpecPath（`/extend` 必填）
16. requirementAnalysisPath（`/extend` / 复杂任务必填）

## TaskContract 字段

1. templatePath
2. taskType
3. objective
4. background
5. editablePaths
6. forbiddenPaths
7. relatedFiles
8. verificationCommands
9. deliverables
10. evidence
11. humanCheckpoints
12. owner
13. outOfScopeHandling

## GateResult 字段

1. status (`pass|blocked`)
2. tier
3. missing[]
4. nextCommand
5. message

## 追踪链接扩展字段

在 spec 文档"追踪链接"中补充以下兼容字段：

1. `historicalSpecPath`（由 `/extend` Step 0.2 生成；非扩展场景允许为空）
2. `requirementAnalysisPath`（由 `/extend` Step 0.4 或 `/brainstorm` 复杂任务生成）
3. `brainstormPath`
4. `researchPath`
5. `designPath`
6. `testStrategyPath`
7. `testcasePath`
8. `testcaseAnalysisPath`
9. `implementationProgressPath`
10. `implementationSummaryPath`
11. `coverageMatrixPath`（覆盖矩阵结构化产物，`spec` 或 `plan` 末尾的 YAML/JSON 块的 anchor 路径）
12. `coverageReportPath`（`/requirement-coverage` 执行后回填）
13. `securityReviewReportPath`（`/security-review` 执行后回填）
14. `perfBaselinePath` / `perfReportPath`（`/perf-check` 执行后回填）
15. `systemTestReportPath`（`/system-test` 执行后回填）
16. `releaseNotesPath` / `rollbackPlaybookPath`（`/release` / `/rollback` 相关）

这些字段允许在 spec 阶段先占位，由后续阶段按需回填；不要求在 `/spec-lite` 阶段一次性生成所有实体文档。
