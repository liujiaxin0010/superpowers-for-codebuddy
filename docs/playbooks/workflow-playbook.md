# Featureflow 工作流实操手册

这份 playbook 负责把 `website` 中抽象出来的 workflow 模式，映射到当前仓库可执行的命令体系。

## Workflow 1：新功能用 `spec-first`

### 什么时候用

- 需求会跨多个文件或模块
- 很容易边做边扩范围
- 需要交给别人 review 或异步接力

### 当前仓库链路

1. 若明确要需求预分析文档，或需求属于 `must/should-brainstorm`，先 `/brainstorm`
2. `/spec-lite`
3. 若 `finalTier=H` 且 `brainstormPath` 缺失，执行 `/brainstorm spec=<specPath> tier=H`
4. `/write-plan`
5. `/execute-plan`
6. `/test-gen` 或 `/unified-test`
7. `/code-review`
8. `check-quality.ps1/.sh`

### 合同模板

- `.codebuddy/templates/task-contracts/new-feature.md`

## Workflow 2：已知 bug 用 `bugfix`

### 什么时候用

- 已经能复现
- 目标是关闭缺陷，不是顺手重构
- 改动范围应该尽量小

### 当前仓库链路

1. `/fix-bug`
2. 生成 bugfix contract
3. 根因定位
4. 最小修复
5. 最小复现关闭 + 相关回归
6. 必要时 `/code-self-check` / `/code-review`

### 合同模板

- `.codebuddy/templates/task-contracts/bugfix.md`

## Workflow 3：工单任务用 `issue / Jira -> draft PR`

### 什么时候用

- 任务已经在 issue 或 Jira 里
- 目标与验收相对清晰
- 可以接受 agent 异步推进

### 当前仓库链路

1. `/issue-draft-pr` 固化工单输入并检查 acceptance criteria
2. 若需求仍模糊，回退 `/spec-lite`
3. `/write-plan`
4. `/execute-plan`
5. `/code-review`
6. 输出 draft PR 所需说明与证据

## Workflow 4：长任务用 `parallel delivery`

### 什么时候用

- 任务可拆成低耦合子项
- 多个 agent 并行确实能节省时间
- 有明确 owner 负责最终合流

### 当前仓库链路

1. `/parallel-delivery` 检查并输出并行组
2. 使用 `dispatching-parallel-agents`
3. Git 项目配合 `using-git-worktrees`
4. 子任务各自提交验证证据
5. owner 做统一 review、整体验证、质量门禁

### 合同模板

- `.codebuddy/templates/task-contracts/parallel-delivery.md`

## 通用验收清单

1. 任务目标仍与最初一致
2. 没有改到范围外的目录或接口
3. 验证命令真实执行过
4. 证据包含失败与成功信息，而不是只有结论
5. 剩余风险已声明
6. merge / handoff owner 明确
7. 失败模式已回写到合同模板、门禁或规则
