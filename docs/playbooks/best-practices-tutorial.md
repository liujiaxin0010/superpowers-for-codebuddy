# Featureflow 最佳实践教程：新建项目 & 老项目扩展

> 这是一篇**手把手教程**，用三个贯穿场景把 Featureflow 工作流跑通：
> - **场景 A**：从零开发一个**新项目**（greenfield）
> - **场景 B**：在一个**已有老项目**上扩展功能（brownfield，走 `/extend`）
> - **场景 C**：把 A / B 接到**内网 GitLab** 上跑（MCP + CI/CD 强门禁 + 24×7 自动化）
>
> 抽象的命令-合同映射见 [workflow-playbook.md](./workflow-playbook.md)；门禁单行规则见 [gate-matrix.md](../../.codebuddy/skills/process-gatekeeper/references/gate-matrix.md)。本篇只讲「实际怎么一步步操作、会撞到什么、怎么过」。

---

## 0. 先记住 5 个底层概念

这 5 个概念在所有场景里都成立。看不懂下面的实例时，回来对照。

### 0.1 单入口 `/Featureflow`：拿不准就用它

不确定该走哪条命令时，永远先 `/Featureflow <你的需求原话>`。它会先判断任务类型（new-feature / bugfix / refactor / extend …）和需求模糊度，再路由到正确的下游命令。**它不直接写代码，只负责"把你领到正确的起点"。**

知道自己要干什么时，也可以直接用专用入口（`/spec-lite`、`/extend`、`/fix-bug`…）。

### 0.2 tier（L/M/H）决定流程深度

`/spec-lite` 会按下面这张表给任务打分，分数映射到等级，**等级越高、强制门禁越多**：

| 打分项 | 分值 |
|---|---|
| 变更文件数 ≤2 / 3-6 / ≥7 | +0 / +1 / +2 |
| 影响模块数 1 / 2 / ≥3 | +0 / +1 / +2 |
| 外部契约变更（API/DB/Event/Config） | +3 |
| 安全 / 权限域变更 | +3 |
| 数据 / 状态迁移 | +2 |
| 关键路径性能影响 | +1 |
| 线上故障修复 | +1 |

`0-2 → L`，`3-6 → M`，`≥7 → H`。

- **L/M**：轻链路，`spec-lite → write-plan → execute-plan → 测试 → review`。
- **H**：重链路，强制 `brainstorm` + `walkthrough`（设计对齐）+ `requirement-coverage` + `system-test` 等。

> 💡 不确定时**宁可升一级**：把 `clear` 当 `should-brainstorm` 只多花 10 分钟确认；把 `must-brainstorm` 误判成 `clear`，代价是方向错了之后的全量返工。

### 0.3 硬门禁与 `BLOCKED`：撞墙是设计，不是故障

每条命令进入前都有**前置条件**。条件不满足时，AI 会返回 `BLOCKED` 并告诉你回退到哪一步，**绝不允许"为了效率"硬推进**。常见阻断：

- `/write-plan` 前：spec 里还有 `TBD/待定`，或 H 级缺 `brainstormPath` / `walkthroughPath`。
- `/unified-test` 前（H 级 / 复杂扩展）：没先过 `/requirement-coverage`。
- `/extend` 前：`historical-spec.md` 或 `requirement-analysis.md` 没让你（Boss）打勾核实。
- `/fix-bug` 前：没提交"修复前必然失败的回归测试"三件套。

看到 `BLOCKED` 不要催 AI 跳过——按它给的 `nextCommand` 把缺的东西补上即可。

### 0.4 文件即记忆：三个文件必须一直在更新

长任务不靠"AI 记性"，靠文件：

| 文件 | 什么时候写 |
|---|---|
| `docs/progress.md` | 每个阶段、每次出错后 |
| `docs/findings.md` | 每 2 次搜索/读取后；出现新结论/决策时立即 |
| `docs/pending-decisions.md` | **一次回复抛出 ≥ 2 个待决策项时立即落盘**（用 `/pending`） |

阶段切换或交接前，先 `/pending sweep`：还有未决项就视为澄清没完成。

### 0.5 Boss 核实点：这些产物必须你亲自签字

工作流里有几处**必须人工确认**、AI 不能自己拍板放行：

- `/spec-lite` 的需求澄清结论 + 2~3 个方案方向（你选哪个、否决哪个）。
- `/extend` 的 `historical-spec.md`（历史实现规格）和 `requirement-analysis.md`（扩展需求分析）。
- 任何触达生产数据的操作（`/data-safety-check` 四件套）+ 真实 `/release` / `/rollback`。

> ⚠️ **四条铁律贯穿全程**：① 每次回复先称呼 `Boss`；② 拿不准先问，不擅自拍板；③ 未经要求不写兼容代码；④ 动生产数据先有备份+dry-run+回滚脚本并经你签字。

---

## 场景 A：从零开发新项目（greenfield）

### A.1 "新建项目"的特点与起手式

新项目 = **没有任何存量代码可读**。所以：

