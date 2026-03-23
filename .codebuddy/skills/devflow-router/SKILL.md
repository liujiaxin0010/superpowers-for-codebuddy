---
name: devflow-router
description: Featureflow 总控路由技能。用于把任意开发请求统一收口到一个入口，自动识别文档产物意图、任务类型、判断前置条件，并路由到 brainstorm、spec-lite、fix-bug、research、test、review、issue-draft-pr 或 parallel-delivery 等工作流。
---

# Featureflow 总控路由

把分散的工作流封装成一个统一入口。

## 资源加载规则

当需要根据任务类型或前置缺失做正式路由判断时，再读取：

- `references/routing-matrix.md`

当任务本身带有“需求预分析文档 / 需求分析文档 / 按模板输出”这类产物意图，或需求模糊度难以判断时，再读取：

- `references/ambiguity-routing.md`

只有在要把 `Featureflow` 作为单入口导入到其他项目时，才读取：

- `references/import-bundle.md`

当需要输出结构化路由结果时，再读取：

- `templates/route-decision-template.md`

## 何时使用

1. 用户希望只有一个入口命令
2. 其他项目导入后不想记忆多条命令
3. 需要先判断任务类型，再决定走哪条工作流
4. 需要在缺少 spec / plan / contract 时自动回退到正确前置步骤

## 决策协议

1. 先识别用户真正要的产物，而不是先猜命令
2. 再判断任务类型：new-feature / bugfix / refactor / test / research / review-pr / issue-draft-pr / parallel-delivery
3. 再判断模糊度：`must-brainstorm | should-brainstorm | clear`
4. 再检查前置是否齐备：spec / plan / target / issueLink / owner
5. 最后选择最短但不越界的链路

## H 级统一口径

H 级任务有两条都合法的进入路径：

1. 模糊需求或明确要需求预分析文档：
   `/brainstorm -> /spec-lite -> /write-plan`
2. 需求较清晰，但 `/spec-lite` 判定为 `H`：
   `/spec-lite -> /brainstorm spec=<specPath> tier=H -> /write-plan`

共同约束：

1. 进入 `/write-plan` 前，H 级 spec 必须具备 `brainstormPath`
2. 若 `brainstormPath` 缺失，下游必须 `BLOCKED` 并回退 `/brainstorm`

## 输出要求

结构化路由结果至少包含：

1. `taskType`
2. `ambiguityLevel`
3. `recommendedCommand`
4. `why`
5. `missingPrerequisites`
6. `nextAction`

## 何时不用

1. 用户已经明确知道要执行哪条命令（如直接说 `/fix-bug`）——此时无需路由，直接执行目标技能
2. 任务是纯对话问答、知识查询，不涉及任何工作流产物
3. 用户只是要求读取或查看文件内容，没有开发意图
4. 项目中只配置了一条工作流，不存在路由选择空间

## 禁止事项

1. 不要在需求模糊时直接跳到实现链路——模糊需求跳过 brainstorm 会导致方向错误，返工成本远大于多走一步预分析
2. 不要在产物意图明显是需求预分析文档时绕开 `/brainstorm`——绕开会丢失需求发散和风险识别的产物
3. 不要缺前置还硬推命令主体——前置缺失时强行推进，下游会因缺少 spec/plan 而产出质量不可控
4. 不要在路由判断时一次性加载所有 references——路由判断只需 routing-matrix，按需加载才不会稀释上下文
5. 不要把路由结果口头化输出而跳过结构化模板——非结构化输出会遗漏 missingPrerequisites 等关键字段，导致下游误判
6. 不要在用户未提供足够信息时自行猜测 taskType——猜错 taskType 会把整条链路带偏，应先向用户确认
