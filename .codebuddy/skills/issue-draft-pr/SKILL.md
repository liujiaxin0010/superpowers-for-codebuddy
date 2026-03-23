---
name: issue-draft-pr
description: 以 issue 或 Jira 工单为起点，生成可审查的 draft PR 交付链路。适用于目标相对清晰、验收可定义、需要异步交接和 owner 收口的任务。用户提到"issue 转 PR/工单到 PR/draft PR/从 issue 开始开发/Jira 工单实现/工单交付"时触发。
---

# 工单到 Draft PR

把 issue / Jira 输入收敛成可执行合同、规格、计划、证据和 draft PR 说明。

## 资源加载规则

当工单质量判断需要参考标准证据格式、或准备输出最终 draft PR 描述时，再读取：

- `references/draft-pr-checklist.md`

当工单只有标题或描述模糊、需要帮助 owner 补齐 acceptance criteria 时，不要加载证据清单——先完成需求补齐。

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

## 工单质量快速判断

| 信号 | 判断 | 动作 |
|---|---|---|
| 有明确 acceptance criteria | 可直接进入合同 | 继续 |
| 有目标但无验收标准 | 需补充 | 先与 owner 确认验收条件 |
| 只有标题或一句话描述 | 不可执行 | BLOCKED，要求 owner 补齐 |
| 包含设计稿/原型链接 | 验收可视化 | 将视觉验收纳入证据 |

## Draft PR 最小质量标准

PR 描述必须包含：

1. **工单映射**：哪些 acceptance criteria 被满足，逐条对应
2. **验证证据**：测试输出、截图或命令结果，不是"已测试"
3. **未覆盖项**：明确声明哪些验收条件本次未实现
4. **风险声明**：已知风险和缓解措施
5. **Handoff**：reviewer 应重点关注什么

## 禁止事项

1. 不要在工单不清晰时就开始写代码——模糊需求产出的代码大概率需要全部返工，浪费的上下文和时间不可回收
2. 不要把 draft PR 当成最终 PR——draft 意味着仍需 review，直接合并会绕过质量门禁
3. 不要在 PR 描述中写"已完成所有功能"却不给逐条证据——无证据的声明无法被 reviewer 验证，等同于未测试
4. 不要跳过 `/code-review` 直接标记为 ready for review——未审查的代码可能包含安全漏洞或架构问题，合并后修复成本成倍增加
5. 不要在 review 阶段补需求或改方向——review 的目的是验证实现质量，方向变更应回退到 spec 阶段
6. 不要把工单的所有 label/tag 当作需求——label 是分类标签不是验收标准，以 acceptance criteria 为准

## 参考

- Draft PR 证据清单：`references/draft-pr-checklist.md`
