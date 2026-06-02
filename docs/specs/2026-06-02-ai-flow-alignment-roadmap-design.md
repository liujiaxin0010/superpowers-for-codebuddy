# AI 原生开发流程对齐路线图设计（Phase A–D）

- 状态: **已实现**（Phase A–D + CE 14.8.2 适配全部落地，2026-06-02；见文末「实施记录」）
- 创建日期: 2026-06-02
- 作者: Boss + Claude
- 分支: `claude/gitlab-ci-gate`
- 依据: `D:/CODE/zip2base/流程文档/`（《AI 原生项目开发最佳实践》9 阶段方法论 + 2 个横切系统）

## 1. 背景与目标

`流程文档/` 定义了一套 **9 阶段 AI 原生开发流程** 与 **2 个横切系统**。当前 `superpowers-for-codebuddy`（46 skills / 10 agents / 35 commands / 11 rules）已覆盖大部分阶段，但存在结构性缺口。本分支刚完成 CI **强门禁**（`gitlab-bridge` + `ci-integration` + `/ci-setup`）——这是方法论 `08-CI-CD.md` 的**前半章**；后半章「定时自动化交付」及其驱动的「缺陷闭环 / 增量审查 / 规格回填」尚未落地。

**目标**：把方法论里尚未实现的能力，按依赖顺序补齐为可移植的 skill / command / template，使引擎对齐完整的 AI 原生流程。本文是 **全量路线图设计**，实现按 Phase 分批推进（每 Phase 落地前可再出细化实施 spec）。

**非目标**：不改动已覆盖良好的编码（并行/Worktree/TDD）与测试验证（unified-test/system-test）主链路；不重写 `docs/*` 主流程事实源。

## 2. 缺口分析（方法论 → 当前实现）

| 流程阶段 | 当前实现 | 缺口 | 归属 Phase |
|---|---|---|---|
| 需求分析 | `/requirement-review`、`requirement-coverage-check`、`brainstorming` | 分层功能清单模板、三级评审、结构合规检查 | D |
| 方案设计 | `brainstorming`、`spec-lite`、`research`、`openapi-creator` | 双层 Spec、设计文档编写模板（README三级/技术选型/核心流程/数据库设计/配置） | B |
| **串讲** | **无** | 概要+详细两层串讲，对齐架构方向/模块边界/接口契约 | **B（高优）** |
| 测试用例设计 | `testcase`、`custom-testing` | 8 维度强制、五维加权评审评分、实现状态标注、用例↔代码双向映射 | D |
| 编码实现 | `executing-plans`、`parallel-delivery`、`using-git-worktrees`、TDD 规则 | 覆盖良好 ✅ | — |
| 代码审查 | `code-review-standards`、`web/cpp-qt`、`receiving/requesting-review` | 增量审查 + Baseline Commit 锚点、Block 化、审查立方、Critical→Issue 闭环 | **A** |
| 测试验证 | `unified-test`、`system-test`、`verification-before-completion` | 覆盖良好 ✅（L2 集成分层略弱） | D（增强） |
| CI/CD | `ci-integration`/`gitlab-bridge`/`/ci-setup`（5-stage MR 硬门禁） | 定时自动化体系（7 任务）、CI 7 原则编码化、e2e/deploy 阶段 | **A + D** |
| 缺陷管理 | `bug-fix`、`systematic-debugging`、`issue-draft-pr` | 生命周期闭环、`bugfix:*` 标签状态机、`.clawbench`↔GitLab Issue 双向同步 | **A** |
| spec 组织规范 | `spec-lite`、`code-documentation`(CONTEXT.md) | spec/ 三级目录、唯一事实来源、三种 SSoT 错误约束 | B |
| 自动规格回填 | `doc-sync`（仅 CONTEXT.md，非 spec/） | 三层保障（即时/每日/每周）、Merge-Back、三段式回填 | C |

> 关键区分：现有 `code-documentation`/`doc-sync` 维护的是 **CONTEXT.md（代码自文档，L0/L1/L2）**；方法论的 **spec/（设计文档）** 是另一套体系。两者不冲突，Phase B/C 补的是后者。

## 3. 总体架构与依赖关系

```
Phase A 交付自动化闭环 ──┐ (rides on gitlab-bridge)
  incremental-review ──→ defect-tracking ──→ scheduled-automation
                                                    │ 驱动
Phase B 设计阶段补强 ──┐                            │
  walkthrough(串讲)   │ (独立, 无 GitLab 依赖)      │
  spec-organization ──→ design-doc-templates       │
        │                                           │
        ▼                                           ▼
Phase C 规格活文档 ── spec-backfill (依赖 B 的 spec/ 结构 + A 的定时框架)

Phase D 精细化 ── requirement-spec / testcase++ / ci-principles (增强, 大多独立)
```

