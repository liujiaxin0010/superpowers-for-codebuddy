# 规格兼容层说明

本目录用于兼容《AI特性流程开发指南》的 `spec/Me2AI + spec/AI2AI` 产物约定。

当前仓库保持以下原则：

1. `docs/*` 为主事实源（主流程产物与门禁依赖不变）。
2. `spec/*` 为兼容层（用于承接指南流程与阶段文档）。
3. 关键路径通过 `docs/specs/*` 的“追踪链接”字段关联 `spec/AI2AI/*`。
4. `/spec-lite` 只初始化追踪链接，不要求一次性生成全部 `spec/AI2AI/*` 文档。

## 目录说明

| 路径 | 责任主体 | 说明 |
|---|---|---|
| `spec/Me2AI/需求描述.md` | 人类 | 需求输入与业务目标 |
| `spec/Me2AI/技术约束.md` | 人类 | 技术栈、架构与硬约束 |
| `spec/AI2AI/*.md` | AI | 研究、设计、计划、测试、实施沉淀 |

## 与 docs 的关系

| docs 主产物 | spec 兼容产物 |
|---|---|
| `docs/specs/*-spec-lite.md` | 追踪链接（`brainstorm/research/design/test/plan/testcase/implementation` 等阶段产物） |
| `docs/plans/*.md` | 需求预分析与实施计划主文档，可关联 `plan.md` 与执行阶段 AI2AI 文档 |
| `docs/quality/*.json` | 质量门禁结果；可选校验 AI2AI 测试与执行文档是否齐备 |

## 分阶段生成约定

| 阶段命令 | 负责生成或回填的 AI2AI 文档 / 追踪字段 |
|---|---|
| `/extend` Step 0.2 | `docs/specs/*-historical-spec.md`，回填 `historicalSpecPath` |
| `/extend` Step 0.4 | `docs/specs/*-requirement-analysis.md`，回填 `requirementAnalysisPath` |
| `/spec-lite` | 初始化追踪链接占位；若存在上游需求分析，必须生成覆盖矩阵（`coverageMatrixPath`） |
| `/brainstorm` | `Design.md`, `test.md`，回填 `brainstormPath / designPath / testStrategyPath` |
| `/research` | `research.md`，回填 `researchPath` |
| `/write-plan` | `plan.md`, `summary.md`，回填 `planPath`；同步补齐覆盖矩阵中的 `planTaskId` |
| `/execute-plan` | `IMPLEMENTATION_PROGRESS.md`, `IMPLEMENTATION_SUMMARY.md`, `Architecture_Info.md`, `Protocol_and_Data.md`；同步维护覆盖矩阵 `status / implementationRef` |
| `/testcase` | `testcase.md`, `testcase_analysis.md`；同步补齐覆盖矩阵 `verificationTestId` |
| `/requirement-coverage` | `docs/quality/requirement-coverage-report.md(.xlsx)`，回填 `coverageReportPath` |
| `/security-review` | `docs/quality/security-review-report.md`，回填 `securityReviewReportPath` |
| `/perf-check` | `docs/quality/perf-report.md` 与 `.codebuddy/state/perf-baseline/*.json`，回填 `perfBaselinePath / perfReportPath` |
| `/system-test` | `docs/quality/system-test-report.md`，回填 `systemTestReportPath` |
| `/release` | `CHANGELOG.md` 新增条目与 `docs/release/YYYY-MM-DD-release-notes.md`，回填 `releaseNotesPath / rollbackPlaybookPath` |
