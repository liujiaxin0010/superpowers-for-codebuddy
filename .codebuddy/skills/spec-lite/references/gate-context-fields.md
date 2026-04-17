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

1. `brainstormPath`
2. `researchPath`
3. `designPath`
4. `testStrategyPath`
5. `testcasePath`
6. `testcaseAnalysisPath`
7. `implementationProgressPath`
8. `implementationSummaryPath`

这些字段允许在 spec 阶段先占位，由后续 `/brainstorm`、`/research`、`/write-plan`、`/execute-plan`、`/testcase` 按阶段回填；不要求在 `/spec-lite` 阶段一次性生成所有 `spec/AI2AI/*` 实体文档。
