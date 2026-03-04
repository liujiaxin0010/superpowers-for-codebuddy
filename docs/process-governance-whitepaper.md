# Superpowers 混合式流程治理技术实现白皮书

## 1. 文档目的

本文档说明本轮流程治理能力的技术实现原理，聚焦以下新增能力：

1. `Spec-Lite` 轻规格入口与 L/M/H 分级
2. `process-gatekeeper` 硬门禁机制
3. `/extend`、`/write-plan` 的“先判档再选流程”
4. 质量门禁脚本（通过率、覆盖率、文档同步）
5. 试运行样例与可追溯产物沉淀
6. `docs` 主产物 + `spec/Me2AI + spec/AI2AI` 兼容层
7. 指南阶段别名命令：`/research`、`/testcase`、`/code-self-check`

本文档面向研发、流程治理维护者、平台工程同学。

## 2. 设计目标与约束

### 2.1 目标

1. 将“探索 -> 收敛 -> 执行”固化为统一可执行流程
2. 将关键前置项从“建议”升级为“阻断”
3. 通过文档产物沉淀实现流程可追踪、可审计
4. 通过脚本化检查减少遗漏和口头约定

### 2.2 非目标

1. 本轮不引入新的代码执行引擎
2. 本轮不做 IDE 深度插件开发
3. 本轮不替换现有 unified-test 内部测试编排器

## 3. 总体架构

实现采用四层结构：

1. 命令层（`.codebuddy/commands/*.md`）：定义入口、参数、前后置步骤
2. 技能层（`.codebuddy/skills/*/SKILL.md`）：定义流程规则、契约与策略
3. 脚本层（`scripts/*.ps1|*.sh`）：执行静态/质量门禁检查
4. 文档层（`docs/*`）：保存规格、质量、试运行和进度证据

### 3.1 核心编排链路

1. 新需求默认先进入 `/spec-lite`
2. 由 `spec-lite` 计算 `recommendedTier` 并得出 `finalTier`
3. 下游命令统一先过 `process-gatekeeper`
4. 阻断时返回 `BLOCKED + nextCommand`，不进入命令主体
5. 通过后按等级分流执行并沉淀文档
6. 收尾前执行质量门禁脚本，失败则阻断完成

## 4. 数据契约设计

### 4.1 GateContext

定义位置：`Spec-Lite` 文档中（`docs/specs/*.md`）。

关键字段：

1. `taskId`
2. `recommendedTier`
3. `finalTier`
4. `overrideReason`
5. `specPath`
6. `planPath`
7. `requiredChecks`
8. `completedChecks`
9. `gateStatus`

作用：

1. 提供任务分级与前置检查上下文
2. 作为后续 `/write-plan`、`/execute-plan`、`/status` 的追踪来源

### 4.2 GateResult

统一门禁返回结构：

1. `status` (`pass|blocked`)
2. `tier`
3. `missing[]`
4. `nextCommand`
5. `message`

作用：

1. 统一阻断语义
2. 统一“下一步可执行命令”引导

## 5. 分级算法与覆盖策略

实现位置：

1. `.codebuddy/skills/spec-lite/SKILL.md`
2. `.codebuddy/commands/spec-lite.md`
3. `.codebuddy/skills/spec-lite/template.md`

### 5.1 评分模型

按多维风险加权打分：

1. 变更文件数
2. 影响模块数
3. 外部契约变化（API/DB/Event/Config）
4. 安全/权限影响
5. 数据/状态迁移
6. 性能关键路径影响
7. 线上故障修复属性

映射规则：

1. `0-2 => L`
2. `3-6 => M`
3. `>=7 => H`

### 5.2 人工覆盖策略

1. 系统先产出 `recommendedTier`
2. 用户可通过 `tierOverride` 覆盖
3. 覆盖必须携带 `overrideReason`
4. 缺理由即 `BLOCKED`

### 5.3 澄清优先策略（新增）

为避免“spec 过粗直接进计划”，`/spec-lite` 新增“通用需求澄清 + 方向确认”门禁：

1. 需求澄清：目标、场景、边界、约束、运维观测
2. 方向发散：AI 产出 2-3 个可行方向（优点/代价/风险）
3. 用户确认：必须有已确认方向，或明确替代方向与硬约束

任一项缺失或为 `TBD/待定/未确认`，直接 `BLOCKED`，不允许进入 `/write-plan`。

