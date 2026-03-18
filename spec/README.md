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

| 阶段命令 | 负责生成或回填的 AI2AI 文档 |
|---|---|
| `/spec-lite` | 只初始化追踪链接占位；如已做过 brainstorm，应回填 `brainstormPath` |
| `/brainstorm` | `Design.md`, `test.md`，并回填 `brainstormPath` |
| `/research` | `research.md` |
| `/write-plan` | `plan.md`, `summary.md` |
| `/execute-plan` | `IMPLEMENTATION_PROGRESS.md`, `IMPLEMENTATION_SUMMARY.md`, `Architecture_Info.md`, `Protocol_and_Data.md` |
| `/testcase` | `testcase.md`, `testcase_analysis.md` |
