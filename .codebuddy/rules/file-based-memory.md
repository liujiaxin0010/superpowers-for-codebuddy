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
- `/extend` 特殊要求：每次执行结束（`BLOCKED`/门禁阻断/分流通过）必须更新 `docs/progress.md`
- `/extend` 特殊要求：若形成新的分流判断、风险结论或阻断经验，必须同步更新 `docs/findings.md`

## 违规处理

若出现流程违规（缺少引导、未记录错误、未先读后决策），
先修复流程状态，再继续实现。