### 5.4 日志策略约束（新增）

编码阶段新增全局日志约束：

1. 旧项目必须沿用既有日志结构（框架、字段、级别、traceId）
2. 新项目必须在 brainstorm/spec 阶段确定日志框架与字段规范
3. 日志内容要求英文（message/key）
4. 默认禁用控制台输出，除非用户明确要求

## 6. 硬门禁实现机制

实现位置：

1. `.codebuddy/skills/process-gatekeeper/SKILL.md`
2. `.codebuddy/skills/process-gatekeeper/gate-matrix.md`
3. `.codebuddy/skills/process-gatekeeper/templates/*.md`

### 6.1 门禁语义

1. 门禁是阻断，不是提示
2. 任一必需项缺失立即 `blocked`
3. `blocked` 必须返回 `nextCommand`
4. 命令主体必须停止

### 6.2 命令矩阵

门禁矩阵将每个命令拆成：

1. `L` 级要求
2. `M/H` 级要求
3. 阻断后推荐命令

特性说明：

1. `H` 级需额外验证 `brainstormPath`
2. `/extend` 已从“建议补 spec”升级为“必须先具备 spec/tier”

## 7. “先判档再选流程”落地

### 7.1 /extend

实现点：`.codebuddy/commands/extend.md`

流程变化：

1. 必须解析并校验 `spec` 与 `tier`
2. 缺失即直接 `BLOCKED`，回退 `/spec-lite`
3. 门禁通过后仅做分流，不直接越级进入实现
4. `H` 级必须先走 `/brainstorm` 完整流程

### 7.2 /write-plan

实现点：`.codebuddy/commands/write-plan.md`

流程变化：

1. 缺少 `spec` 或 `tier` 直接阻断
2. spec 的澄清结论或方向确认若存在 `TBD/待定/未确认` 或未决项，直接阻断并回退 `/spec-lite`
3. 若用户否决候选方向但未给替代方向，直接阻断
4. 通过门禁后才允许生成 plan
5. 计划文档必须写入 `specPath/finalTier/gateStatus`

## 8. 质量门禁脚本设计

### 8.1 脚本文件

1. `.codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1`
2. `.codebuddy/skills/process-gatekeeper/scripts/check-quality.sh`

### 8.2 输入与输出

默认输入：

1. `docs/quality/test-summary.json`
2. `docs/quality/doc-sync-report.json`
3. `docs/progress.md`
4. `docs/findings.md`

默认输出：

1. `docs/quality/last-quality-gate.json`

新增可选模式：

1. `RequireAi2AiDocs=true` 时，额外校验 `spec/AI2AI` 关键文档存在性

### 8.3 判定逻辑

1. 测试通过率：
   `passRate` 或 `passed/total`，阈值默认 `100%`
2. 覆盖率：
   `coverage` 或 `coverage.branches/statements`，阈值默认 `80%`
3. 文档同步：
   `status in [pass, ok, synced]` 或 `inSync=true`
4. 文档基础文件存在性：
   `docs/findings.md`、`docs/progress.md`
5. 可选 AI2AI 文档存在性：
   `research.md`、`Design.md`、`test.md`、`plan.md`、`summary.md`、
   `Architecture_Info.md`、`Protocol_and_Data.md`、`testcase.md`、
   `testcase_analysis.md`、`IMPLEMENTATION_PROGRESS.md`、`IMPLEMENTATION_SUMMARY.md`

若任一失败或缺失：

1. 输出 `BLOCKED`
2. 记录 `missing[]` 与 `failed[]`
3. 返回非零退出码

### 8.4 与执行流程集成

`/execute-plan` 已加入质量门禁步骤：

1. 计划执行完成后运行 `check-quality`
2. 质量门禁失败则禁止“宣告完成”
3. 通过后才允许进入收尾

## 9. 静态门禁自检脚本

脚本文件：

1. `.codebuddy/skills/process-gatekeeper/scripts/check-gates.ps1`
2. `.codebuddy/skills/process-gatekeeper/scripts/check-gates.sh`

功能：

1. 检查关键命令是否引用 gatekeeper
2. 检查 `spec-lite/gatekeeper/templates/scripts` 必需文件是否存在
3. 检查指南兼容命令与技能（`research/testcase/code-self-check`）是否接线
4. 当前已纳入 `check-quality.ps1/.sh` 的存在性校验

