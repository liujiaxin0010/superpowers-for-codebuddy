# 硬门禁矩阵

| 命令 | L 级要求 | M/H 级要求 | 阻断后推荐命令 |
|---|---|---|---|
| `/write-plan` | 存在有效 spec-lite，且“需求澄清结论+方案方向确认+日志策略”已填写 | spec 完整且风险/验收非空，方向已确认，无 `TBD/待定/未确认` 与未决项，日志规范已明确 | `/spec-lite ...` |
| `/execute-plan` | 存在计划且包含测试任务 | 计划 + 门禁通过记录 + 风险缓解条目 | `/write-plan ...` |
| `/test-gen` | 目标路径合法 | 必须同时关联 `spec` 与 `plan` | `/execute-plan ...` |
| `/unified-test` | 目标路径合法 | 必须同时关联 `spec` 与 `plan` | `/execute-plan ...` |
| `/code-review` | 可选 | M/H 必需，且应关联 `spec/plan` | `/code-review ...` |
| `/extend` | 必须关联 spec-lite 与 finalTier | 必须关联完整 spec-lite（含风险/验收）与 finalTier；H 级需有 brainstorm 证据 | `/spec-lite ...` |
| `/brainstorm` | 允许执行 | H 级必须走完整流程 | `/brainstorm ...` |
| `/status` | 仅展示状态 | 仅展示状态 | `/status` |