- **不要先 `/doc-init`**。三层代码自文档、`project-reading.md` 的"先读懂再动手"是给**已有代码**用的；新项目要先把骨架**建出来**。`/doc-init`、`/doc-sync` 留到 A.6 收尾时再用。
- **日志框架要"选型"而不是"沿用"**。`/spec-lite` 会强制你在澄清/头脑风暴阶段定下日志框架 + 结构化字段（英文日志、默认禁控制台）。这条不定，进不了 `/write-plan`。
- 新项目通常**天然是 H 级**：新服务往往一上来就有多模块 + 对外 API 契约 + 鉴权，打分很容易 ≥7。

起手只有一句：

```text
/Featureflow 从零做一个「审批流服务」，给内部系统提供审批单的提交、流转、查询能力，需要登录鉴权
```

### A.2 贯穿实例：从零搭一个「审批流服务」

下面按 H 级重链路逐步走。每步给出**你敲什么**、**AI 大致回什么**、**会撞到的门禁**。

#### Step 1 · `/Featureflow` 路由

AI 判定 `taskType=new-feature`、模糊度 `must-brainstorm`（"做一个服务"目标偏大、多模块、影响面未知），推荐先 `/brainstorm`。

```text
Boss，这是一个新建服务、范围较大的需求，我判定为 must-brainstorm。
建议先做头脑风暴对齐方案，再出规格。下一步：/brainstorm …
```

#### Step 2 · `/brainstorm` 七阶段发散

```text
/brainstorm 审批流服务：提交/流转/查询 + 登录鉴权
```

头脑风暴会逼出关键决策并落到 `docs/plans/2026-06-02-审批流服务-需求预分析.md`：

- 模块切分（auth / approval-core / query / 通知）。
- 鉴权方案（自建 JWT vs 接入已有 SSO）——**这是方向选择，要你拍板**。
- 数据模型（审批单、流转记录、审批人）。
- **日志框架选型**（如 zap / logback，结构化字段 `traceId/module/action/result/durationMs/errorCode`）。

> 抛出 ≥2 个待决策项（鉴权方案、存储选型…）时，AI 会立即写 `docs/pending-decisions.md`，而不是把选项丢在对话里。你逐项回答，它逐项回填。

#### Step 3 · `/spec-lite` 出规格 + 定级

```text
/spec-lite 审批流服务 MVP
```

AI 完成"通用需求澄清"（业务目标、调用方、触发入口、交付形态、数据边界、非功能约束、日志策略）并给 2~3 个实现方向让你确认，然后生成 `docs/specs/2026-06-02-审批流服务-spec-lite.md`。

打分示例：新增文件 ≥7（+2）、模块 ≥3（+2）、新增 API 契约（+3）、鉴权/权限域（+3）= **10 → H**。

```yaml
GateResult:
  status: "pass"
  tier: "H"
  nextCommand: "/brainstorm 审批流服务 MVP spec=docs/specs/2026-06-02-审批流服务-spec-lite.md tier=H"
```

> 若你**先**跑了 `/spec-lite` 才发现是 H，路径也合法：`/spec-lite → /brainstorm spec=… tier=H → …`。只要进 `/write-plan` 前 `brainstormPath` 已回填即可。

#### Step 4 · `/walkthrough`（概要）串讲——堵住"方向偏了再返工"

H 级 spec 进 `/write-plan` 前**必须**有概要串讲纪要（`walkthroughPath`），否则 `BLOCKED`。

```text
/walkthrough layer=概要 spec=docs/specs/2026-06-02-审批流服务-spec-lite.md
```

概要层对齐：整体架构、模块边界、谁依赖谁。关键分歧 ≥2 项未决也会阻断——先在这里吵清楚，比写完代码再推倒便宜得多。

#### Step 5 · `/write-plan` 写实施计划

```text
/write-plan spec=docs/specs/2026-06-02-审批流服务-spec-lite.md tier=H
```

产出 `docs/plans/2026-06-02-审批流服务-plan.md`，按批次拆任务，每个任务带验证命令与证据要求。

> **进入门禁**：spec 无 `TBD`、方向已确认、日志策略已定、`TaskContract` 完整、H 级有 `brainstormPath` + `walkthroughPath`。缺一项就回退。

#### Step 6 · `/walkthrough`（详细）锁接口契约

跨模块任务进 `/execute-plan` 前建议补详细串讲（`detailWalkthroughPath`），把接口签名、数据流、错误码锁死。

```text
/walkthrough layer=详细 spec=… plan=docs/plans/2026-06-02-审批流服务-plan.md
```

#### Step 7 · `/execute-plan` 分批执行

```text
/execute-plan docs/plans/2026-06-02-审批流服务-plan.md spec=… tier=H
```

**每批执行后暂停等你确认**。新项目建议第一批先交付"最小可跑骨架"（能启动 + 一个健康检查接口 + 日志框架接好），后续批次再填业务。每批结束更新 `docs/progress.md`。

#### Step 8 · 需求覆盖 + 测试

H 级先过覆盖审查，再生成/跑测试：

```text
/requirement-coverage spec=… plan=…
/unified-test target=<模块或文件> spec=… plan=… tier=H
```

> **门禁**：H 级 `/unified-test` 前必须有 `/requirement-coverage` 的**通过态**报告，且报告时间晚于最近一次代码提交；否则回退 `/requirement-coverage`。覆盖审查**不允许实现者自审**。