## 16. 指南兼容层实现（2026-03-04）

本次新增“中等接入”实现，不改变主链路语义：

1. 主事实源：`docs/*` 不变
2. 兼容层：新增 `spec/Me2AI + spec/AI2AI`
3. 别名命令：`/research`、`/testcase`、`/code-self-check`
4. `spec-lite` 追踪链接新增 7 个兼容字段
5. 质量门禁新增可选参数 `RequireAi2AiDocs`，默认关闭，保持历史阈值兼容

定位：

1. 保障“门禁链路自身”不被误删或漏接
2. 不替代业务测试，仅做流程完整性校验

## 10. 状态可观测性

`/status` 增强内容：

1. 读取最新 `GateContext`
2. 展示门禁 `PASS/BLOCKED`
3. 展示等级、缺失项、下一步命令
4. 读取 `docs/quality/last-quality-gate.json` 展示质量门禁状态

效果：

1. 让“流程状态 + 质量状态”在一个命令里可视化

## 11. 试运行机制与结果

试运行目录：

1. `docs/quality/trials/`

本轮已沉淀 3 个真实需求样例：

1. 订单导出能力（M）
2. RBAC 接口收敛（H）
3. 支付状态迁移修复（H）

每个样例包含：

1. `spec-lite` 文档
2. 测试摘要 JSON
3. 文档同步报告 JSON
4. 质量门禁结果 JSON
5. 人类可读 trial 记录

结果：

1. 3/3 质量门禁 `PASS`
2. 通过率均为 `100%`
3. 覆盖率均 `>=80%`
4. 文档同步状态均为 pass/synced/ok

## 12. 与既有能力的兼容性

1. 不改变 `.vue/.go` 的 unified-test 路由策略
2. 保留 `options.goProfile=auto|go_kit|generic_go`
3. 维持覆盖率阈值语义 `80%`
4. 在命令层增量接入，不破坏历史技能结构

## 13. 风险与边界

### 13.1 当前边界

1. 门禁仍基于命令/技能协议驱动，不是编译期强约束
2. `check-quality.sh` 依赖运行环境具备 `bash`
3. JSON 输入格式需要遵守约定字段

### 13.2 风险缓解

1. 通过 `check-gates` 确保关键门禁资产存在
2. 在 README 与技能文档中明确输入模板
3. 将试运行样例作为回归基线

## 14. 后续演进建议

1. 将 `check-quality` 与 CI 流水线绑定（PR 阻断）
2. 增加门禁结果历史趋势（通过率/覆盖率周报）
3. 增加“真实任务 ID -> spec/plan/quality”自动关联索引
4. 对 `/status` 增加最近 N 次质量门禁历史摘要

## 15. 关键文件索引

命令层：

1. `.codebuddy/commands/spec-lite.md`
2. `.codebuddy/commands/extend.md`
3. `.codebuddy/commands/write-plan.md`
4. `.codebuddy/commands/execute-plan.md`
5. `.codebuddy/commands/status.md`
6. `.codebuddy/commands/research.md`
7. `.codebuddy/commands/testcase.md`
8. `.codebuddy/commands/code-self-check.md`

技能层：

1. `.codebuddy/skills/spec-lite/SKILL.md`
2. `.codebuddy/skills/spec-lite/template.md`
3. `.codebuddy/skills/process-gatekeeper/SKILL.md`
4. `.codebuddy/skills/process-gatekeeper/gate-matrix.md`
5. `.codebuddy/skills/executing-plans/SKILL.md`
6. `.codebuddy/skills/research/SKILL.md`
7. `.codebuddy/skills/testcase/SKILL.md`
8. `.codebuddy/skills/code-self-check/SKILL.md`
9. `.codebuddy/rules/logging-conventions.md`

脚本层：

1. `.codebuddy/skills/process-gatekeeper/scripts/check-gates.ps1`
2. `.codebuddy/skills/process-gatekeeper/scripts/check-gates.sh`
3. `.codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1`
4. `.codebuddy/skills/process-gatekeeper/scripts/check-quality.sh`

产物层：

1. `docs/specs/*.md`
2. `docs/quality/*.json`
3. `docs/quality/trials/*`
4. `docs/findings.md`
5. `docs/progress.md`
6. `spec/Me2AI/*`
7. `spec/AI2AI/*`

---

版本：`v1.1`  
更新时间：`2026-03-04`
