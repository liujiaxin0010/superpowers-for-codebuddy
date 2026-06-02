---
name: walkthrough
description: 串讲（设计对齐）技能。在方案设计后、编码前主持两层串讲——概要设计串讲对齐架构方向与模块边界，详细设计串讲锁定接口契约、数据流与联调风险，产出串讲纪要喂入实施计划。用户提到"串讲/设计对齐/架构对齐/接口契约对齐/概要设计评审/详细设计评审/编码前对齐/walkthrough"时触发。
---

# 串讲（Walkthrough / 设计对齐）

本技能回答的是：**在 AI 编码之前，怎样把人的架构意图与跨模块接口契约对齐到位，避免方向偏了再返工。**

## 核心心智：AI 开发模式下，串讲是「人对质量影响最大的窗口」

1. **人不再逐行读代码** → 设计阶段是人对质量影响最大的窗口，后面基本靠流程兜底。
2. **AI 不会主动对齐跨模块认知** → 串讲确保人的意图在编码前就达成一致。
3. **方向偏了代价极大** → 方案先建好，后面才可控。

**串讲不是 AI 自问自答**——必须有 Boss 对每个议题的确认结论，未决项落 `pending-decisions`。

## 两层串讲

| | 概要设计串讲 | 详细设计串讲 |
|---|---|---|
| 时机 | 方案设计后（`/spec-lite`/`/brainstorm` 之后，`/write-plan` 之前）| 详细设计后、编码前（`/write-plan` 之后，`/execute-plan` 之前）|
| 关注点 | 架构对不对、模块切得合不合理 | 接口调得通不通、数据流对不对 |
| 核心产出 | 架构共识 + 模块边界确认 | 接口契约锁定 + 联调风险消除 |
| 解决的问题 | 「方向不能偏」 | 「细节不能错」 |

议题清单与主持流程见 `references/two-layer-walkthrough.md`。

## 资源加载规则

- 判断该走哪层、要过哪些议题时，读 `references/two-layer-walkthrough.md`
- 产出纪要时，读 `templates/walkthrough-minutes.md`

## 何时使用

1. H 级 / 复杂任务在 `/write-plan` 前做概要串讲（强制，见门禁）
2. 涉及多模块协作、跨前后端接口的任务在 `/execute-plan` 前做详细串讲
3. 架构方向或模块边界存在分歧，需要显式对齐

## 何时不用

1. L 级单文件改动、无跨模块交互——开销大于收益，跳过
2. 纯 bug 修复 / 纯重构（行为不变）——走对应工作流
3. 没有 spec——先 `/spec-lite`，无设计输入无从串讲

## 阻断条件

1. 无有效 spec（概要串讲）或无实施计划草案（详细串讲）——阻断并回退上游
2. 议题存在 Boss 未确认的关键分歧 且 ≥2 项——落 `pending-decisions` 后阻断 `/write-plan` 或 `/execute-plan`

## 产出物

串讲纪要 `docs/specs/{date}-{slug}-walkthrough.md`（committed），回填到 spec-lite 的追踪字段 `walkthroughPath` / `detailWalkthroughPath`。

## 与门禁 / 路由衔接

- H 级 `/write-plan` 前置：spec 必须具备 `walkthroughPath`（概要串讲纪要）；缺失则 `BLOCKED` 回退 `/walkthrough layer=概要`
- 多模块 / 跨端任务 `/execute-plan` 前置（建议）：`detailWalkthroughPath`（详细串讲纪要）
- 路由主链：`/brainstorm -> /spec-lite -> /walkthrough(概要) -> /write-plan -> /walkthrough(详细) -> /execute-plan`

## 禁止事项

1. 不要用 AI 自问自答冒充对齐——没有 Boss 确认结论的「串讲」是无效的，方向风险照旧
2. 不要把实现细节塞进概要串讲——概要层只对齐方向与边界，细节留给详细串讲
3. 不要在有 ≥2 项关键分歧未决时硬推下游——未决项必须落 `pending-decisions`
4. 不要跳过纪要 committed 直接进编码——口头结论会丢，违反唯一事实来源
