---
name: spec-backfill
description: 自动规格回填技能。用于把代码变更反向同步到 spec/ 设计文档，三层保障——即时回填（编码后）、每日回填（扫 24h 提交）、每周回填（全量重写+增量）；遵循三段式写作与回填红线，落实 Merge-Back。维护 spec/ 设计文档（README/核心流程/接口/配置），不是 CONTEXT.md（那是 doc-sync）。用户提到"规格回填/spec 同步/spec-sync/spec 与代码同步/spec 活文档/Merge-Back"时触发。
---

# 自动规格回填（Spec Backfill）

本技能回答的是：**代码变了之后，怎样把 spec/ 设计文档同步更新，让它始终是代码的实时快照，而不是腐化的历史版本。**

## 核心心智

1. **Spec 是活文档**：不是「写完就完」的一次性产物，需与代码持续同步。
2. **三层保障**：即时回填（编码中）+ 每日回填（Task#1）+ 每周回填（Task#25），层层兜底。
3. **三段式写作**：概述 → Mermaid 流程图 → 功能与设计要点；文档是「理解系统的地图」而非「代码的镜像」。
4. **回填红线**：不复述代码逻辑、不罗列完整 API 字段、不留过时信息。
5. **Merge-Back**：开发期临时规格（对话结论 / `spec/AI2AI/`）验证后回填至 `spec/` 主文档，升级为官方规格。

## 与 doc-sync 的分工

| | `doc-sync`（已有）| `spec-backfill`（本技能）|
|---|---|---|
| 对象 | `CONTEXT.md`（代码自文档，L0/L1/L2）| `spec/` 设计文档（README/核心流程/接口/配置）|
| 视角 | 代码结构的镜像（文件/调用关系）| 业务设计的地图（是什么/为什么）|
| 触发 | `/doc-sync` | `/spec-sync` + 定时 Task#1/#25 |

两者互补，不重叠：`doc-sync` 不改 spec/，`spec-backfill` 不改 CONTEXT.md/源码。

## 资源加载规则

- 判断走哪层回填、各层做什么时，读 `references/three-layer.md`
- 写回填内容时，读 `references/three-paragraph-style.md`（三段式）+ `references/redlines.md`（红线 + 自检）
- 涉及 spec/ 目录结构时，配合 `spec-organization`

## 何时使用

1. 编码完成后即时同步核心流程 / 接口定义（`/execute-plan` 内嵌 hook）
2. 每日扫 24h 提交补充/更新 spec（Task#1）
3. 每周全量审视 spec 与代码一致性（Task#25）
4. 把临时规格 Merge-Back 到 spec/ 主文档

## 何时不用

1. 同步代码自文档 CONTEXT.md → 用 `/doc-sync`
2. 纯内部重构（不影响设计语义）→ 通常不回填
3. 项目无 spec/ 结构 → 先 `spec-organization` 建立

## 三层保障简表

| 层 | 触发 | 范围 | 落点 |
|---|---|---|---|
| 即时 | `/execute-plan` 每次生成代码后 | 核心流程 + 接口定义 | hook（见 executing-plans）|
| 每日 | Task#1（01:00）| 扫 24h 提交，feat→补充/fix→更新行为 | `/spec-sync mode=daily` |
| 每周 | Task#25（周一）| 全量：README 重写 + 模块增量 + 自检 | `/spec-sync mode=weekly` |

详见 `references/three-layer.md`。所有回填经 MR 流程提交，CI 通过后合并（由 `scheduled-automation` 编排）。

## 禁止事项

1. 不要复述代码——文档是地图不是镜像；读者要看代码就引导他去看代码（红线）
2. 不要保留过时信息——代码已删的，删除旧描述而非保留「历史版本」
3. 不要把实现细节写进 spec——条件分支/错误处理细节/完整字段不写
4. 不要改 CONTEXT.md 或源码——那不是本技能职责
5. 不要跳过 Merge-Back——临时规格不回填即「文档私藏」（SSoT 错误）
