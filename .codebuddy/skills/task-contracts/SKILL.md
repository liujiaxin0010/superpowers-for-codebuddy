---
name: task-contracts
description: 统一任务合同技能。用于根据任务类型选择合同模板，补齐目标、边界、验证、证据、owner 与超边界处理，并将模板压缩成 agent 可执行合同摘要。
---

# 任务合同（Task Contracts）

把任务从“聊天描述”收敛成“可执行合同”。

## 何时使用

- 需要把需求压缩成稳定输入时
- 需要在 spec / plan / execute / review 之间共享同一套边界时
- 需要明确可编辑位置、验证命令、交付证据与 owner 时
- 任何使用 `.codebuddy/templates/task-contracts/*.md` 的场景

## 合同最小字段

必须至少包含：

1. `任务目标`
2. `范围边界`
3. `允许修改`
4. `禁止修改`
5. `验证命令`
6. `交付物`
7. `交付证据`
8. `人工确认点`
9. `owner`
10. `超边界时如何处理`

## 执行流程

1. 先识别任务类型
2. 选择对应模板
3. 补齐最小字段
4. 检查是否存在 `TBD/待定/未确认`
5. 将模板压缩为 agent 合同摘要：
   - objective
   - editablePaths
   - forbiddenPaths
   - verificationCommands
   - deliverables
   - evidence
   - humanCheckpoints
   - owner
   - outOfScopeHandling
6. 若缺少关键字段，则阻断并回退上游规格或人工确认

## 模板与任务类型映射

- `new-feature` -> `../../templates/task-contracts/new-feature.md`
- `bugfix` -> `../../templates/task-contracts/bugfix.md`
- `refactor` -> `../../templates/task-contracts/refactor.md`
- `test` -> `../../templates/task-contracts/test.md`
- `research` -> `../../templates/task-contracts/research.md`
- `review-pr` -> `../../templates/task-contracts/review-pr.md`
- `issue-draft-pr` -> `../../templates/task-contracts/issue-draft-pr.md`
- `parallel-delivery` -> `../../templates/task-contracts/parallel-delivery.md`

## 参考

- 任务类型选择：`references/task-types.md`
- 合同压缩清单：`references/compression-checklist.md`