- **A 与 B 互相独立**，可并行启动。A 直接延续本分支（gitlab-bridge）；B 是设计阶段，无外部依赖。
- **C 依赖 B（spec/ 结构先存在）+ A（定时任务框架）**。
- **D 为增强项**，大多独立，`ci-principles` 依赖现有 `ci-integration`。
- 推荐落地顺序：**A → B → C → D**（或 A/B 并行 → C → D）。

---

## 4. Phase A — 交付自动化闭环

方法论 `08-CI-CD.md` 后半章 + `11-缺陷跟踪.md` + `06-代码审查.md` 增量部分。三组件咬合成环：**审查发现 → 缺陷闭环修复 → 定时任务编排**，全部经 `gitlab-bridge`。

### 4.1 `code-review` 增量化升级（incremental-review）

扩展现有 review 家族（不新建并列技能，避免割裂）：

| 能力 | 设计 | 落点 |
|---|---|---|
| 增量/全量模式 | 增量（默认）基于 Baseline Commit 的 `git diff`；全量（首次/周日）枚举源文件 | `code-review-standards` 新增 `references/incremental-mode.md` |
| Baseline Commit 锚点 | 报告末尾记录 `Baseline Commit`，下次据此算 diff；丢失则退化全量 | `.clawbench/reviews/{date}/report.md` |
| 流程追踪 | 从变更文件沿 import/调用链纳入上下游（可跨前后端） | review 执行协议 |
| Block 化 | 按数据流分组、每 Block ≤500 行、按 P0-P3 排序、超时截断（P0 不截断） | review 执行协议 |
| 审查立方 | 流程×模块×关注点 = 3×3×4 = 36 项交叉 | `references/review-cube.md` |
| Critical→Issue 闭环 | Critical 项同时写 `.clawbench/issues/ISS-{nnn}.md`（含 status/severity/dimension/files/History） | 新建 `.clawbench/` 产物规范 |
| 疑似解决检查 | 检查 open Issue 涉及文件是否已变更，标 `Suspected Resolved` | review 执行协议 |

产物目录（新约定，加入 `.gitnexusignore`）：
```
.clawbench/
├── reviews/{date}/{plan.md, block-01.md, ..., report.md}
└── issues/ISS-{nnn}.md
```

### 4.2 `defect-tracking` 缺陷生命周期闭环【新增 skill】

承接 `bug-fix`（单次修复方法论）+ `gitlab-bridge`（Issue API）+ `using-git-worktrees`（隔离），补全 **发现→分类→修复→验证→关闭** 全闭环。

- **标签状态机**：`bug → bugfix:in-progress → bugfix:awaiting-review → 关闭`；分支 `bugfix:needs-design / failed / needs-verification`。
- **双向同步**：`.clawbench/issues/ISS-{nnn}.md`（审查内部追踪）↔ GitLab Issue（外部可观测），History 互相记录编号。
- **Worktree 隔离修复**：`.worktrees/bugfix-{iid}` + `fix/issue-{iid}`，每次只修 1 个，最小化变更，必带回归测试。
- **放弃标准**：>5 文件 / 跨层架构 / 核心流程重构 / 方案不确定 / 信息不足 → 打 `bugfix:needs-design`。
- **验证矩阵**：后端→测试全绿；前端→浏览器自动化；无法验证→`bugfix:needs-verification` 不关 Issue。
- 新增命令 `/defect-loop`（扫描+分类+择一修复+MR+清理）；`/fix-bug` 仍是手动单次入口，`/defect-loop` 是自动批量入口。

### 4.3 `scheduled-automation` 定时自动化体系【新增 skill】

把方法论的 **7 个 Codebuddy 定时任务** 落成可执行 runbook + 接入命令。引擎平台无关：`/schedule-setup` 把任务接到 CodeBuddy 原生定时能力或 cron 调 `codebuddy` CLI。每个任务都走 **MR 流程**（不直推 main）、**轮询 CI**（最多 40 次×30s）、**失败自修复**（最多 3 次）、**auto-merge**。

