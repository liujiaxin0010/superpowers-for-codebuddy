# Spec Compatibility Layer

本目录用于兼容《AI特性流程开发指南》的 `spec/Me2AI + spec/AI2AI` 产物约定。

当前仓库保持以下原则：

1. `docs/*` 为主事实源（主流程产物与门禁依赖不变）。
2. `spec/*` 为兼容层（用于承接指南流程与阶段文档）。
3. 关键路径通过 `docs/specs/*` 的“追踪链接”字段关联 `spec/AI2AI/*`。

## 目录说明

| 路径 | 责任主体 | 说明 |
|---|---|---|
| `spec/Me2AI/需求描述.md` | 人类 | 需求输入与业务目标 |
| `spec/Me2AI/技术约束.md` | 人类 | 技术栈、架构与硬约束 |
| `spec/AI2AI/*.md` | AI | 研究、设计、计划、测试、实施沉淀 |

## 与 docs 的关系

| docs 主产物 | spec 兼容产物 |
|---|---|
| `docs/specs/*-spec-lite.md` | `spec/AI2AI/Design.md`, `spec/AI2AI/plan.md`, `spec/AI2AI/summary.md` |
| `docs/plans/*.md` | `spec/AI2AI/plan.md`, `spec/AI2AI/IMPLEMENTATION_PROGRESS.md` |
| `docs/quality/*.json` | `spec/AI2AI/testcase.md`, `spec/AI2AI/testcase_analysis.md` |

