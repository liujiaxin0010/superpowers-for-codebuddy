---
name: issue-draft-pr
description: 以 issue 或 Jira 工单为起点，生成可审查的 draft PR 交付链路。适用于目标相对清晰、验收可定义、需要异步交接和 owner 收口的任务。
---

# 工单到 Draft PR

把 issue / Jira 输入收敛成可执行合同、规格、计划、证据和 draft PR 说明。

## 何时使用

- 任务已经存在于 GitHub issue 或 Jira 中
- 可以清楚写出目标、非目标和验收标准
- 允许 agent 异步推进，但不直接合并

## 必备输入

1. 工单链接
2. 目标
3. 非目标
4. 验收标准
5. PR 说明要求
6. owner / handoff 负责人

## 执行流程

1. 先校验工单是否真的写清目标与验收
2. 若未写清，先补 acceptance criteria，不进入实现
3. 使用 `task-contracts` 生成 `issue-draft-pr` 合同
4. 若缺少 spec，回退 `/spec-lite`
5. 若缺少 plan，回退 `/write-plan`
6. 若 `spec + plan` 齐备，进入 `/execute-plan`
7. 收尾前必须执行 `/code-review`
8. 输出 draft PR 草稿，至少包含：
   - 工单目标映射
   - 验收证据
   - 风险声明
   - owner / handoff

## 阻断条件

- 工单没有清晰目标
- 工单没有清晰验收标准
- 合同缺少 owner
- 试图直接把 review 阶段当成补需求阶段

## 参考

- Draft PR 证据清单：`references/draft-pr-checklist.md`
