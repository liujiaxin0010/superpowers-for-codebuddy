---
name: devflow-router
description: devflow-ai 总控路由技能。用于把任意开发请求统一收口到一个入口，自动识别任务类型、判断前置条件，并路由到 spec-lite、fix-bug、research、test、review、issue-draft-pr 或 parallel-delivery 等工作流。
---

# devflow-ai 总控路由

把分散的工作流封装成一个统一入口。

## 何时使用

- 用户希望只有一个入口命令
- 其他项目导入后不想记忆多条命令
- 需要先判断任务类型，再决定走哪条工作流
- 需要在缺少 spec / plan / contract 时自动回退到正确前置步骤

## 路由目标

1. `new-feature` -> `/spec-lite`
2. `bugfix` -> `/fix-bug`
3. `refactor` -> `/write-plan`
4. `test` -> `/test-gen` 或 `/unified-test`
5. `research` -> `/research`
6. `review-pr` -> `/code-review`
7. `issue-draft-pr` -> `/issue-draft-pr`
8. `parallel-delivery` -> `/parallel-delivery`

## 模糊需求分级规则（新增）

如果用户给的是**模糊需求**，即使还没有判到 H 级，也应优先评估是否先走 `/brainstorm`，而不是直接进入 `/spec-lite` 或实现链路。

### 分级

#### `must-brainstorm`

满足任意一条即可归为 **必须先 brainstorm**：

1. 只有目标，没有范围边界
2. 只有一句“帮我做这个/加这个”，没有用户、场景、入口或验收标准
3. 明显存在多个实现方向，但用户尚未选方向
4. 需求可能跨模块，但没有说明影响范围
5. 需求包含“优化一下/改造一下/升级一下”这类宽泛表述，且未定义行为边界

#### `should-brainstorm`

满足任意一条即可归为 **建议先 brainstorm**：

1. 已有明确目标，但验收标准仍然偏粗
2. 已知大致范围，但用户/场景/入口不完整
3. 看起来主要影响单模块，但仍存在明显边界条件未定义
4. 已有倾向方案，但仍缺少用户确认

### 处理方式

#### 对 `must-brainstorm`

1. 先输出 `RouteDecision`
2. 将 `ambiguityLevel` 设为 `must-brainstorm`
3. 将 `recommendedCommand` 设为 `/brainstorm`
4. 在 `why` 中明确说明：因为需求边界不清，先做需求澄清与方案发散
5. 不直接进入实现，不替用户猜范围

#### 对 `should-brainstorm`

1. 先输出 `RouteDecision`
2. 将 `ambiguityLevel` 设为 `should-brainstorm`
3. 默认仍推荐 `/brainstorm`
4. 若用户坚持走快速收敛链路，且最小字段已具备，可回退到 `/spec-lite`
5. 在 `why` 中明确说明：先 brainstorm 风险更低，但可在边界足够时直接收敛

## 决策顺序

1. 先判断用户目标是什么，而不是先猜命令
2. 再判断需求模糊等级：`must-brainstorm | should-brainstorm | clear`
3. 若为 `must-brainstorm`，直接优先 `/brainstorm`
4. 若为 `should-brainstorm`，默认推荐 `/brainstorm`，必要时可退到 `/spec-lite`
5. 再识别是否已有 `spec / plan / target / issueLink / owner`
6. 优先选择最短但不越界的链路
7. 缺少前置条件时，不硬推进，直接回退到正确上游步骤

## 输出格式

至少输出：

```text
RouteDecision:
- taskType:
- ambiguityLevel:
- recommendedCommand:
- why:
- missingPrerequisites:
- nextAction:
```

## 参考

- 路由映射：`references/routing-matrix.md`
- 导入清单：`references/import-bundle.md`
