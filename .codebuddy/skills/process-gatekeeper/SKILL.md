---
name: process-gatekeeper
description: 命令执行前置项的硬性流程门禁。
---

# 流程门禁（Process Gatekeeper）

## 目标

在命令执行前进行前置检查。若检查失败，返回 `BLOCKED` 并立即停止。

## 输入

```yaml
command: "write-plan|execute-plan|test-gen|unified-test|code-review|extend|brainstorm|status|research|testcase|code-self-check"
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

### Spec 完整性约束

进入 `/write-plan` 前，必须确认 spec 中以下内容已明确：

1. 需求澄清结论（目标、场景、边界、约束）
2. 方案方向确认（候选方向 + 用户已确认方向）
3. 用户拒绝记录（若有）与替代方向/硬约束
4. 日志策略（沿用项目日志结构或新项目日志框架选型，且声明英文日志与禁控制台）

若存在 `TBD/待定/未确认`、未决项、或方向未确认，应阻断并回退 `/spec-lite` 补充澄清。

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