#### Step 9 · 条件门禁（命中才强制）

| 命令 | 触发条件 | 本例是否命中 |
|---|---|---|
| `/security-review` | 外部输入 / 鉴权 / 加密 / 敏感数据 | ✅ 有登录鉴权 → 必跑（9 维度 + 依赖审计 + 秘密扫描；🔴严重即阻断）|
| `/perf-check` | 热路径 / 批量 / 并发 / DB / 关键接口 | 查询接口若是关键路径 → 建立基线 |
| `/system-test` | H 级 / 复杂任务 | ✅ 必跑（端到端剧本，🔴/🟠 缺陷阻断 `/release`）|
| `/data-safety-check` | DDL / 批量 DML / 迁移 | 建库建表脚本命中 → 走四件套 |

#### Step 10 · `/code-review`（默认只读）

```text
/code-review spec=… plan=…
```

先出问题清单 + 风险声明，**未经你确认不直接改代码**。

#### Step 11 · 收尾：建文档 + 发布

新项目此时才补上代码自文档体系，并走发布三件套：

```text
/doc-init                 # 生成项目地图→模块 CONTEXT.md→文件头注释
/release                  # changelog / release-notes / rollback-playbook
/status                   # 收尾：剩余风险、owner、handoff
```

### A.3 新项目链路全貌

```text
/Featureflow → /brainstorm → /spec-lite(H) → /walkthrough(概要) → /write-plan
   → /walkthrough(详细) → /execute-plan → /requirement-coverage
   → /unified-test → /security-review → /perf-check → /system-test
   → /code-review → /doc-init → /release → /status
```

L/M 级新项目（少见，比如纯工具脚本）可省掉 brainstorm/walkthrough/system-test：

```text
/spec-lite → /write-plan → /execute-plan → /unified-test → /code-review → /status
```

### A.4 新项目常见坑

1. **一上来就 `/doc-init`**：没代码可文档化，纯属空转。骨架建出来后再做。
2. **日志策略留 `TBD`**：直接卡在 `/write-plan` 门口。新项目必须在 brainstorm/spec-lite 阶段定死框架 + 字段。
3. **第一批就想交全功能**：先交"最小可跑骨架"，把架构/边界验证对了再铺业务，返工最小。
4. **跳过 walkthrough**：H 级这是硬门禁；省下的 10 分钟会变成写完三个模块后发现边界划错的两天。

---

## 场景 B：在老项目上扩展功能（brownfield，`/extend`）

### B.1 "老项目扩展"为什么必须走 `/extend`

老项目的风险不在"写新代码"，在"**不知道碰了什么旧代码**"。所以扩展的核心问题是：

> 新功能该**接在哪**、要**动哪些地方**、哪些地方**绝不能顺手改**。

`/extend` 强制一套**四步前置**（顺序不可逆、缺一阻断），把"先理解、再沉淀、再发散、再分析"做实，之后才允许进入和新项目一样的 `spec-lite → write-plan → …` 链路。

> ❗ `/extend` 本身**不写实现代码**，只编排前置流程。它的全部价值是"在你动手前，逼出对旧系统的正确认知 + 你的签字确认"。

### B.2 起手式：先把项目读懂（信息源优先级铁律）

任何"分析项目/解释代码"都按这个顺序选源，**禁止跳级**：

```text
三层代码自文档(CONTEXT.md + 文件头 INPUT/OUTPUT/POS)
   → GitNexus(先做模式 G 基线对比/刷新)
   → 手动阅读四步法
```

- 接手一个**还没有 CONTEXT.md** 的老项目？先 `/doc-init` 把三层文档建起来，后续所有扩展都受益。
- 有 GitNexus MCP 时，按"模糊定位→你核实候选→精确分析"三阶段用；基线漂移 `riskLevel=high` 未刷新会阻断。

### B.3 贯穿实例：给已有订单模块加 Excel 导出

```text
/extend requirement=给订单后台列表新增 Excel 导出，按当前筛选条件导出，不影响现有查询与分页
```

#### Step 0.1 · 项目理解（强制）

AI 按优先级读订单模块，**必读** `CONTEXT.md` 的两节并写入 `docs/progress.md`：

- **§⑥ 设计决策与踩坑**：哪些不变量不能破、历史踩过哪些坑。
- **§⑧ 扩展点**：新需求该挂在哪、哪些是"禁止修改的不动区"。

> ⚠️ 如果你的改动**命中 §⑧ 不动区**，必须先向 Boss 申请授权；未授权 → `BLOCKED`。

#### Step 0.2 · 生成历史实现规格（Boss 核实）

把"订单模块现在已经做了什么"**反向沉淀**成 spec：

- 路径：`docs/specs/2026-06-02-order-模块-historical-spec.md`
- 内容：业务目标、用例清单、对外接口、数据模型、关键流程（含 Mermaid）、跨模块依赖、当前缺陷与债务、日志/观测约束、隐含约束。
- **完整提交你核实**。只要还有 `待补充/TBD`，或你没打勾 → `BLOCKED`，进不了下一步。

#### Step 0.3 · `/brainstorm`（带历史规格）

```text
/brainstorm 订单 Excel 导出 historicalSpec=docs/specs/2026-06-02-order-模块-historical-spec.md
```

