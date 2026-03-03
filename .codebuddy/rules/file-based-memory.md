---
alwaysApply: true
---

# 文件记忆（File-Based Memory）

复杂任务的持久化记忆策略。

## 强制启用条件

满足任一条件即启用：

- 多步骤任务（>=3）
- 跨文件修改
- 预计工具调用次数 >5
- 研究/排查类任务

## 强制引导硬门禁

执行前必须确保：

- `docs/findings.md`
- `docs/progress.md`
- `docs/specs/`

若缺失，先按模板创建。
若引导失败，停止并返回 `BLOCKED`。

## 持久化文档更新策略

- `docs/findings.md`：每 2 次搜索/读取后更新
- `docs/progress.md`：每个阶段与每次错误后更新

## 违规处理

若出现流程违规（缺少引导、未记录错误、未先读后决策），
先修复流程状态，再继续实现。
