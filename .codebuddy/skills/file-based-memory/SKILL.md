---
description: 带强制文档引导的持久化记忆工作流。
---

# 文件记忆（File-Based Memory）

将持久化文档作为多步骤任务的工作记忆。

## 强制引导（硬要求）

复杂任务开始时，必须确保以下内容存在：

1. `docs/findings.md`
2. `docs/progress.md`
3. `docs/specs/`

若缺失，先按模板创建后再继续。
若创建失败，返回 `BLOCKED`。

## 会话恢复

```bash
# Linux/macOS
python3 .codebuddy/skills/file-based-memory/scripts/session-catchup.py "$(pwd)"

# PowerShell
python .codebuddy/skills/file-based-memory/scripts/session-catchup.py (Get-Location)
```

## 核心规则

1. 2 次操作规则
2. 先读后决策
3. 三次错误协议
4. 失败不重复
5. 五问重启测试

## 标准路径

- `docs/specs/`
- `docs/plans/`
- `docs/findings.md`
- `docs/progress.md`