发散时**必须显式列出**对历史实现的四类决策：

| 决策 | 本例 |
|---|---|
| **复用** | 订单查询 service、现有鉴权、结构化日志框架 |
| **扩展** | 列表页新增导出按钮、新增 `GET /orders/export` |
| **替换** | 无 |
| **废弃** | 无 |

产出 `docs/plans/2026-06-02-订单导出-需求预分析.md`。

#### Step 0.4 · 生成扩展需求分析规格（Boss 核实）

- 路径：`docs/specs/2026-06-02-订单导出-requirement-analysis.md`
- **必须逐条引用** historical-spec 里的受影响项，并包含「**需求 → 设计 → 实现 → 验证**」四列追溯矩阵。
- **完整提交你核实**，未打勾 → `BLOCKED`。

#### Step 1+ · 进入标准链路

四步前置通过后，`/extend` 把 `requirement-analysis.md` 作为输入分流：

```text
/spec-lite 订单 Excel 导出   # 以 requirementAnalysisPath 为输入，定级
```

本例打分：变更文件 3（+1）、影响模块 2（+1）、新增 API 契约（+3）、关键路径性能（+1）= **6 → M**（与仓库里的真实样例 [order-export-spec-lite](../specs/2026-03-02-order-export-spec-lite.md) 一致）。

M 级后续：

```text
/write-plan spec=docs/specs/2026-06-02-订单导出-requirement-analysis.md tier=M
/execute-plan <planPath> spec=… tier=M
/unified-test target=orders/export spec=… plan=…
/code-review …
/status
```

> 若定级为 H，则与场景 A 一样补 `walkthrough` / `requirement-coverage` / `system-test`。命中鉴权/性能/数据条件时，`/security-review`、`/perf-check`、`/data-safety-check` 同样强制。

### B.4 扩展模式选择：加法优先

影响评估必须输出三类结论——**必须新增**的文件、**必须修改**的现有文件、**保持不动**的核心模块——然后按下表选模式：

| 判断条件 | 扩展模式 | 典型操作 | 风险标注 |
|---|---|---|---|
| 与现有功能无数据共享 | 新增独立模块 | 新建目录 + 接口注册 | 低 |
| 复用现有数据但独立展示 | 新增路由/页面 | 新建路由 + 复用现有 service | 低 |
| 是现有功能的变体 | 新增处理器/组件 | 现有模块目录下新增文件 | 低 |
| 必须改现有行为才能实现 | 最小侵入式修改 | 仅改必要接口 | **必须标风险等级** |

原则：**先新增，再接入，最后才考虑最小修改**。只有最后一种需要标风险。

### B.5 老项目扩展链路全貌

```text
[四步前置] 项目理解(三层→GitNexus→手动)
   → historical-spec(Boss✓) → /brainstorm(复用/扩展/替换/废弃) → requirement-analysis(Boss✓)
[标准链路] → /spec-lite → /write-plan → /execute-plan → /requirement-coverage(H)
   → /unified-test → /security-review* → /perf-check* → /system-test(H)
   → /code-review → /release* → /status
                                   (* = 命中条件才强制)
```

### B.6 老项目扩展常见坑

1. **没读懂就动手**：不理解现有结构的扩展等于在暗室砌墙——四步前置就是来堵这个的。
2. **把"扩展"写成大面积侵入式改造**：那是重构，不是扩展。侵入式改动越多，回归风险越大。
3. **改了共享契约还当"小改动"**：共享契约的影响面是**所有消费者**，必须按高风险处理。
4. **新模块依赖旧模块 OK，旧模块反向依赖新模块 = 循环依赖**：禁止。
5. **日志风格各写各的**：新增链路必须沿用旧的结构化日志字段，否则排障时新旧模块关联不上。
6. **跳过回归验证**：新代码没 bug ≠ 旧代码没被影响。每个修改类任务都要保留回归命令。

---

## 场景 A / B 对照速查（接 GitLab 见场景 C）

| 维度 | 场景 A 新建项目 | 场景 B 老项目扩展 |
|---|---|---|
| 入口 | `/Featureflow` → `/brainstorm` / `/spec-lite` | `/extend` |
| 起手第一件事 | **建骨架**（不要先 doc-init） | **读懂旧代码**（三层→GitNexus→手动，必要时先 `/doc-init`） |
| 强制前置 | H 级要 brainstorm + walkthrough | **四步前置**：理解 → historical-spec✓ → brainstorm → requirement-analysis✓ |
| 日志 | **选型**（定框架+字段） | **沿用**现有结构化字段 |
| 典型定级 | H（新服务多模块+契约+鉴权） | L/M 居多（加法式扩展），动核心才 H |
| 最大风险 | 方向/架构偏，靠 walkthrough 堵 | 误伤旧代码/共享契约，靠四步前置 + 不动区 + 回归堵 |
| 文档时机 | 收尾才 `/doc-init` | 扩展前就该有 CONTEXT.md |

---

## 场景 C：结合 GitLab 做项目（MCP + CI/CD 全流程）

