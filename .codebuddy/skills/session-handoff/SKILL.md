---
name: session-handoff
description: 会话交接技能。用于在会话结束或上下文断裂时，把任务上下文快照到 `.codebuddy/state/session-handoff.json`，供下次 `/resume` 精准恢复。用户提到"继续上次 / 恢复会话 / 交接 / handoff / resume"时触发。
---

# 会话交接

回答的核心问题：**下一次 AI 进来时，能不能 10 秒内知道"现在在哪、卡在哪、下一步做什么"？**

`docs/progress.md` + `docs/findings.md` 是人类可读的叙述版；本技能提供机器可读、结构化的快照，供 `/resume` 直接消费。

## 触发条件

1. 用户声明"先到这、下次继续"
2. 会话预期跨天 / 跨人
3. 任务被阻断并等待外部输入
4. 上下文濒临压缩边界

## 何时不用

1. 单轮完成的轻任务
2. 仅阅读 / 回答问题的会话

## 阻断条件（BLOCKED）

1. 交接快照缺少 `taskType` / `lastCommand` / `pendingGates` 任一核心字段
2. 宣称"已完成"但 `pendingGates` 仍含 `blocker=true`

## 快照文件

路径：`.codebuddy/state/session-handoff.json`
示例：`.codebuddy/state/session-handoff.json.example`

核心字段：

| 字段 | 含义 |
|---|---|
| `sessionId` | 会话唯一标识（`sess-YYYY-MM-DD-NNN`） |
| `lastUpdatedAt` | 最近一次写入 ISO 时间戳 |
| `branch` | 当前 git 分支 |
| `taskType` | `new-feature` / `bugfix` / `refactor` / `test` / `research` / ... |
| `taskTier` | `L` / `M` / `H` |
| `lastCommand` | 最近一次运行的斜杠命令 |
| `specPath` | 关联 spec 路径 |
| `planPath` | 关联 plan 路径 |
| `pendingGates[]` | 待决门禁清单；每项含 `command` / `reason` / `blocker` |
| `openQuestions[]` | 等待 Boss 或外部输入的问题 |
| `recentEvidence[]` | 最近一次的证据路径 |
| `nextAction` | 下一步动作一句话 |

## 写入时机

1. 会话主动收尾前
2. 任务阻断、等待 Boss 决策时
3. 每个门禁通过 / 不通过后
4. 压缩即将触发前

## 读取时机（/resume）

1. 新会话开启、用户说"继续"时
2. 上下文明显断裂、无法回答"现在在哪"时

`/resume` 必须：

1. 加载快照
2. 校验 `pendingGates` 是否仍成立
3. 自动跳转到 `nextAction` 对应命令
4. 执行前第一步运行 `/status` 展示全貌

## 与现有工具的关系

- `scripts/session-catchup.py`：从聊天缓存中补全上下文；快照存在时优先读快照
- `docs/progress.md`：人类叙述；快照是其"TL;DR 机读版"
- `check-gates.sh`：会检查快照中 `pendingGates` 与实际落盘证据是否一致

## 禁止事项

1. 禁止用快照替代 `progress.md` / `findings.md`（人类可读性仍必需）
2. 禁止写入不同步的 `pendingGates`（"已通过"但报告不存在）
3. 禁止宣称"已完成"却不清理 `pendingGates`
4. 禁止在快照中存放敏感凭据
