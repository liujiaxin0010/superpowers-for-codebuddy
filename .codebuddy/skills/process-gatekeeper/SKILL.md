---
name: process-gatekeeper
description: 命令执行前置项的硬性流程门禁。用于在 `/write-plan`、`/execute-plan`、`/research`、`/testcase`、`/code-review`、`/fix-bug`、`/Featureflow` 等命令进入主体前检查 spec、plan、TaskContract、tier、owner、验证命令和头脑风暴证据是否齐备；若不满足则返回 `BLOCKED` 并给出下一条命令。
---

# 流程门禁（Process Gatekeeper）

## 目标

在命令执行前进行前置检查。若检查失败，返回 `BLOCKED` 并立即停止。

## 输入

```yaml
command: "write-plan|execute-plan|test-gen|unified-test|code-review|extend|brainstorm|status|research|testcase|code-self-check|fix-bug|issue-draft-pr|parallel-delivery|Featureflow"
tier: "L|M|H"
spec: "docs/specs/..."
plan: "docs/plans/..."
target: "..."
```

## 输出

```yaml
GateResult:
  status: "pass|blocked"
  tier: "L|M|H"
  missing: []
  nextCommand: ""
  message: ""
```

## 规则

1. 门禁是阻断机制，不是建议机制。
2. 任一必需项缺失即返回 `blocked`。
3. `blocked` 状态必须提供可执行的 `nextCommand`。
4. `blocked` 状态下必须停止命令主体。

## 命令要求

详见 `gate-matrix.md`。

## 门禁矩阵使用规则

### 何时读取 `gate-matrix.md`

1. 已知 `command` 后，优先只查该命令对应行
2. 只有在需要比较多个候选命令时，才扩大到多行

### 不要怎么读

1. 不要每次都把整张矩阵全文加载进上下文
2. 不要在未确定 `command` 时就开始逐条套所有门禁

## 输出协议

### 阻断时

优先使用：`templates/blocked-report.md`

输出必须包含：

1. `command`
2. `tier`
3. `missing[]`
4. `reason`
5. `nextCommand`

### 通过时

优先使用：`templates/pass-report.md`

输出必须包含：

1. `command`
2. `tier`
3. `completedChecks[]`

## 脚本使用规则

### `scripts/check-gates.*`

当门禁字段需要做确定性检查时使用，用于：

1. 校验 spec/plan/contract 关键字段是否存在
2. 统一返回 pass / blocked 结果

### `scripts/check-quality.*`

只在接近收尾、发布前或质量闸口阶段使用；不要在普通前置门禁中提前运行。

### Spec 完整性约束

进入 `/write-plan` 前，必须确认 spec 中以下内容已明确：

1. 需求澄清结论（目标、场景、边界、约束）
2. 方案方向确认（候选方向 + 用户已确认方向）
3. 用户拒绝记录（若有）与替代方向/硬约束
4. 日志策略（沿用项目日志结构或新项目日志框架选型，且声明英文日志与禁控制台）
5. `TaskContract` 已生成，且至少包含目标、允许修改、禁止修改、验证命令、交付证据、owner、超边界处理

若存在 `TBD/待定/未确认`、未决项、或方向未确认，应阻断并回退 `/spec-lite` 补充澄清。

### TaskContract 完整性约束（新增）

下游命令进入主体前，必须确认合同字段完整：

1. `objective`
2. `editablePaths`
3. `forbiddenPaths`
4. `verificationCommands`
5. `deliverables`
6. `evidence`
7. `owner`
8. `outOfScopeHandling`

任一缺失时返回 `blocked`，并引导回上游规格或合同模板补齐。

### Extend 编排约束

`extend` 命令必须先具备 `specPath + finalTier`，缺失即阻断并回退到 `/spec-lite`。
通过后仅做分流编排，不得跳过分级直接进入实现。

### H 级额外约束

对于 H 级任务，`write-plan`、`execute-plan`、`test-gen`、`unified-test`、`code-review` 必须验证规格中的头脑风暴证据（`brainstormPath`）。
若缺失：直接阻断并引导到 `/brainstorm`。

### Research 约束

`research` 命令应优先读取 `spec/Me2AI/需求描述.md` 与 `spec/Me2AI/技术约束.md`。若两者均缺失，阻断并引导先补充需求输入。

### Testcase 约束

`testcase` 命令必须具备：

1. `spec=<path>` 与 `plan=<path>`
2. `spec/AI2AI/Design.md`
3. `spec/AI2AI/Architecture_Info.md`
4. `spec/AI2AI/Protocol_and_Data.md`

任一缺失应阻断并给出下一条补齐命令。

### Test 约束（新增）

`test-gen` 与 `unified-test` 在进入执行前，应确认至少已定义：

1. 覆盖目标
2. 主路径
3. 边界条件
4. 验证命令

若 spec / plan / contract 中缺少上述信息，应阻断并回退到测试合同补齐。

### Bugfix 约束（新增）

`fix-bug` 命令进入修改前，必须具备：

1. 问题描述
2. 复现步骤或最小复现条件
3. 期望行为 / 实际行为
4. 允许修改范围
5. 验证命令或复现关闭证据要求

若上述信息不能从问题单或用户描述中提取，应先生成 bugfix contract 并阻断执行。

### Issue Draft PR 约束（新增）

`issue-draft-pr` 命令进入主体前，必须具备：

1. 工单链接
2. 目标 / 非目标
3. 验收标准
4. PR 需要包含的说明
5. owner / handoff 负责人

若工单目标或验收不清，应先阻断并回退到补 acceptance criteria 或 `/spec-lite`。

### Parallel Delivery 约束（新增）

`parallel-delivery` 命令进入主体前，必须具备：

1. 已批准的 `plan`
2. 子任务拆分
3. 每个子任务的允许修改目录
4. 每个子任务的验证命令
5. 最终收口 owner

若子任务共享核心文件或依赖关系未拆清，应阻断并回退到 `/write-plan`。

### Featureflow 入口约束（新增）

`Featureflow` 是路由入口，不直接承担深层实现；进入主体前必须先完成：

1. 任务类型识别
2. 推荐命令决策
3. 缺失前置项清单
4. 下一步动作说明

若无法判断任务类型，应先阻断并要求补充目标、边界或输入材料。

### Code Self Check 约束

`code-self-check` 命令必须能确定版本控制类型：

1. `vcs=git` 或仓库存在 `.git`
2. `vcs=svn` 或仓库存在 `.svn`

若无法确定版本控制类型，应阻断并提示补充 `vcs` 参数或初始化仓库。

## 模板

- `templates/blocked-report.md`
- `templates/pass-report.md`

## 质量门禁脚本

- `scripts/check-quality.ps1`
- `scripts/check-quality.sh`

用于发布前质量闸口检查，默认校验：
1. 测试通过率阈值（默认 100%）
2. 覆盖率阈值（默认 80%）
3. 文档同步状态（doc-sync 报告 + findings/progress 文件）
4. 可选校验 `spec/AI2AI` 关键文档（`RequireAi2AiDocs=true`）

## 禁止事项

1. 不要把门禁当作“提醒”，一旦阻断就必须停止主体执行
2. 不要返回 `blocked` 却不给下一条可执行命令
3. 不要在缺少 `command` 语义的情况下乱套门禁
4. 不要把质量闸口和普通前置门禁混为一谈
5. 不要在 H 级任务缺少 `brainstormPath` 时继续放行