前面两个场景是**单机本地**工作流——门禁靠 AI 自觉，AI 可以跳过、没人拦得住。项目托管在**内网 GitLab**（Community Edition 14.8.2）时，可以把软门禁升级成**系统强制的硬阻断**，并让 AI 经 MCP 直接读写 GitLab（拉需求、建 MR、查流水线、合并），最终做到交付阶段 24×7 无人值守。

> 适用人群：项目在内网 GitLab、团队协作、想让"AI 该做的检查"变成"机器拦得住的关卡"。纯本地单人开发可跳过本章。

### C.1 先理解三层关系（一图说清）

GitLab 接入不是新增一条工作流，而是给已有的 A/B 链路**加两层**：

```text
① 本地工作流（场景 A / B）           ——「做什么」
     /Featureflow → /spec-lite → /write-plan → /execute-plan → 测试 → review
     软门禁：process-gatekeeper，靠 AI 自觉
              │  开发完成：git push 分支 + 建 MR
              ▼
② GitLab CI/CD 流水线（5 阶段）       ——「门禁怎么被系统强制」
     gate → build → test → quality → verify
     任一红灯 +「Pipelines must succeed」→ MR 合不了（软门禁 → 硬阻断）
              ▲
              │  AI 读 issue / 建 MR / 查流水线 / 合并 MR
③ gitlab-bridge ↔ MCP server          ——「AI 怎么访问 GitLab」
     @zereight/mcp-gitlab · 探测优先 · 唯一对接层 · 优雅降级 · 初期只读
```

- **第 ②、③ 层是可选增强，不改变 A/B 主线链路。** 本地软门禁照常先过一遍，CI 再强制兜底——同一套门禁的"自觉版"和"强制版"。
- **CE 为什么只能靠流水线**：GitLab Community Edition 缺 EE 的 Push Rules / Approval Rules / 安全 widget。CE 唯一能"阻断合并"的机制是 MR 设置「Pipelines must succeed」。所以**所有想强制的门禁，统统做成 `.gitlab-ci.yml` 里的 job**，一条流水线收口全部强门禁。

### C.2 一次性接入：四步搭好底座

#### Step 1 · 服务器侧：GitLab + Runner（决定要不要 Docker）

- GitLab CE 14.8.2 自带 CI/CD，服务器侧通常无需额外开启。
- **必须有 GitLab Runner**：没 Runner 流水线一直 pending、门禁形同虚设——装并注册一个 Runner 到内网 GitLab。
- 要不要 Docker 取决于 executor：

| executor | 要 Docker? | 代价 | `.gitlab-ci.yml` |
|---|---|---|---|
| `docker`（推荐，模板默认） | ✅ 需要 | Runner 主机装 Docker + 内网 registry 提供 `image:` 基础镜像；e2e 真实中间件（`services:`）只在此模式可用 | 保留 `image:` / `services:` |
| `shell` | ❌ 不需要 | 要在 Runner 主机预装构建/测试工具链 | 删掉 `default: image:` 与 e2e `services:` |

详见 [gitlab-server-setup.md](../../.codebuddy/skills/ci-integration/references/gitlab-server-setup.md)。

#### Step 2 · 部署 GitLab MCP server（AI 访问 GitLab 的通道）

