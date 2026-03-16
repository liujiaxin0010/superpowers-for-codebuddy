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
| `Exploring` | 陌生代码库探索、模块理解、执行链路追踪 | `.codebuddy/rules/project-reading.md`、`/research`、`/doc-init`、`/extend` 前置理解阶段 | `E`、`B`、`A`、`F` |
| `Debugging` | 沿调用链定位 bug | `/fix-bug`、`.codebuddy/skills/bug-fix/SKILL.md`、`.codebuddy/skills/systematic-debugging/SKILL.md` | `D`、`F`、`A` |
| `Impact Analysis` | 变更前评估 blast radius | `/extend`、`/write-plan`、`/code-review`、`/code-self-check` 的影响面分析步骤 | `C`、`A` |
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

## 与三层文档体系的关系

GitNexus 知识图谱和三层文档体系（INPUT/OUTPUT/POS + CONTEXT.md）不是替代关系：

- **GitNexus** = 实时可查询的结构化代码关系数据（机器友好）
- **三层文档** = 人类和 AI 都能直接阅读的业务语言上下文（人机友好）

GitNexus 是三层文档的**数据源**，三层文档是 GitNexus 数据的**业务语言呈现**。
两者共存，互不替代。
