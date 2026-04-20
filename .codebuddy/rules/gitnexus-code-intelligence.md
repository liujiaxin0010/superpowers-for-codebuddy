---
alwaysApply: false
---

# GitNexus 代码智能集成

当项目已配置 GitNexus MCP 并完成索引时，本规则定义如何利用知识图谱加速代码理解。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

---

## GitNexus 自动安装 Skills 的 CodeBuddy 适配

执行 `npx gitnexus analyze` 后，GitNexus 可能自动生成 `AGENT.md`、`CLAUDE.md` 与 `.claude/skills/*`。

在 **CodeBuddy/Featureflow** 项目中，这些文件的定位是：

- **GitNexus 侧边提示层**：描述 GitNexus 推荐的查询方式与使用场景
- **不是** CodeBuddy 的活跃技能注册目录
- **不替代** `CODEBUDDY.md`、`.codebuddy/commands/*`、`.codebuddy/skills/*`、`.codebuddy/rules/*`、`.codebuddy/agents/*`

如果 `.claude/skills/*` 与 `.codebuddy/*` 出现冲突，**一律以 `.codebuddy/*` 为准**。可以读取 `.claude/skills/*` 理解 GitNexus 的推荐查询模式，但实际执行时必须映射回 CodeBuddy 的命令与规则体系。

| GitNexus 自动安装 Skill | 原始用途 | CodeBuddy 中的承接方式 | 优先查询模式 |
|---|---|---|---|
| `Exploring` | 陌生代码库探索、模块理解、执行链路追踪 | `.codebuddy/rules/project-reading.md`、`/research`、`/doc-init`、`/extend` 前置理解阶段 | `W`（首次 / 调用链盲点）、`E`、`B`、`A`、`F` |
| `Debugging` | 沿调用链定位 bug | `/fix-bug`、`.codebuddy/skills/bug-fix/SKILL.md`、`.codebuddy/skills/systematic-debugging/SKILL.md` | `W`（跨模块链路）、`D`、`F`、`A` |
| `Impact Analysis` | 变更前评估 blast radius | `/extend`、`/write-plan`、`/code-review`、`/code-self-check` 的影响面分析步骤 | `W`（扩展点识别）、`C`、`A` |
| `Refactoring` | 跨文件安全重构 | `/simplify`、`/write-plan`、`/execute-plan`、`.codebuddy/skills/code-simplifier/SKILL.md` | `C`、`D`、`A` |

---

## 索引排除目录（强制）

GitNexus 索引**必须排除**以下依赖/生成目录，不为它们建立图谱节点：

| 类别 | 排除目录 |
|------|---------|
| JS/TS 依赖 | `node_modules/` |
| Go 依赖 | `vendor/` |
| Python 缓存 | `__pycache__/`、`.venv/`、`venv/`、`env/` |
| Java 构建 | `target/`、`.gradle/`、`build/` |
| C/C++ 构建 | `build/`、`cmake-build-*/` |
| Rust 构建 | `target/` |
| 前端构建产物 | `dist/`、`.next/`、`.nuxt/`、`.output/` |
| 版本控制 | `.git/`、`.svn/` |
| 通用第三方 | `third_party/`、`external/`、`deps/` |
| 代码生成 | `gen/`、`pb/`、`generated/` |
| Agent 提示产物 | `.claude/skills/`、`AGENT.md`、`CLAUDE.md` |

执行 `npx gitnexus analyze` 时，这些目录会被自动跳过。如果项目有额外需要排除的目录，在 `.gitnexusignore` 或 GitNexus 配置文件中添加。

---

## 可用性检查（每次使用前必做）

在调用 GitNexus MCP 工具前，先确认可用性：

1. 尝试调用 GitNexus MCP 的任意轻量工具（如 `search`）
2. 如果成功，标记 `gitnexusAvailable = true`，后续操作走 GitNexus 路径
3. 如果失败（连接错误 / 工具不存在），标记 `gitnexusAvailable = false`，回退手动路径
4. 将可用性状态记录到当前会话上下文，避免重复检查

**降级是自动的，不需要询问 Boss。但降级后在 `docs/progress.md` 中记录原因。**

---

## 六大标准查询模式

以下是各流程复用的标准化查询模式。每个模式对应一个 GitNexus MCP 工具调用。

### 模式 A：文件 360° 上下文（单文件理解）

**用途**：理解一个文件的输入、输出、在系统中的位置
**对应工具**：GitNexus `context` 工具
**返回数据**：
- incomingRefs → 谁依赖这个文件（用于 INPUT）
- outgoingRefs → 这个文件依赖谁（用于 INPUT）
- exports → 暴露的函数/类/接口（用于 OUTPUT）
- community → 所属模块聚类（用于 POS）
- processes → 参与的执行流（用于 POS 和 CONTEXT.md 的逻辑描述）