AI 经 [`@zereight/mcp-gitlab`](https://github.com/zereight/gitlab-mcp) 访问 GitLab，**版本锁定 `2.1.12`**（别用 `latest`，版本漂移会变工具集）。能直连 npm 时直接用 `npx`；纯内网无公网时把包发布到内网 npm registry，或自建 Docker 镜像推内网 registry。

在 CodeBuddy 的 MCP 配置（`mcp.json` / 项目级 `.mcp.json`）里加（npx 方式）：

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "npx",
      "args": ["-y", "@zereight/mcp-gitlab@2.1.12"],
      "env": {
        "GITLAB_API_URL": "https://<内网GitLab域名>/api/v4",
        "GITLAB_PERSONAL_ACCESS_TOKEN": "<PAT，scope 只勾 api>",
        "USE_PIPELINE": "true",
        "USE_GITLAB_WIKI": "true",
        "GITLAB_READ_ONLY_MODE": "true"
      }
    }
  }
}
```

- `GITLAB_API_URL` 填到 `/api/v4` 为止；`USE_PIPELINE=true` 是 CI 门禁强依赖；`GITLAB_READ_ONLY_MODE` **初期必须 `true`**，验证后经确认再放开写。
- 纯内网 npm：`env` 里加 `"npm_config_registry": "https://<内网npm registry>"`（或用 `.npmrc`）。Docker / SSE 方式见 [mcp-setup.md](../../.codebuddy/skills/gitlab-bridge/references/mcp-setup.md)。

部署后先用最基础端点验证 GitLab 可达（不经 MCP）：

```bash
curl --header "PRIVATE-TOKEN: <PAT>" "https://<内网GitLab域名>/api/v4/version"
# 预期返回 {"version":"14.8.2",...}
```

完整步骤与排障见 [mcp-setup.md](../../.codebuddy/skills/gitlab-bridge/references/mcp-setup.md)。

#### Step 3 · `/ci-setup` 生成流水线与门禁产物

```text
/ci-setup
```

AI 会**探测技术栈**（`pom.xml`→Maven、`go.mod`→Go、`package.json`→Node、`CMakeLists.txt`→CMake、`*.pro`→qmake…），一次问清参数（executor、内网镜像地址、主分支名、`BUILD_COMMAND`、`TEST_COMMAND`、是否强制 commit 工单号），然后从模板实例化产出：

| 产物 | 作用 |
|---|---|
| `.gitlab-ci.yml` | 5 阶段门禁流水线（替换全部 `<PLACEHOLDER>`）|
| `.gitlab/merge_request_templates/featureflow.md` | MR 模板（含门禁 checklist）|
| `scripts/commit-msg-lint.sh`（及 `.ps1`）| commit 规范校验（替代 CE 缺失的 Push Rules）|
| `docs/gitlab-setup-checklist.md` | GitLab 项目设置清单，交 Maintainer 人工执行 |

> ⚠️ `/ci-setup` **只生成文件，不替你改 GitLab 项目设置**——AI 无此能力。且不要在引擎仓库（superpowers-for-codebuddy）自身跑它，引擎只提供模板。

#### Step 4 · Maintainer 配 GitLab 设置 + 测试 MR 验证

按 `docs/gitlab-setup-checklist.md` 在 GitLab 项目里配置（**这步决定门禁是否真的拦得住**）：

- **Settings → Merge requests → 勾「Pipelines must succeed」**（没这一项，流水线红了照样能合，门禁白做）。
- **Protected Branches**：主分支限「Allowed to merge: Maintainers」（替代 CE 缺失的 Approval Rules）。
- 推一个测试 MR，确认 5 阶段流水线触发、且任一 job 红时 MR 被阻断。

### C.3 MCP 怎么在工作流里用（gitlab-bridge）

**所有 GitLab 交互只经 `gitlab-bridge` 的抽象动作，其他命令不直接调 MCP 工具**——这样换平台只改一个文件，核心工作流零改动。

- **探测优先**：任何动作前必须先 `bridge.probe`，列出 MCP server 实际暴露的工具，给每个动作打 `available / degraded / unavailable`。不探测就调用 = 拿不确定的工具集赌运行时。
- **优雅降级**：MCP 不可达时全部动作回退本地 `docs/` 文件模式（降级是设计的一部分，不是故障）。

常用抽象动作：

| 抽象动作 | 用途 | 降级行为 |
|---|---|---|
| `intake.list` / `intake.get` | 从 GitLab Issue 拉需求 | 读本地 `docs/backlog/` |
| `mr.create` / `mr.comment` | 建 MR / 贴评论 | 输出人工创建提示 |
| `mr.status` / `mr.merge` | 查 MR 状态 / 合并 | 读本地门禁产物 / 人工合并 |
| `pipeline.status` | 查流水线 / job 状态 | 读 `docs/quality/last-quality-gate.json` |
| `ci.lint` | 校验 `.gitlab-ci.yml` 语法 | 跳过，提示人工校验 |
| `issue.create/update/note` | 缺陷收录 / 改标签 / 评论 | 写本地缺陷卡 |
| `wiki.read/write` | 团队知识库读写 | 读写本地 `docs/knowledge/` |

> 🔒 **安全**：初期 `GITLAB_READ_ONLY_MODE=true`，只跑探测与只读动作；写动作（`mr.create`/`mr.merge`/`issue.*`/`wiki.write`）放开前必须经你确认。PAT 只用最小 `api` scope，别复用管理员 token。

### C.4 CI/CD 五阶段流水线长什么样

流水线**仅在 MR event 触发**，任一 job 失败 → 流水线红 → MR 阻断：

| stage / job | 跑什么 | 对应门禁 |
|---|---|---|
| `gate:process` | `check-gates.sh` | 流程门禁：门禁资产与命令接线完整 |
| `build:compile` | 项目构建命令（按技术栈填） | 编译检查：真实编译，失败即阻断 |
| **`test:unit`** | 项目测试命令 | **单元测试在这**：真实跑测试，产出 `test-summary.json` |
| `quality:check` | `check-quality.sh` | 质量门禁：消费 `test-summary.json` 判通过率/覆盖率/文档同步 |
| `verify:commit-msg` | `commit-msg-lint.sh` | commit 规范（替代 CE 缺失的 Push Rules）|

精简骨架（完整模板见 [gitlab-ci.yml.template](../../.codebuddy/skills/ci-integration/templates/gitlab-ci.yml.template)）：

```yaml
stages: [gate, build, test, quality, verify]
default:
  image: <PLACEHOLDER:INTERNAL_REGISTRY_IMAGE>   # docker executor 用
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'   # 仅 MR 触发
build:compile:
  stage: build
  script: [ <PLACEHOLDER:BUILD_COMMAND> ]        # 如 mvn -B compile
test:unit:
  stage: test
  script: [ <PLACEHOLDER:TEST_COMMAND> ]         # 须产出 docs/quality/test-summary.json
