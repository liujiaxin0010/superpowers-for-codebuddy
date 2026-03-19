# 硬门禁矩阵

| 命令 | L 级要求 | M/H 级要求 | 阻断后推荐命令 |
|---|---|---|---|
| `/write-plan` | 存在有效 spec-lite，且“需求澄清结论+方案方向确认+日志策略+TaskContract”已填写 | spec 完整且风险/验收非空，方向已确认，无 `TBD/待定/未确认` 与未决项，合同字段完整，日志规范已明确；H 级还需 `brainstormPath` | `/spec-lite ...` |
| `/execute-plan` | 存在计划，且合同中包含验证与证据要求 | 计划 + 门禁通过记录 + 风险缓解条目 + owner/handoff 定义 | `/write-plan ...` |
| `/test-gen` | 目标路径合法，且已定义覆盖目标、主路径、边界条件 | 必须同时关联 `spec` 与 `plan`，且合同中存在验证命令与证据字段 | `/execute-plan ...` |
| `/unified-test` | 目标路径合法，且已定义覆盖目标、主路径、边界条件 | 必须同时关联 `spec` 与 `plan`，且合同中存在验证命令与证据字段 | `/execute-plan ...` |
| `/code-review` | 可选，但若执行必须先输出问题清单、风险声明与证据完整性（默认只读，不直接修复） | M/H 必需，且应关联 `spec/plan` 与 owner/handoff 信息；修复需 Boss 明确确认后进入执行命令 | `/code-review ...` |
| `/fix-bug` | 需明确问题描述、复现条件、期望/实际行为、允许修改范围 | 额外要求最小修复边界、回归命令、剩余风险声明 | `/fix-bug ...` |
| `/issue-draft-pr` | 需明确工单链接、目标/非目标、验收标准、PR 说明、owner | 建议关联 `spec/plan`，并提供 review 证据与 handoff 信息 | `/spec-lite ...` |
| `/parallel-delivery` | 需具备已批准计划、子任务拆分、文件边界、验证命令、owner | Git 项目建议 worktree；必须提供合流验证与统一收口方案 | `/write-plan ...` |
| `/Featureflow` | 需先识别任务类型并给出推荐命令 | 必须输出缺失前置与下一步动作，不得跳过路由直接乱执行 | `/Featureflow ...` |
| `/extend` | 必须关联 spec-lite 与 finalTier | 必须关联完整 spec-lite（含风险/验收）与 finalTier；H 级需有 brainstorm 证据 | `/spec-lite ...` |
| `/brainstorm` | 允许执行 | H 级必须走完整流程 | `/brainstorm ...` |
| `/status` | 展示任务类型、门禁、证据、owner | 额外展示 handoff / merge owner / 剩余风险 | `/status` |
| `/research` | 允许执行；若有 Me2AI 文档则优先读取 | 建议关联 `spec` 与 `tier` 并回填 `researchPath` | `/research ...` |
| `/testcase` | 需要 `target`、`spec`、`plan` | 必须具备 `Design + Architecture_Info + Protocol_and_Data` | `/execute-plan ...` |
| `/code-self-check` | 需可确定 VCS（git/svn）并生成 diff | 可选自动修复时必须保留修复证据 | `/code-self-check ...` |
| `/score-interaction` | 需提供对话内容（文本/文件路径/当前上下文） | 建议关联 `task` 描述以确定评分基线；输出 MD + XLSX 报告 | `/score-interaction ...` |