**降级方案**：手动 `read_file` 阅读完整文件，提取 import/export 语句

### 模式 B：模块全景查询（目录级理解）

**用途**：理解一个模块/目录下所有文件的关系
**对应工具**：GitNexus `query` 工具，按目录路径过滤
**返回数据**：模块内所有文件、它们之间的调用关系、模块对外的依赖和被依赖

**降级方案**：手动 `find` + 逐文件阅读头部注释（如已有三层文档）或逐文件完整阅读

### 模式 C：变更影响分析（增量理解）

**用途**：分析 git diff 中的变更会影响哪些文件
**对应工具**：GitNexus `detect_changes` 工具
**返回数据**：直接影响文件 + 间接影响文件（通过调用链传播）+ 影响的执行流

**降级方案**：`git diff --name-only` + 手动 grep 引用点

### 模式 G：增量索引刷新与差异检测（基线漂移）

**用途**：当 GitNexus 上一次 `analyze` 之后又新增/修改了大量代码，知识图谱会与代码不同步。**进入任何代码理解、扩展、审查任务前**必须先执行差异检测，并按需做增量刷新；否则后续模式 A-F 的查询都会基于过期图谱，产出不可靠。

**触发条件（任一满足即触发）**：

1. 距上次 `analyze` 超过 24 小时
2. 当前 HEAD 与 `.codebuddy/state/gitnexus-baseline.json` 中记录的 `lastIndexedCommit` 不一致
3. `git diff --stat <lastIndexedCommit>..HEAD` 中新增/修改源文件 ≥ 20 个
4. 新增了 GitNexus 覆盖范围内的整目录 / 整模块
5. `extend / write-plan / code-review / code-self-check / 项目分析 / 代码解释` 命令进入主体前

**对应工具与流程**：

```text
1. 读取基线: .codebuddy/state/gitnexus-baseline.json
   { "lastIndexedCommit": "<sha>", "indexedAt": "<iso>", "scope": "<paths>" }
2. 调用 GitNexus delta 工具：
   - 优先 `detect_changes since=<lastIndexedCommit>`
   - 若不支持，退回 `query` 比对节点哈希
3. 对比当前工作区：
   git diff --name-status <lastIndexedCommit>..HEAD -- <scope>
4. 判定刷新范围：
   - 增量刷新（<200 文件 / 单模块）：`npx gitnexus analyze --paths <changed-dirs>`
   - 全量刷新（跨模块、目录结构调整、删除文件 >50）：`npx gitnexus analyze`
5. 刷新成功后写回基线：
   { "lastIndexedCommit": "<HEAD>", "indexedAt": "<now>", "scope": "<paths>" }
6. 在 docs/progress.md 记录：
   - 触发条件
   - 差异统计（新增/修改/删除/重命名）
   - 选择的刷新策略与耗时
   - 刷新后被影响最大的 Top-N 模块
```

**差异输出契约（供下游消费）**：

```yaml
delta:
  baselineCommit: <sha>
  headCommit: <sha>
  files:
    added: [...]
    modified: [...]
    deleted: [...]
    renamed: [{from, to}]
  modulesTouched: [...]
  newSymbolsExposed: [...]   # 新增的对外 export
  brokenReferences: [...]    # 旧调用点指向已删除/重命名的目标
  riskLevel: low|medium|high
```

**降级方案（GitNexus 不可用 / 索引彻底失效）**：

1. `git log --since="<lastIndexedAt>" --name-status` 收集变更面
2. 按目录手动复检三层文档（`CONTEXT.md`、文件头部 INPUT/OUTPUT/POS）的同步度
3. 在 `docs/findings.md` 记录“GitNexus 离线 + 变更面 N 文件”，提示下游降级到全量 `project-reading` 流程

**禁止事项**：

1. 禁止跳过基线对比直接使用 GitNexus 查询 —— 过期图谱比无图谱更危险，因为 AI 会以高置信度给出错误调用链
2. 禁止只做局部刷新却隐瞒全局影响 —— 跨模块改动若仅刷新单目录会留下幽灵节点
3. 禁止在 `riskLevel=high` 时不通知 Boss 自动继续 —— 必须先报告差异和刷新计划再确认

### 模式 D：调用链追踪（问题定位）

**用途**：从一个函数/方法出发，追踪完整的调用链
**对应工具**：GitNexus `context` 工具（聚焦 callers / callees）
**返回数据**：上游调用者链 + 下游被调用链 + 所属执行流

**降级方案**：手动 grep 函数名 + 逐层追踪

### 模式 E：全局结构查询（项目全貌）