```

要点：

- **真实编译 + 真实单测**是质量门禁的证据来源；若 CI 只消费一个外部 `test-summary.json`，门禁就建在可能过时/造假的文件上。
- **CE 适配**：YAML 关键字必须落在 CE 14.8.2 安全子集内，禁用 14.8 之后的特性（`id_tokens` / `spec:inputs` / CI/CD components / `run:` steps）。
- **渐进接入**：`test:unit` 产物管线还没配好时，可临时给 `quality:check` 设 `allow_failure: true`，待稳定产出 JSON 再改回强制；`gate/build/test/verify` 应一开始就强制。
- **关于 AI 代码审查**：它**默认不是流水线里的阻断 job**（CE 无审查 widget，且 AI 审查要 agent 运行时而非普通 runner），而是走 C.6 的定时任务产出 Critical Issue，经 `/defect-loop` 闭环。

### C.5 把 A/B 场景接到 GitLab 上端到端跑

接好底座后，日常一轮开发（无论新建项目还是老项目扩展）变成：

```text
1. 需求 intake：bridge intake.list 从 GitLab Issue 拉需求（或 /issue-draft-pr 固化工单）
2. 开发：照常走场景 A 或 B 链路 —— 本地软门禁先自觉过一遍
3. 提交：本地建分支 → 实现 → git push → bridge mr.create 建 MR（套 MR 模板 checklist）
4. 流水线：5 阶段自动跑；红灯 → MR 阻断（此刻本地软门禁被 CI 硬化）
5. 修复：bridge pipeline.status 查失败 job → 定位 → 修 → 再推，直到全绿
6. 合并：CI 绿 + 审查通过 → bridge mr.merge 合并
```

> 核心心智：**本地门禁与 CI 门禁是同一套门禁的两次表达。** 本地那次让你（和 AI）在推之前就把问题挡住、少等流水线；CI 那次保证"就算 AI 偷懒跳过了，机器也拦得住"。

#### CI 配置何时写 + 怎么触发

**`.gitlab-ci.yml` 只写一次**：项目首次接入时跑 `/ci-setup` 生成，提交到 `master`/`main`。之后**所有分支、所有 MR 自动适用**，不用每个功能/每条分支重写。你从 GitLab 拉下来的项目，基线里已经带着它。

触发规则就一行——`workflow: rules: - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'`——**门禁流水线只认 MR 事件，push 不触发**：

```text
拉项目(master 已含 .gitlab-ci.yml) → git checkout -b feature/xxx
  ① 本地走 Featureflow（spec-lite → … → code-review）   ⚠️ 不触发 CI
  ② git commit（message 合规：AC123: / feat:）+ git push 分支   ⚠️ 仍不触发
  ③ 建 MR（bridge mr.create / 网页）   ★ CI 在此刻触发：gate→build→test→quality→verify
  ④ 红灯 +「Pipelines must succeed」→ 合并锁死；修 → push 同分支 → ★ 自动重跑
  ⑤ 全绿 + 讨论已解决 → bridge mr.merge 合并
```

| 动作 | `$CI_PIPELINE_SOURCE` | 门禁流水线触发？ |
|---|---|---|
| push 到普通分支（没建 MR）| `push` | ❌ 不触发（最常见误解）|
| 建 MR / 往已开 MR 的源分支再 push | `merge_request_event` | ✅ 触发 5 阶段 |
| GitLab 定时计划（`CI/CD → 计划`）| `schedule` | 触发定时任务类（见 C.6）|
| 打 tag | `push`(tag) | ❌ 门禁流水线不触发；发布流水线另配 |

> 触发动作 = **建 MR**；之后每次往该分支 push 会重跑。AI 侧由 `gitlab-bridge` 串起来：`mr.create`（触发）→ `pipeline.status`（查红在哪个 job）→ 本地修复再推 → `mr.merge`（绿后合并）。

### C.6 24×7 无人值守（`/schedule-setup`）

底座搭好、且放开 MCP 写权限（`GITLAB_READ_ONLY_MODE=false`，需你确认）后，可接入 7 类定时任务，让交付阶段下班后接着跑：

| 任务 | 时间 | 动作 |
|---|---|---|
| #1 文档补充 | 每日 01:00 | 扫 24h 提交 → 规格回填（`/spec-sync`）|
| #3 夜间发布 | 每日 02:00 | 定版 → Release Notes → 打 tag 触发 release 流水线 |
| #4 每日审查 | 每日 03:00 | 增量审查（周日全量）→ 报告 + Critical Issue |
| #9 Issue 清理 | 每日 05:00 | 扫 `.clawbench/issues/` → 修 Critical（`/defect-loop source=clawbench`）|
| #10 GitLab Issue 修复 | 每日 08:00 / 20:00 | 扫 GitLab Issue → 分类 → 修 1 个（`/defect-loop source=gitlab`）|
| #17 MR 审查合并 | 每小时 | open MR → CI 通过 + 审查通过 → 合并 |
| #25 文档周更 | 周一 10:00 | 全量扫描 → README 重写 + 模块增量 |

公共机制：**全走 MR 不直推 main** → 提交后轮询 CI（最多 40 次×30s）→ 失败自动分析日志修复（最多 3 次）→ CI 绿后 auto-merge。

调度方式三选一（`/schedule-setup` 时问你）：CodeBuddy 原生定时能力 / 系统 cron 调 `codebuddy` CLI / **GitLab CE 14.8.2 原生 Pipeline Schedules**（`CI/CD → 计划`，`$CI_PIPELINE_SOURCE == "schedule"` 触发）。