| 任务 | 时间 | 动作 | 复用 |
|---|---|---|---|
| Task #1 文档补充 | 01:00 | 扫 24h 提交 → 回填 spec/CONTEXT | Phase C `spec-backfill` |
| Task #3 夜间发布 | 02:00 | semver 定版 → Release Notes → tag → release 流水线 | `release-and-rollback` |
| Task #4 每日审查 | 03:00 | 增量审查（周日全量）→ 报告 + Issue | §4.1 incremental-review |
| Task #9 Issue 清理 | 05:00 | 扫 `.clawbench/issues/` → 修 Critical（≤3）| §4.2 defect-tracking |
| Task #10 GitLab Issue 修复 | 08:00+20:00 | 扫 GitLab Issue → 分类 → 修 1 个 | §4.2 defect-tracking |
| Task #17 MR 审查合并 | 每小时 | open MR → CI 通过+审查通过 → 合并 | `gitlab-bridge` + review |
| Task #25 文档周更 | 周一 10:00 | 全量扫描 → README 重写 + 模块增量 | Phase C `spec-backfill` |

### 4.4 `gitlab-bridge` 抽象动作补全

当前 bridge 有 `intake.list/get`、`mr.create/comment/status`、`pipeline.status`、`ci.lint`、`wiki.*`、`metrics.*`。Phase A 需补：

| 新增动作 | 用途 | 预期 MCP 工具 | CE 14.8.2 | 降级 |
|---|---|---|---|---|
| `issue.create` | 创建 GitLab Issue | `create_issue` | available | 写 `docs/backlog/` |
| `issue.update` | 改标签/状态 | `update_issue` | available | 更新本地卡 |
| `issue.note` | Issue 评论 | `create_issue_note` | available | 追加本地卡 |
| `mr.merge` | 合并 MR | `merge_merge_request` | available（需非只读）| 输出人工提示 |

> 写操作放开需先把 `GITLAB_READ_ONLY_MODE=false`，与本分支「初期只读」策略衔接：定时自动化上线前单独评估放开。

### 4.5 Phase A 文件清单

```
.codebuddy/skills/
├── code-review-standards/references/{incremental-mode.md, review-cube.md}   [新增]
├── code-review-standards/references/clawbench-issue-format.md               [新增]
├── defect-tracking/{SKILL.md, references/label-state-machine.md,            [新增]
│                    references/dual-sync.md, templates/fix-report.md}
├── scheduled-automation/{SKILL.md, references/task-playbooks.md,            [新增]
│                         templates/{ci-poll.sh, schedule-config.sample}}
└── gitlab-bridge/references/capability-map.md                              [修改] 补 4 动作
.codebuddy/commands/{defect-loop.md, schedule-setup.md}                      [新增]
.gitnexusignore                                                             [修改] 加 .clawbench/
docs/quality/ 或 README/CODEBUDDY                                           [修改] 命令速查
```

---

## 5. Phase B — 设计阶段补强

方法论 `02-方案设计.md` + `03-串讲.md` + `04-spec文档组织规范.md`。独立于 GitLab。

### 5.1 `walkthrough`（串讲）【新增 skill + `/walkthrough` 命令】高优

方法论称串讲为「人对质量影响最大的窗口」，当前完全缺失。两层：

| | 概要设计串讲 | 详细设计串讲 |
|---|---|---|
| 时机 | 方案设计后（`/spec-lite`/`/brainstorm` 之后）| 详细设计后、编码前（`/write-plan` 之后、`/execute-plan` 之前）|
| 关注点 | 架构方向、模块边界 | 接口契约锁定、数据流、异常处理 |
| 产出 | 架构共识 + 模块边界确认 | 接口契约锁定（参数转换表）+ 联调风险消除 |

- 产出 **串讲纪要**（`docs/specs/*-walkthrough.md`），喂入 `/write-plan` / `/execute-plan`。
- **接入路由与门禁**（见 §8）：H 级 `/write-plan` 增加 `walkthroughPath`（概要）前置；H 级 `/execute-plan` 建议 `detailWalkthroughPath`（详细）。

### 5.2 `spec-organization`【新增 skill + `/spec-check` 命令】

落地 `04-spec文档组织规范.md`：

