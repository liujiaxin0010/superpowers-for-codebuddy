# AI 特性流程映射（指南兼容层）

## 目标

将《AI特性流程开发指南》的阶段流程映射到当前仓库命令体系，保持 `docs/*` 主流程不变。

## 目录策略

1. `docs/*`：主产物与门禁事实源
2. `spec/Me2AI`：人类输入兼容层
3. `spec/AI2AI`：AI 过程文档兼容层

## 阶段映射

| 指南阶段 | 推荐命令 | 主产物（docs） | 兼容产物（spec/AI2AI） |
|---|---|---|---|
| 阶段1 工程研究 | `/research` | `docs/specs/*`（追踪链接） | `research.md` |
| 阶段2 方案分析 | `/brainstorm` + `/spec-lite` | `docs/specs/*-spec-lite.md` | `Design.md`, `test.md` |
| 阶段2 计划编写 | `/write-plan` | `docs/plans/*.md` | `plan.md`, `summary.md` |
| 阶段2 执行编码 | `/execute-plan` | `docs/progress.md`, `docs/findings.md` | `IMPLEMENTATION_PROGRESS.md`, `IMPLEMENTATION_SUMMARY.md`, `Architecture_Info.md`, `Protocol_and_Data.md` |
| 阶段3 测试用例 | `/testcase` | `docs/specs/*`（追踪链接） | `testcase.md`, `testcase_analysis.md` |
| 阶段4 代码自检 | `/code-self-check` | `docs/quality/code-self-check-report.md` | - |
| 质量收尾 | `check-quality.ps1/.sh` | `docs/quality/last-quality-gate.json` | 可选 AI2AI 存在性校验 |

## 推荐命令链

### L/M 任务

```bash
/spec-lite <需求描述>
/research <需求或模块> spec=<specPath> tier=<L|M>
/write-plan spec=<specPath> tier=<L|M>
/execute-plan <planPath> spec=<specPath> tier=<L|M>
/testcase target=<pathOrModule> spec=<specPath> plan=<planPath> tier=<L|M>
/code-self-check vcs=auto
```

### H 任务

```bash
/spec-lite <需求描述>
/brainstorm <需求描述> spec=<specPath> tier=H
/research <需求或模块> spec=<specPath> tier=H
/write-plan spec=<specPath> tier=H
/execute-plan <planPath> spec=<specPath> tier=H
/testcase target=<pathOrModule> spec=<specPath> plan=<planPath> tier=H
/code-self-check vcs=auto
```

## 追踪链接字段（spec-lite）

1. `researchPath`
2. `designPath`
3. `testStrategyPath`
4. `testcasePath`
5. `testcaseAnalysisPath`
6. `implementationProgressPath`
7. `implementationSummaryPath`