> 🔒 安全：Task #3 夜间发布**只打 tag 触发流水线，不直接部署生产**；生产部署仍需人工审批。定时任务上线前先手动触发一次只读的 Task #4 验证 runbook 跑通。

### C.7 顺带：缺陷闭环 + 活文档

- **`/defect-loop`**：缺陷从发现到关闭自驱动——经 `gitlab-bridge` 的 `issue.*` + `.clawbench`↔GitLab Issue 双向同步 + `bugfix:*` 标签状态机 + Worktree 隔离修复。
- **`/spec-sync` / `/doc-sync`**：把设计文档（`spec/`）和代码自文档（`CONTEXT.md`）做成**活文档**，即时/每日/每周三层自动回填，防文档与代码漂移。

### C.8 GitLab 接入常见坑

1. **没装/没注册 Runner**：流水线永远 pending，门禁形同虚设。
2. **没勾「Pipelines must succeed」**：流水线红了照样能合——门禁白做。这是最常见、最致命的漏配。
3. **`<PLACEHOLDER:...>` 没替换干净**：CI 拉不到镜像或执行空命令。
4. **`USE_PIPELINE` 没开**：`pipeline.status` 探测不到，CI 门禁强依赖它。
5. **MCP 用 `latest` 不锁版本**：工具集漂移，`bridge.probe` 结果不稳定。
6. **绕过 `gitlab-bridge` 直接调 MCP 工具**：GitLab 依赖散落各处，换平台收不回来；且第三方 MCP server 有 ~156 个工具（含改文件、推 commit、merge MR），必须经唯一对接层 + 初期只读管住。
7. **假设 EE 功能可用**：审批规则 / 安全扫描 widget 在 CE 14.8.2 没有，一律按不可用处理，用流水线 job + Protected Branches 替代。

### C.9 进阶优化：事件驱动 + 行内审查（对标 Claude Code 的 GitHub 接入）

GitHub 上 Claude Code 走"GitHub App + 事件触发 + 行内评论 + 多 checks"；CE 14.8.2 受限，但下面几项**纯 CE 就能补齐**，让体验逼近：

| 优化 | 命令 / 能力 | 效果 |
|---|---|---|
| 事件驱动取代轮询 | `/event-setup` + `event-triggers` | webhook 实时触发，秒级；轮询退化为兜底 |
| MR 评论/标签召唤 AI（复刻 `@claude`）| MR 评论 `/code-review`、打 `ai:review` 标签 | 在 MR 上下文直接召唤，无需进会话 / 等 cron |
| 审查行内化 | `gitlab-bridge` 的 `mr.discussion` | 审查意见贴到 diff 行，配合「All threads must be resolved」 |
| 令牌收敛 | Project Access Token + 轮换 | 替代长期个人 `api` PAT（CE 无 OIDC）|
| 审查作阻断 job | `ai-review-job.yml.template`（需专用 runner）| 审查红 → MR 合不了 |
| 结果贴 MR | `commit.status` | MR 上一眼看 AI 检查状态（CE 展示态）|

接入顺序：`/ci-setup` → 令牌收敛 → `/event-setup`（注册 webhook + 接收器）→ 放开写权限 → 把 `scheduled-automation` 轮询调成低频兜底 →（可选）维护带 CLI 的 runner 启用审查 job。设计与权衡见 [event-driven-integration-design](../specs/2026-06-02-event-driven-integration-design.md)。

---

## 附录：命令 → 关键门禁 → 必备证据 速查

| 命令 | 进入前必备（节选） | 产出证据 |
|---|---|---|
| `/spec-lite` | 需求澄清无 TBD、2~3 方向已确认、日志策略已定 | `docs/specs/*-spec-lite.md` + GateContext |
| `/write-plan` | 有效 spec、合同完整；H 级要 brainstormPath + walkthroughPath | `docs/plans/*.md` |
| `/execute-plan` | 计划已批、有验证/证据要求、高风险有回滚保护 | `docs/progress.md` 批次记录 |
| `/requirement-coverage` | 需求分析文档 + 覆盖矩阵 + 可执行用例；非实现者自审 | 通过态覆盖报告 |
| `/unified-test` | 关联 spec+plan；H 级先过 requirement-coverage | `test-summary.json`（通过率/覆盖率）|
| `/security-review` | 命中触发条件强制；9 维度 + 依赖审计 + 秘密扫描 | MD + XLSX 报告（🔴即阻断）|
| `/extend` | historical-spec✓ + requirement-analysis✓ + 项目理解优先级 | 两份 spec + progress 记录 |
| `/fix-bug` | 失败回归测试三件套（path+command+evidence） | 红转绿对比证据 |
| `/release` | spec/plan 已过覆盖审查、三件套齐、checklist 全勾 | changelog + release-notes + rollback-playbook |

---

## 下一步

- 不想记链路？永远从 `/Featureflow <需求原话>` 开始。
- 进度乱了？`/status` 看门禁与证据；`/resume` 从上次交接点恢复。
- 想看抽象的工作流-合同映射：[workflow-playbook.md](./workflow-playbook.md)。
- 想看会话最小规则集：[CODEBUDDY.md](../../CODEBUDDY.md)。