- **spec/ 三级目录结构**：`spec/{子组件}/{README.md, 技术选型.md, openapi.yaml, 数据库设计.md, 核心流程/, 测试用例/, 配置设计/, 子模块/{子模块名}/README.md...}`。
- **双层 Spec**：高层（概要，面向人，README）＋低层（详细，面向 AI，子模块 README + 核心流程）。
- **Spec 细致度三问**（架构约束/测试指导/无需澄清）+ 各层细致度上限 = Test 覆盖度。
- **唯一事实来源 + 三种 SSoT 错误**（文档私藏/代码即文档/规格分裂）+ Merge-Back（衔接 Phase C）。
- **`/spec-check` 结构合规检查**：必须文件、命名规范（`{业务}流程.md`/`{功能}测试套.md`）、目录层级、跨层错放。
- **关系**：`spec-lite` 仍是轻量入口（flat `docs/specs/`）；当任务升级为组件级时，`spec-organization` 提供「毕业」到完整 spec/ 结构的路径。

### 5.3 设计文档编写模板【新增 templates，挂 `spec-organization`】

| 模板 | 要点 | 备注 |
|---|---|---|
| README 三级 | 概述/功能清单/架构图/模块或类划分；实现状态标签（✅本期/🚧开发中/📋规划中）；负责/不负责双表 | 子系统/子组件/子模块 |
| 技术选型.md | 候选对比矩阵 + 量化数据 + 选择依据 + 变更历史 + 技术债双轨 | — |
| 核心流程文档 | 流程图 + 时序图双图 + 文字说明 + 异常分级（L1/L2/L3）；命名 `{业务}流程.md` | — |
| 数据库设计.md | DDL + 字段说明 + 示例值 三位一体 + Mermaid ER 图 + 数据生命周期 | — |
| 配置设计 | `配置说明.md` 逐项 + `config.yaml` 可直接用样例 + 最佳实践/FAQ | — |
| OpenAPI | 已有 `openapi-creator` ✅ | 复用 |

- **Mermaid 规范**：flowchart/sequenceDiagram/graph；配色（人主导黄 `#fff3cd`/AI 核心红 `#f8d7da`/自动化灰 `#d6d8db`/完成绿 `#d4edda`）；折线连线。

### 5.4 Phase B 文件清单

```
.codebuddy/skills/
├── walkthrough/{SKILL.md, references/two-layer-walkthrough.md,             [新增]
│               templates/walkthrough-minutes.md}
├── spec-organization/{SKILL.md, references/{ssot-principles.md,            [新增]
│                      structure-spec.md, mermaid-conventions.md},
│                      templates/{readme-l1.md, readme-l2.md, readme-l3.md,
│                      tech-selection.md, core-flow.md, db-design.md, config-design.md}}
.codebuddy/commands/{walkthrough.md, spec-check.md}                          [新增]
.codebuddy/skills/process-gatekeeper/references/gate-matrix.md               [修改] 加 walkthrough 行
.codebuddy/skills/devflow-router/SKILL.md + references/routing-matrix.md     [修改] 插入串讲节点
```

---

## 6. Phase C — 规格活文档回填（spec-backfill）

方法论 `02-方案设计.md` §自动规格回填 + `04` §Merge-Back。把 `doc-sync` 从 CONTEXT.md 扩展到 spec/。**依赖 B（spec/ 结构）+ A（定时框架）**。

### 6.1 三层保障【新增 skill + `/spec-sync` 命令】

| 层 | 触发 | 范围 | 落点 |
|---|---|---|---|
| 即时回填 | `/execute-plan` 每次生成代码后 | 核心流程 + 接口定义 | hook 进 `executing-plans` |
| 每日回填 | scheduled Task #1（01:00）| 扫 24h 提交，feat→补充/fix→更新行为 | §4.3 |
| 每周回填 | scheduled Task #25（周一）| 全量：README 重写 + 模块增量 + 自检 | §4.3 |

- **三段式写作**：概述（1-2 段）→ Mermaid 流程图（5-8 节点/图）→ 功能与设计要点（是什么/有什么用/为什么）。
- **回填红线**：不写实现逻辑/条件分支/完整 API 字段/前端 props/完整 schema；不复述代码；不留过时信息。
- **Merge-Back**：开发期临时规格（如 `spec/AI2AI/`）验证后回填至 `spec/` 主文档，升级为官方规格。
- **自检清单**：流程图可渲染 / 功能完整 / 术语一致 / 无实现细节泄漏 / 交叉引用有效 / 无过时信息。

### 6.2 Phase C 文件清单

```
.codebuddy/skills/spec-backfill/{SKILL.md, references/{three-layer.md,       [新增]
│                                three-paragraph-style.md, redlines.md}}
.codebuddy/commands/spec-sync.md                                            [新增]
.codebuddy/skills/executing-plans/SKILL.md                                  [修改] 即时回填 hook
.codebuddy/skills/scheduled-automation/references/task-playbooks.md          [修改] Task#1/#25 接 spec-backfill
```