**用途**：快速理解项目的模块划分、核心入口、整体架构
**对应工具**：GitNexus `query` 工具（不加文件过滤，获取顶层 Community 聚类）
**返回数据**：模块聚类列表 + 模块间连接关系 + 入口文件

**降级方案**：project-reading.md 的四步法（全局扫描 → 文档 → 技术栈 → 依赖）

### 模式 F：语义搜索（模糊定位）

**用途**：根据业务关键词找到相关代码
**对应工具**：GitNexus `search` 工具（混合 BM25 + 语义 + 图扩展）
**返回数据**：匹配的文件/函数，按执行流分组

**降级方案**：`search_content` / `grep` 关键词搜索

### 模式 W：Repo Wiki 全量知识库（code-expose 调用链补偿）

**立项动机**：CodeBuddy 自带的 `code-expose` 代码分析只能展示**静态代码文本**（单文件视角），无法跨文件追踪**函数调用链**。在 `/extend`、`/fix-bug`、`/code-review` 等需要"谁调用了谁、完整路径是什么"的场景，code-expose 结果不足以支撑安全决策。本模式以 GitNexus 知识图谱为数据源，借鉴阿里巴巴 GitNexus 的 Repo Wiki 能力，构建项目级调用链视图并持久化为可复用文档，填补 code-expose 的盲点。

**触发条件（满足任一即触发）**：

1. code-expose 返回的代码片段缺少调用链信息，而当前任务需要判断"影响面 / 调用者 / 下游依赖"
2. `/extend` 进入 Step 0.1（项目理解）且 `gitnexusAvailable=true`
3. `/fix-bug` 需要追踪跨模块调用链以定位根因
4. `/code-review` 审阅涉及共享接口/热点函数的变更
5. `docs/repo-wiki.md` 不存在，或其 `generatedAt` 落后于 `gitnexus-baseline.json` 的 `indexedAt`
6. 用户显式发问："帮我画一下这个项目的调用链 / 扩展点在哪 / 哪些函数被最多地方调用"

**前置条件**：
- `gitnexusAvailable = true`（按"可用性检查"节验证通过）
- 模式 G 基线未漂移（或已刷新至最新 commit）

**执行流程**（必须按顺序，不可跳步）：

```text
Step 1：基线刷新（模式 G）
  - 读取 .codebuddy/state/gitnexus-baseline.json
  - 若 riskLevel=high → 先刷新，再进入 Step 2；不得基于过期图谱生成 Wiki

Step 2：全局模块扫描（模式 E × 1）
  - 调用 GitNexus query（不加文件过滤）
  - 收集：顶层模块聚类 moduleClusters、模块间连接度、候选入口文件列表

Step 3：逐模块调用关系（模式 B × N）
  - 对 moduleClusters 中核心模块（按连接度降序，默认取 Top-5，超过时向 Boss 确认是否全量）
  - 每个模块调用 GitNexus query（按目录过滤），获取：
    · 模块内文件间调用关系
    · 对外暴露的接口（exports）
    · 外部依赖（outgoingRefs）

Step 4：入口调用链追踪（模式 D × K）
  - 对 Step 2 识别的每个核心入口文件调用 GitNexus context（聚焦 callers/callees）
  - 深度限制 ≤ 3 层（避免图谱无限展开）
  - 产出：入口 → 中间层 → 存储/外部服务 的完整调用路径

Step 5：业务语言翻译 + 持久化
  - 按"数据翻译规则"把技术名称转为业务语言
  - 写入 docs/repo-wiki.md（格式见下方输出契约）
  - 在 docs/progress.md 记录：生成耗时、模块覆盖率、input token 估算
```

**输出契约（写入 `docs/repo-wiki.md`）**：

```markdown
# Repo Wiki

> 由 GitNexus 模式 W 生成
> generatedAt: <ISO8601>
> baselineCommit: <sha>
> coverage: <已索引模块数> / <仓库总模块数>

## 1. 模块地图

| 模块 | 路径 | 职责（业务语言） | 对外接口 | 依赖模块 |
|---|---|---|---|---|
| {name} | {path} | {业务描述} | {exports} | {depends-on} |

## 2. 核心调用链

### 调用链 #1：{入口业务名}
{入口文件}:{函数}
  └─ {中间层函数}（{所属模块}）
       └─ {存储/外部调用}（{目标}）

### 调用链 #2：...

## 3. 扩展点推荐

| 扩展点 | 位置（file:line） | 合适原因 | 风险提示 |
|---|---|---|---|
| {name} | {file:line} | {why} | {blast-radius} |

## 4. 高风险区域（修改传播面大）

| 函数/文件 | 调用者数 | 涉及模块数 | 建议 |
|---|---|---|---|
| {symbol} | {N} | {M} | {modify via contract} |

## 5. 信息来源

- GitNexus baseline: {sha} @ {indexedAt}
- 覆盖模式：E + B × {N} + D × {K}
- 未覆盖范围：{说明}
```

