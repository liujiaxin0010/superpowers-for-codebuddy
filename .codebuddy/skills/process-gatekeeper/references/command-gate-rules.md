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
6. **失败回归测试三件套（硬门禁）**：
   - `failingRegressionTestPath`：测试文件路径
   - `failingRegressionTestCommand`：可以独立执行该测试的命令
   - `failingRegressionTestEvidence`：修复前运行该测试的完整失败输出
   - 证据标准：连续运行 3 次均稳定失败；不依赖本地时间/网络等不可重现状态
7. 合同模板：`.codebuddy/skills/bug-fix/templates/regression-test-contract.md`

缺任一项 → BLOCKED，回 `/fix-bug` 补齐。修复后必须在同一 PR 内提交"测试由红转绿"的对比证据。

例外：线上紧急止血（hotfix）可先合修复，但必须在 24 小时内补交失败测试，并在 `docs/findings.md` 记录延迟理由。

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

## `/security-review`

必须具备：

1. `scope=<paths>` 或已关联 `spec=<path>`/`plan=<path>`
2. 9 个维度（威胁建模 / OWASP / 输入输出 / 鉴权授权 / 加密密钥 / 日志审计 / 依赖审计 / 秘密扫描 / 合规隐私）逐项出具"不涉及 / 涉及但已缓解 / 涉及且有风险"三态判定
3. 依赖审计实际运行（npm audit / pip-audit / govulncheck / cargo audit 等），命令输出附入报告
4. 秘密扫描实际运行（gitleaks 或等价），命令输出附入报告
5. 报告路径：`docs/quality/security-review-report.md` + `docs/quality/security-review-report.xlsx`
6. 🔴 严重问题存在 → BLOCKED，禁止进入 `/unified-test` / `/system-test` / `/release`

未命中任何触发条件时，仅允许 Boss 显式"不涉及"强制通过；自动跳过禁止。

## `/data-safety-check`

进入前必须确认：

1. 命中触发条件清单（见 `.codebuddy/skills/data-safety/SKILL.md#触发条件`）
2. 四件套齐全：
   - 行数 / 作用域预估（只读统计命令 + 实际输出）
   - 备份 / 快照（创建或引用已有，必须附验证证据 / 恢复演练结果）
   - dry-run 证据（实际执行 `BEGIN;...ROLLBACK;` 或 `--dry-run`）
   - 回滚脚本（已存档路径，staging 已演练一次）
3. 执行窗口 / 值守人 / 终止条件齐备
4. Boss 显式签字原文 + 时间戳写入 `docs/progress.md`
5. 未签字 → BLOCKED；禁止以"紧急"名义跳过

计划文档路径：`docs/plans/YYYY-MM-DD-<op-name>-data-safety.md`。

## `/release`

进入前必须确认：

1. spec / plan 已通过 `/requirement-coverage`
2. 若包含数据操作 → 必须引用已签字的 `/data-safety-check` 报告
3. `docs/changelog/<version>.md` 已填写
4. `docs/release/<version>-release-notes.md` 已填写
5. `docs/runbooks/<feature>-rollback.md` 已就绪
6. pre-release checklist 全部勾选
7. 灰度 / 全量策略、观测指标、告警阈值、回滚触发条件显式写入

## `/rollback`

进入前必须确认：

1. 存在 `rollback-playbook`（对应版本/部署）
2. 已记录快照点（commit / tag / 备份标识）与恢复命令
3. Boss 显式签字确认"执行真实回滚"
4. 通知链（运维 / 业务 / 值守人）已触发
5. 回滚完成后必须在 24 小时内提交复盘（写入 `docs/findings.md`）

默认策略：仅允许"回滚准备 + dry-run 演练"，真实回滚非默认动作。

## `/perf-check`

必须具备：

1. 命中触发条件（热路径代码改动 / 批量处理 / 并发模型变化 / DB 查询改动 / 关键接口）
2. 基线：`.codebuddy/state/perf-baseline/<scope>.json`（不存在 → 先建立）
3. 本次结果：同输入、同机型、同负载规格
4. 阈值判定：回归超过 `±thresholdPct` 即 BLOCKED
5. 报告路径：`docs/quality/perf-report-<scope>.md`
6. 证据：命令、输出、采样截图、profiling 文件路径

## `/system-test`

必须具备：

1. `/requirement-coverage` 报告通过
2. 系统测试剧本（`docs/quality/system-test-scenarios.md`），覆盖主路径 + 关键边界
3. 数据准备 / 清理脚本，不得污染生产
4. 证据：命令输出、截图、录屏或日志归档
5. 缺陷分类：按 `defect-classification.json` 输出等级
6. 🔴 严重 / 🟠 高 缺陷存在 → BLOCKED，禁止进入 `/release`

## `/resume`

必须具备：

1. `.codebuddy/state/session-handoff.json` 存在
2. 包含 `taskType`、`lastCommand`、`pendingGates`、`specPath`、`planPath` 等字段
3. 若关联任务已 BLOCKED，显式恢复到对应门禁并提示 Boss
4. 恢复后第一步必须 `/status`，确认门禁与进度一致

## 统一高风险规则

以下情况默认不要放行：

1. 共享契约改动未覆盖
2. H 级缺少 brainstorm 证据
3. owner / handoff 缺失
4. 验证命令缺失
5. 命中数据安全触发条件却未提供已签字的 `/data-safety-check` 报告
6. 命中安全审查触发条件却未提供通过态 `/security-review` 报告
7. 命中性能触发条件却未提供基线对比证据