---

## 7. Phase D — 精细化（增强项）

| 子项 | 设计 | 落点 |
|---|---|---|
| 需求分层模板 | 五列功能清单（模块→功能点→描述→依赖→实现状态）+ 边界条件前置声明 + 三级评审（子系统/子组件/子模块）+ 结构合规 | 新增 `requirement-spec` skill 或增强 `requirement-review` |
| 测试 8 维度 | 强制覆盖 功能/性能/安全/可靠/兼容/易用/监控/数据一致；用例 ID 按维度编号（T0xx-T7xx）；实现状态标注；用例↔代码双向映射 | 增强 `testcase` |
| 测试用例评审 | 五维加权评分（功能覆盖25%+流程覆盖20%+脱离实现15%+饱和覆盖25%+引用准确15%）| 增强 `testcase` 或新增 `references/review-scoring.md` |
| CI 7 原则编码化 | 快速失败(lint-first) / 编译执行分离 / 覆盖率分层 / golangci-lint 团队契约 / `-race` 默认 / 防御性 CI(artifact always) / e2e 真实中间件 services；补 lint+e2e+deploy+scheduled-tasks 阶段 | 增强 `ci-integration` templates |
| L2 集成测试分层 | 明确 `tests/integration/` ≥40% 门禁、内存替代品策略 | 增强 `unified-test`/`system-test` |

---

## 8. 门禁矩阵与路由接线（跨 Phase）

`process-gatekeeper/references/gate-matrix.md` 增补：

| 命令 | L 级 | M/H 级 | 阻断后推荐 |
|---|---|---|---|
| `/walkthrough` | 可选；需存在 spec | H 级 `/write-plan` 前必须有概要串讲纪要（`walkthroughPath`）| `/spec-lite` |
| `/spec-check` | 可选 | 组件级 spec/ 必须结构合规才进 `/write-plan` | `/spec-organization` |
| `/spec-sync` | 软性，类 `/doc-sync` | 同 | — |
| `/defect-loop` | 需 gitlab-bridge 可用或本地降级 + 标签体系就绪；每次 1 个；必带回归测试 | 同 + Worktree 隔离 + 验证证据 | `/fix-bug` |
| `/schedule-setup` | 需 bridge 可用 + 写权限评估 | 同 + 每任务 runbook 自洽 | `/ci-setup` |

`devflow-router` 主链路插入串讲（H 级）：
```
/brainstorm -> /spec-lite -> /walkthrough(概要) -> /write-plan
  -> /walkthrough(详细) -> /execute-plan -> /requirement-coverage -> ...
```
`code-review` 默认改为「增量优先，全量兜底」，每次输出末尾记录 Baseline Commit。

## 9. 验证策略（每 Phase 落地时执行）

- **Phase A**：构造含 Critical 的 diff → review 产出 `.clawbench/issues/ISS-001.md` 且报告含 Baseline Commit；模拟 GitLab Issue → `/defect-loop` 走通标签状态机（bridge 不可用时降级到 `docs/backlog/`）；`scheduled-automation` runbook 步骤自洽、引用路径存在；`gitlab-bridge` 4 新动作在 capability-map 标注完整。
- **Phase B**：`/walkthrough` 产出纪要模板渲染正常；`/spec-check` 对合规/不合规 spec/ 目录各跑一次判定正确；6 个设计文档模板 Mermaid 语法可解析、配色符合规范。
- **Phase C**：`/spec-sync` 即时回填只动 spec/ 不动源码；三段式 + 红线在 SKILL.md 定义完整；Task#1/#25 接线正确。
- **Phase D**：CI 模板 YAML 可解析、7 原则各有对应 job/配置；testcase 8 维度模板齐全。
- **通用**：`grep` 确认无 `.lingma`/错误路径引用；README/CODEBUDDY 命令速查与新命令一致；所有新写操作经 `gitlab-bridge`，不绕过门禁直推 main。

## 10. 实施顺序（建议）

1. **Phase A**（延续本分支，最高杠杆）：A.1 incremental-review → A.4 bridge 补动作 → A.2 defect-tracking → A.3 scheduled-automation。
2. **Phase B**（可与 A 并行，独立分支）：B.1 walkthrough（快赢，先做）→ B.2 spec-organization → B.3 设计文档模板。
3. **Phase C**：spec-backfill（需 B 的 spec/ 结构 + A 的定时框架就位）。
4. **Phase D**：按价值穿插，`ci-principles` 与 `testcase++` 优先。

