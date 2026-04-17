# 命令门禁细则

本文件只在 `gate-matrix.md` 的单行信息不足以判断放行条件时读取。

## `/write-plan`

进入前必须确认：

1. spec 中已有需求澄清结论、方案方向确认、日志策略
2. `TaskContract` 已生成且字段完整
3. 不存在 `TBD/待定/未确认`

H 级额外要求：

1. 必须存在 `brainstormPath`

## `/execute-plan`

进入前必须确认：

1. plan 已批准
2. 合同中有验证与证据要求
3. 高风险动作具备回滚或 dry-run 保护

## `/research`

优先检查：

1. `spec/Me2AI/需求描述.md`
2. `spec/Me2AI/技术约束.md`

若两者均缺失，应阻断并要求先补需求输入。

## `/testcase`

必须具备：

1. `spec=<path>` 与 `plan=<path>`
2. `Design.md`
3. `Architecture_Info.md`
4. `Protocol_and_Data.md`

## `/test-gen` 与 `/unified-test`

至少确认：

1. 覆盖目标
2. 主路径
3. 边界条件
4. 验证命令

H 级 / 复杂扩展任务额外要求：

1. 必须存在由 `/requirement-coverage` 输出的通过态报告
   （`docs/quality/requirement-coverage-report.md`，审查结论=通过）
2. 报告生成时间晚于最近一次实现代码提交
3. 若报告不通过或缺失 → 阻断，回退到 `/requirement-coverage`

## `/requirement-coverage`

必须具备：

1. 需求分析文档（`docs/plans/*-需求预分析.md` 或 `docs/specs/*-requirement-analysis.md`）
2. 覆盖矩阵（spec 或 plan 中的"需求覆盖矩阵"章节）
3. 可定位到实现位置的代码
4. 可执行的验证用例 / 命令
5. 独立审查视角（不得由实现者本人在同一会话内自审自验）

## `/extend`

进入主体前必须确认：

1. 已按 `project-reading.md` 的"三层文档→GitNexus→手动"优先级完成项目理解
2. 已生成 `historical-spec.md` 且 Boss 核实通过
3. 已生成 `requirement-analysis.md` 且包含追溯矩阵、Boss 核实通过
4. 已明确 `finalTier` 并写入规格

## `/fix-bug`

进入修改前必须具备：

1. 问题描述
2. 复现步骤或最小复现条件
3. 期望行为 / 实际行为
4. 允许修改范围
5. 验证命令或关闭证据要求

## `/issue-draft-pr`

必须具备：

1. 工单链接
2. 目标 / 非目标
3. 验收标准
4. PR 需要包含的说明
5. owner / handoff

## `/parallel-delivery`

必须具备：

1. 已批准的 plan
2. 子任务拆分
3. 每个子任务的允许修改目录
4. 每个子任务的验证命令
5. 最终收口 owner

## `/Featureflow`

它是路由入口，不直接承担深层实现。进入主体前必须先完成：

1. 任务类型识别
2. 推荐命令决策
3. 缺失前置项清单
4. 下一步动作说明

## `/code-self-check`

必须能确定版本控制类型：

1. `vcs=git` 或存在 `.git`
2. `vcs=svn` 或存在 `.svn`

## 统一高风险规则

以下情况默认不要放行：

1. 共享契约改动未覆盖
2. H 级缺少 brainstorm 证据
3. owner / handoff 缺失
4. 验证命令缺失
