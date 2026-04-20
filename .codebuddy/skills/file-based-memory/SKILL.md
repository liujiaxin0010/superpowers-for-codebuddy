---
name: file-based-memory
description: 文件记忆与持久化工作流。用于复杂、多阶段、跨会话任务中维护 `docs/findings.md`、`docs/progress.md` 和规格文档，确保研究结论、阶段状态、错误记录和下一步动作不会丢失。用户提到“继续上次任务/恢复上下文/持久化记录/记到文件里/跨会话接着做”时触发。
---

# 文件记忆

将持久化文档作为多步骤任务的工作记忆，避免上下文漂移、重复排错和阶段状态丢失。

## 何时使用

以下场景必须使用本技能：

1. 任务会跨多个阶段或多轮对话
2. 任务需要研究、计划、执行、回归等持续跟踪
3. 任务中会产生可复用的技术结论、失败模式或决策依据
4. 需要恢复上一次会话的状态

## 强制引导（硬要求）

复杂任务开始时，必须确保以下内容存在：

1. `docs/findings.md`
2. `docs/progress.md`
3. `docs/specs/`

若缺失，先按模板创建后再继续。
若创建失败，返回 `BLOCKED`。

**首次进入复杂任务时，必须读取 `references/memory-protocols.md`**，了解 2次操作规则、三次错误协议等核心更新协议后再开始工作。

## 文档职责边界

### `docs/findings.md`

只记录**可复用的研究发现与技术决策**：

1. 架构结论
2. 风险模式
3. 失败原因与解决方案
4. 可复用的工具、命令、链接、线索

不要把临时 TODO、口头承诺、尚未验证的猜测写进 `findings.md`。

### `docs/progress.md`

只记录**当前任务状态与下一步动作**：

1. 当前阶段
2. 已执行操作
3. 创建/修改的文件
4. 测试结果
5. 错误日志
6. 下一步计划

不要把长期知识沉淀写进 `progress.md`。

## 模板加载规则

### 新任务初始化时

若文件不存在，按以下模板创建：

1. `templates/findings.md` → `docs/findings.md`
2. `templates/progress.md` → `docs/progress.md`

**此时必须读取模板文件本身**，不要凭记忆手写一个“差不多的版本”。

### 已存在文档时

先读现有内容，再继续追加；不要覆盖历史记录。

### 不要怎么加载

1. 不要在文件已存在时重新套用模板覆盖历史内容
2. 不要为“图省事”只创建空文件不填模板结构

## 会话恢复

当用户要求“继续上次任务”或上下文明显断裂时，优先运行：

```bash
# Linux/macOS
python3 .codebuddy/skills/file-based-memory/scripts/session-catchup.py "$(pwd)"

# PowerShell
python .codebuddy/skills/file-based-memory/scripts/session-catchup.py (Get-Location)
```

该脚本用于检查最近会话中是否存在**尚未同步到持久化文件**的上下文。

仅在以下场景运行：

1. 用户明确说“继续上次任务”
2. 当前会话明显缺少前文上下文

若当前会话本身就是连续推进，不要多余运行恢复脚本。

## 完整性检查

在准备交接、收尾或阶段切换前，可使用：

```bash
# Linux/macOS
sh .codebuddy/skills/file-based-memory/scripts/check-complete.sh

# PowerShell
.codebuddy/skills/file-based-memory/scripts/check-complete.ps1
```

用途：

1. 检查 `findings/progress/specs` 是否齐备
2. 检查当前任务是否存在明显未记录项

仅在以下场景运行：

1. 准备 handoff
2. 准备收尾
3. 准备切换阶段

## 结构契约校验（新增）

`progress.md` 与 `findings.md` 不再只依赖"名字叫对"，必须满足 JSON Schema 描述的段落清单：

- `schemas/progress.schema.json`
- `schemas/findings.schema.json`

运行校验：

```bash
bash .codebuddy/skills/file-based-memory/scripts/lint-memory.sh
```

- 退出码 0：通过
- 退出码 1：结构缺段落 → 必须按模板补齐
- 退出码 2：文件缺失 → BLOCKED，先创建

接入位置：

1. `/status` 会显式提示"记忆 lint 是否通过"
2. `check-gates.sh` 默认调用一次，失败即 BLOCKED
3. 阶段切换 / handoff 前必须手动跑一次

## 核心规则

详细规则和 findings/progress 边界说明见 `references/memory-protocols.md`。

1. **2 次操作规则**：每完成约 2 次重要搜索/阅读/决策后，更新一次持久化文档
2. **先读后决策**：继续任务前，先读 `progress` 和相关 `findings`
3. **三次错误协议**：同类失败达到 3 次，必须把失败模式写入 `findings`
4. **失败不重复**：已排除的方案必须记录，防止下轮重复尝试
5. **五问重启测试**：当上下文混乱时，用 `progress.md` 重新回答”现在在哪、做了什么、下一步是什么”

## 推荐更新时机

### 更新 `findings.md`

1. 做出技术决策后
2. 发现高价值约束后
3. 总结出稳定失败模式后
4. 收集到关键资源链接后

不要把“下一步做什么”写进 `findings.md`，那属于 `progress.md`。

### 更新 `progress.md`

1. 阶段切换时
2. 跑完关键验证后
3. 遇到阻断时
4. 准备 handoff 或结束会话时

不要把长期可复用结论写进 `progress.md`，那属于 `findings.md`。

## 标准路径

- `docs/specs/`
- `docs/plans/`
- `docs/findings.md`
- `docs/progress.md`

## 禁止事项

1. 不要在跨会话任务中只依赖聊天上下文，不落盘
2. 不要把未经验证的猜测写成研究结论
3. 不要把同一条信息同时写进 `findings` 和 `progress`
4. 不要创建空文档后长期不更新
5. 不要在继续任务前跳过对已有文档的阅读
