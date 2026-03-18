# Featureflow 特性流程映射（指南兼容层）

## 目标

将《AI特性流程开发指南》的阶段流程映射到当前仓库命令体系，保持 `docs/*` 主流程不变。

## 任务类型映射

| 任务类型 | 默认入口 / 组合入口 | 合同模板 | 关键证据 |
|---|---|---|---|
| `new-feature` | `/spec-lite -> /write-plan -> /execute-plan` | `.codebuddy/templates/task-contracts/new-feature.md` | 验收命令 + review 结论 |
| `bugfix` | `/fix-bug` | `.codebuddy/templates/task-contracts/bugfix.md` | 根因 + 最小复现关闭 + 回归 |
| `refactor` | `/write-plan -> /execute-plan -> /simplify` | `.codebuddy/templates/task-contracts/refactor.md` | 行为不变证据 |
| `test` | `/test-gen` / `/unified-test` | `.codebuddy/templates/task-contracts/test.md` | 测试输出 + 覆盖缺口 |
| `research` | `/research` | `.codebuddy/templates/task-contracts/research.md` | 结论 + 备选方案 |
| `review-pr` | `/code-review` + `/code-self-check` | `.codebuddy/templates/task-contracts/review-pr.md` | 证据完整性 + 风险声明 |
| `issue-draft-pr` | 组合链路 | `.codebuddy/templates/task-contracts/issue-draft-pr.md` | 工单映射 + draft PR 说明 |
| `parallel-delivery` | `/write-plan + dispatching-parallel-agents + using-git-worktrees` | `.codebuddy/templates/task-contracts/parallel-delivery.md` | 每 lane 证据 + 合流验证 |

## 目录策略

1. `docs/*`：主产物与门禁事实源
2. `spec/Me2AI`：人类输入兼容层
3. `spec/AI2AI`：AI 过程文档兼容层
4. `spec/AI2AI` 由各阶段命令按需生成，不要求在 `/spec-lite` 阶段一次性齐全

## 阶段映射

| 指南阶段 | 推荐命令 | 主产物（docs） | 兼容产物（spec/AI2AI） |
|---|---|---|---|
| 阶段1 工程研究 | `/research` | `docs/specs/*`（追踪链接） | `research.md` |
| 阶段2 方案分析 | `/brainstorm` + `/spec-lite`，或清晰 H 需求走 `/spec-lite -> /brainstorm` | `docs/specs/*-spec-lite.md` | `Design.md`, `test.md` |
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

两条入口都合法：

1. 模糊需求或明确要需求预分析文档：`/brainstorm -> /spec-lite -> ...`
2. 需求较清晰但 `/spec-lite` 判定为 `H`：`/spec-lite -> /brainstorm -> ...`

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

1. `brainstormPath`
2. `researchPath`
3. `designPath`
4. `testStrategyPath`
5. `testcasePath`
6. `testcaseAnalysisPath`
7. `implementationProgressPath`
8. `implementationSummaryPath`