**复用策略（避免重复全量生成）**：

1. 进入触发场景时，先读 `docs/repo-wiki.md` 的 `baselineCommit` 字段
2. 若与 `gitnexus-baseline.json.lastIndexedCommit` 一致且 `modulesTouched` 未涉及已记录模块 → **直接复用** Wiki，不重新生成
3. 若仅单模块发生变化 → **增量补丁**（只对该模块重跑 Step 3 + Step 4 相关入口，原地更新 Wiki 对应节）
4. 若跨模块 / 目录结构调整 / `riskLevel=high` → **全量重生成**

**与 code-expose 的互补关系**：

| 维度 | code-expose | 模式 W（Repo Wiki） |
|---|---|---|
| 视角 | 单文件 / 代码片段 | 跨文件 / 项目全局 |
| 呈现 | 源码文本 | 调用图 + 模块关系 |
| 更新 | 实时（文件变更立即反映） | 基线驱动（随 GitNexus 索引刷新） |
| 适用问题 | "这段代码实现了什么" | "谁调用了它 / 改它影响哪些地方 / 最适合挂载在哪" |

**最终行为约束**：不要用模式 W 的输出**替代** code-expose 的源码阅读；两者必须**同时作为证据**呈现给 Boss。回答任何涉及调用链的问题时，声明："基于 code-expose 源码 + docs/repo-wiki.md 模式 W 调用链（baselineCommit=<sha>）"。

**降级方案（GitNexus 不可用 / 索引无法刷新）**：

1. 在 `docs/findings.md` 记录"GitNexus 离线，模式 W 不可用，调用链基于手动追踪"
2. 退回 `project-reading.md` 的手动四步法
3. 在需要调用链的关键节点向 Boss 主动提示："当前无 GitNexus，调用链信息可能不完整，是否继续？"
4. 禁止伪造调用链结论——不确定就写"未确认"

**禁止事项**：

1. 禁止在 `gitnexusAvailable=false` 时仍然报告"已生成 Repo Wiki"——必须显式降级声明
2. 禁止跳过 Step 1 的基线刷新直接进入 Step 2——过期图谱生成的 Wiki 是**反向误导**
3. 禁止把 Wiki 当成**唯一真相源**替代源码阅读——Wiki 是导航图，源码才是事实
4. 禁止在 Wiki 未标注 `coverage` 和 `未覆盖范围` 的情况下声称"全量理解"

---

## 数据翻译规则

GitNexus 返回的是技术结构数据，需要 AI 翻译为业务语言：

| GitNexus 原始数据 | 翻译目标 | 翻译规则 |
|---|---|---|
| `imports: ["./user-repository"]` | INPUT 注释 | 转为业务语义：`UserRepository(数据库操作)` |
| `exports: ["registerUser", "loginUser"]` | OUTPUT 注释 | 转为能力描述：`用户注册/登录能力` |
| `community: "user-domain"` | POS 注释 | 转为定位：`user模块 > 业务逻辑层` |
| `callers: [...]` | 影响范围评估 | 转为：影响 N 个调用者，涉及 M 个模块 |

**结构关系以 GitNexus 为准（Tree-sitter 确定性解析 > AI 阅读理解）。
业务语义由 AI 翻译（GitNexus 返回技术名称，AI 转为业务比喻）。**

---

## 基线状态文件位置

GitNexus 索引基线统一保存在：

- `.codebuddy/state/gitnexus-baseline.json`（每个仓库一个）

字段：

| 字段 | 含义 |
|---|---|
| `lastIndexedCommit` | 上次 `analyze` 时的 HEAD commit sha |
| `indexedAt` | 上次 `analyze` 完成时间（ISO8601） |
| `scope` | 索引覆盖的路径白名单 |
| `excludedDirs` | 实际生效的排除目录列表 |
| `gitnexusVersion` | 上次使用的 gitnexus CLI 版本 |
| `lastDelta` | 最近一次差异检测摘要（统计数 + riskLevel） |

如果文件不存在，第一次进入受影响命令时由 AI 创建空模板并立即触发一次全量 `analyze`。**该文件必须纳入版本控制**，避免协作者重复全量索引。

---

## 与三层文档体系的关系

GitNexus 知识图谱和三层文档体系（INPUT/OUTPUT/POS + CONTEXT.md）不是替代关系：

- **GitNexus** = 实时可查询的结构化代码关系数据（机器友好）
- **三层文档** = 人类和 AI 都能直接阅读的业务语言上下文（人机友好）

GitNexus 是三层文档的**数据源**，三层文档是 GitNexus 数据的**业务语言呈现**。
两者共存，互不替代。
