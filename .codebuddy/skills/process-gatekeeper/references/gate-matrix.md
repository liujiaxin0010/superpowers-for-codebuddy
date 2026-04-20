# 硬门禁矩阵

| 命令 | L 级要求 | M/H 级要求 | 阻断后推荐命令 |
|---|---|---|---|
| `/write-plan` | 存在有效 spec-lite，且“需求澄清结论+方案方向确认+日志策略+TaskContract”已填写 | spec 完整且风险/验收非空，方向已确认，无 `TBD/待定/未确认` 与未决项，合同字段完整，日志规范已明确；H 级还需 `brainstormPath` | `/spec-lite ...` |
| `/execute-plan` | 存在计划，且合同中包含验证与证据要求 | 计划 + 门禁通过记录 + 风险缓解条目 + owner/handoff 定义 | `/write-plan ...` |
| `/test-gen` | 目标路径合法，且已定义覆盖目标、主路径、边界条件 | 必须同时关联 `spec` 与 `plan`，且合同中存在验证命令与证据字段 | `/execute-plan ...` |
| `/unified-test` | 目标路径合法，且已定义覆盖目标、主路径、边界条件 | 必须同时关联 `spec` 与 `plan`，合同含验证命令与证据；**H 级 / 复杂扩展任务必须先通过 `/requirement-coverage`** | `/execute-plan ...` 或 `/requirement-coverage ...` |
| `/requirement-coverage` | 必须存在需求分析文档（`docs/plans/*-需求预分析.md` 或 `docs/specs/*-requirement-analysis.md`）与覆盖矩阵 | 同时存在已实现代码与可执行验证用例；不允许实现者自审 | `/spec-lite ...` 或 `/brainstorm ...` 或 `/execute-plan ...` |
| `/code-review` | 可选，但若执行必须先输出问题清单、风险声明与证据完整性（默认只读，不直接修复） | M/H 必需，且应关联 `spec/plan` 与 owner/handoff 信息；修复需 Boss 明确确认后进入执行命令 | `/code-review ...` |
| `/fix-bug` | 需明确问题描述、复现条件、期望/实际行为、允许修改范围，且**必须先提交"失败回归测试" (`failingRegressionTestPath` + `failingRegressionTestCommand` + `failingRegressionTestEvidence`)** | 同 L 要求 + 最小修复边界、剩余风险声明、修复后前绿对比证据 | `/fix-bug ...`（补交失败测试） |
| `/issue-draft-pr` | 需明确工单链接、目标/非目标、验收标准、PR 说明、owner | 建议关联 `spec/plan`，并提供 review 证据与 handoff 信息 | `/spec-lite ...` |
| `/parallel-delivery` | 需具备已批准计划、子任务拆分、文件边界、验证命令、owner | Git 项目建议 worktree；必须提供合流验证与统一收口方案 | `/write-plan ...` |
| `/Featureflow` | 需先识别任务类型并给出推荐命令 | 必须输出缺失前置与下一步动作，不得跳过路由直接乱执行 | `/Featureflow ...` |
| `/extend` | 必须先生成并由 Boss 核实 `historical-spec.md`；再生成并由 Boss 核实 `requirement-analysis.md`；关联 finalTier | 同 L 级要求 + 必须关联完整 spec-lite/计划，且通过 `project-reading.md` 三层文档→GitNexus→手动 优先级；H 级需有 brainstorm 证据 | `/spec-lite ...` 或 `/brainstorm ...` |
| `/brainstorm` | 允许执行 | H 级必须走完整流程 | `/brainstorm ...` |
| `/status` | 展示任务类型、门禁、证据、owner | 额外展示 handoff / merge owner / 剩余风险 | `/status` |
| `/research` | 允许执行；若有 Me2AI 文档则优先读取 | 建议关联 `spec` 与 `tier` 并回填 `researchPath` | `/research ...` |
| `/testcase` | 需要 `target`、`spec`、`plan` | 必须具备 `Design + Architecture_Info + Protocol_and_Data` | `/execute-plan ...` |
| `/code-self-check` | 需可确定 VCS（git/svn）并生成 diff | 可选自动修复时必须保留修复证据 | `/code-self-check ...` |
| `/score-interaction` | 需提供对话内容（文本/文件路径/当前上下文） | 建议关联 `task` 描述以确定评分基线；输出 MD + XLSX 报告 | `/score-interaction ...` |
| `/security-review` | 需明确审查范围（scope 或 spec/plan 路径）；触发条件命中时强制执行 | 必须完成 9 维度判定 + 依赖审计命令 + 秘密扫描命令，输出 MD + XLSX；🔴 严重问题存在即阻断 | `/security-review ...` |
| `/data-safety-check` | 任何触发条件（DDL / 批量 DML / rm -rf / kubectl delete / 对象存储批量 / MQ purge / 迁移脚本 / 脱敏回灌）命中即必须执行 | 四件套齐全（行数预估 + 快照 + dry-run + 回滚脚本）+ Boss 显式签字 + 执行窗口/值守人 | `/data-safety-check ...` |
| `/release` | 必须关联已通过的 `spec/plan`，且包含 changelog 条目与预期观测指标 | 同 L + 发布前 checklist、pre-release gate、发布公告、回滚预案已联动 `/rollback` | `/release ...` |
| `/rollback` | 必须存在 `rollback-playbook`，记录最近一次部署与快照点 | 同 L + Boss 显式签字、通知链、RTO/RPO 预估、真实回滚完成后复盘 | `/rollback ...` |
| `/perf-check` | 变更命中性能触发条件（热路径 / 批量处理 / 并发模型变更 / DB 查询）时强制 | 必须提供基线 vs 本次结果、同输入同机型对比、阈值判定、证据路径 | `/perf-check ...` |
| `/system-test` | 必须先通过 `/requirement-coverage`；存在端到端验证脚本或剧本 | 同 L + 系统测试剧本、数据准备/清理脚本、证据录制、缺陷分类表 | `/requirement-coverage ...` 或 `/execute-plan ...` |
| `/resume` | 存在 `.codebuddy/state/session-handoff.json` 且含最近一次任务上下文 | 同 L + 已关联未完成任务合同，门禁状态已校验，未决 BLOCKED 显式提示 | `/resume ...` |