> 每个 Phase 落地前，可按本项目惯例先出该 Phase 的细化实施 spec（`docs/specs/2026-xx-xx-phaseX-*.md`），经 Boss 评审后实现。

## 11. 风险

| 风险 | 缓解 |
|---|---|
| 定时自动化放开 GitLab 写权限的安全风险 | 沿用本分支「初期只读」；写操作（issue/mr.merge）上线前单独评估，最小 scope PAT |
| `.clawbench/` 产物污染仓库 | 加入 `.gitnexusignore`；reviews 可按需 gitignore，issues 保留可追踪 |
| 串讲流于形式（AI 自问自答）| 串讲纪要必须含 Boss 确认结论；H 级门禁强制 `walkthroughPath`，缺失即 BLOCKED |
| spec/ 结构与现有 `docs/specs/` flat 模式并存混乱 | `spec-organization` 明确「轻量(docs/specs) → 组件级(spec/)」毕业路径，不强制小任务用重结构 |
| CodeBuddy 定时能力与方法论假设有出入 | `scheduled-automation` 抽象为 runbook + `/schedule-setup` 适配层，调度器可换（原生/cron）|
| 引擎仓库自身不应放成品产物 | 同 CI 策略：引擎只提供 skill/template/runbook，业务项目运行命令才实例化 |

## 12. 范围外

- 不替 Boss 决定 GitLab 写权限放开时机（出评估清单，Boss 签字）。
- 不在引擎仓库放成品 `.clawbench/`、`spec/{组件}/`、定时任务配置——这些是业务项目运行时产物。
- 不重写已覆盖良好的编码并行/TDD、测试验证主链路。
- 多子系统/团队级并行（多人多服务器）属组织实践，非引擎能力，不实现。

## 13. 实施记录（2026-06-02，全部落地）

| Phase | 新增/修改 | 关键产物 |
|---|---|---|
| A.1 增量审查 | 改 `code-review-standards` | `references/{incremental-mode, review-cube, clawbench-issue-format}.md`（Baseline Commit + Block 化 + 立方 3×3×4 + Critical→ISS 闭环）|
| A.2 bridge 动作 | 改 `gitlab-bridge` | SKILL + `capability-map.md` 补 `issue.create/update/note` + `mr.merge` |
| A.3 缺陷闭环 | 新增 `defect-tracking` + `/defect-loop` | SKILL + `label-state-machine.md` + `dual-sync.md` + `fix-report.md` |
| A.4 定时自动化 | 新增 `scheduled-automation` + `/schedule-setup` | SKILL + `task-playbooks.md`（7 任务）+ `ci-poll.sh` + `schedule-config.sample` |
| B.1 串讲 | 新增 `walkthrough` + `/walkthrough` | SKILL + `two-layer-walkthrough.md` + `walkthrough-minutes.md` |
| B.2 spec 组织 | 新增 `spec-organization` + `/spec-check` | SKILL + `{ssot-principles, structure-spec, mermaid-conventions}.md` + 7 个设计文档模板 |
| C 规格回填 | 新增 `spec-backfill` + `/spec-sync`；改 `executing-plans` | SKILL + `{three-layer, three-paragraph-style, redlines}.md` + 即时回填 hook |
| D 精细化 | 新增 `requirement-spec`；改 `testcase` / `ci-integration` | 需求规格列表模板 + 三级评审；testcase 8 维度 + 五维评分；CI 7 原则 `ci-quality-principles.md` |
| CE 14.8.2 适配 | 新增基线 + 版本矩阵 | `ci-integration/references/ce-14.8.2-cicd-support.md`（安全子集）+ `gitlab-bridge/references/gitlab-version-support.md`（版本能力矩阵 + 未满足清单）|
| 接线 | gate-matrix / router / README / CODEBUDDY / .gitnexusignore | 5 命令门禁行；H 级链插入串讲；命令速查；`.clawbench/` 忽略 |

验证：29 个新 skill 文件 + 5 命令 + 8 references 全部就位；`ci-poll.sh` 通过 `bash -n`；skill frontmatter name 与目录一致；引用路径全部解析；无 `.lingma`/错误路径。

后续（本次未做）：在真实业务项目跑 `/ci-setup` + `/schedule-setup` 端到端验证；放开 `GITLAB_READ_ONLY_MODE=false` 前 Boss 评估；`bridge.probe` 实测修正 `capability-map`。
