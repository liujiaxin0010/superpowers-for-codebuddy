# Bug 修复上库 commit message 模板

适用：根据缺陷单 / 特性单（AC 工单号）修复代码后的上库提交。

## 格式

```
[AI-H] AC<工单号>: <一句话修改说明>

Bug Id: AC<工单号>
Description: <缺陷单原始标题/描述，原文照搬>
Root Cause: <根本原因>
Solution: <修复方案>
Impact: <影响的模块/文件；有无行为变化>
Verification: <如何验证；自测结论>
Risk: <剩余风险，无则填 none>
```

- **AI 标签（首位，必填且只能一个）**：`[AI-0]` 纯手写 / `[AI-H]` 人机协作 / `[AI-100]` 全 AI 生成。
  团队服务端 hook 与 CI `verify:commit-msg` 都强制此标签；缺失或出现多个一律阻断。bug 修复通常是 `[AI-H]`。
- **首行（subject）**：`[AI-x] AC<工单号>: <修改说明>`。AI 标签 + 空格 + `AC` + 数字工单号 + `: ` + 简短说明。
  此行会被 CI `verify:commit-msg` 校验（见 `ci-integration` 技能），格式不符流水线阻断。
- **空行**：subject 与 body 之间必须空一行。
- **body**：以下字段逐行填写。

## 字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `Bug Id` | 是 | 缺陷单号（AC 号），与首行一致，便于工单系统反查 |
| `Description` | 是 | 缺陷单原始标题/描述，**原文照搬不改写**——保证与工单系统可追溯 |
| `Root Cause` | 是 | 根本原因，不是表象。说清「为什么会有这个 bug」，而非「哪里报错」 |
| `Solution` | 是 | 修复方案概述：改了什么、为什么这样改 |
| `Impact` | 是 | 影响的模块/文件范围；是否有行为变化、兼容性影响 |
| `Verification` | 是 | 如何验证：原复现步骤是否不再触发；执行的自测、回归测试及结论 |
| `Risk` | 是 | 剩余风险点；确无风险填 `none` |

> `Root Cause / Impact / Verification / Risk` 把「上库 log」从一条记录升级为**可审计的修复证据**，
> 与 `systematic-debugging`（先根因后修复）、`task-contracts`（验证证据）一致。

## 示例

### 简短改动

```
[AI-H] AC44753: 修改productTitle从'智能通行一体机'为'智慧通行一体机'

Bug Id: AC44753
Description: 【特性单】productTitle 文案错误，应为"智慧通行一体机"
Root Cause: 初版配置文案沿用了旧产品名，未随产品更名同步
Solution: 更新配置项 productTitle 的默认值
Impact: 基础配置模块；仅文案展示变化，无逻辑影响
Verification: 配置页确认标题显示为"智慧通行一体机"；回归基础配置页无异常
Risk: none
```

### 一般缺陷

```
[AI-H] AC38906: 修复基础配置页在 U20 分销场景下条件性崩溃

Bug Id: AC38906
Description: 【特性单】【基础配置-基本配置 严重 有条件必然重现】U20分销合入主线提单跟踪
Root Cause: 分销模式下 configList 可能为空，遍历前未做空值判断
Solution: 在遍历 configList 前增加空值与长度校验，空集合走默认分支
Impact: 基础配置-基本配置模块；非分销场景行为不变
Verification: 按工单复现步骤在 U20 分销环境验证不再崩溃；回归非分销场景正常
Risk: none
```

## 与 commit-msg-lint 的关系

CI `verify:commit-msg` 校验分两层，与团队服务端 AI 标签 hook 对齐：

1. **AI 标签**（必填，恰好一个，作为 subject 前缀）：`[AI-0]` 纯手写 / `[AI-H]` 人机协作 / `[AI-100]` 全 AI 生成。
   缺失、出现多个（如 `[AI-0] x [AI-H] y`）都会阻断。
2. **标签后的格式**默认接受两类首行：
   - 工单号格式：`AC<数字>: <说明>`（本模板）
   - Conventional 格式：`<type>: <说明>`（如 `fix:` / `feat:`）

bug 修复上库统一用工单号格式（即 `[AI-H] AC<数字>: <说明>`）。如团队工单前缀非 `AC`，按 `commit-msg-lint` 脚本注释调整 `TICKET_PATTERN`。
