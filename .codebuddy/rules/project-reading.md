---
alwaysApply: false
---

# 项目阅读与理解

增强 AI 的代码阅读能力。**在任何需要理解项目代码的场景中自动生效，包括但不限于：**

- 用户要求“分析这个项目 / 帮我看一下这个工程 / 解释这段代码 / 这块逻辑做了什么 / 这个模块怎么用”
- `/extend`、`/spec-lite`、`/write-plan`、`/code-review`、`/code-self-check`、`/research`、`/fix-bug` 进入主体之前
- 任何要回答“这是干嘛的 / 影响哪些地方 / 谁在调用”的问题

本规则定义了系统化的项目探索策略，确保 AI 能在最短时间内建立对任意项目的准确理解。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

---

## 项目分析/代码解释的强制优先级（铁律）

**任何“分析项目 / 解释代码”的请求都按以下顺序选择信息源，禁止跳级：**

```text
第 1 优先：三层代码自文档（CONTEXT.md + 文件头部 INPUT/OUTPUT/POS）
          ↓ 缺失或与代码不同步时降级
第 2 优先：GitNexus 知识图谱（先按"GitNexus 快速路径"做基线检查再查询）
          ↓ 不可用 / 索引过期且无法刷新 / 语言不支持时降级
第 3 优先：本规则下方的"项目探索四步法"手动阅读
```

降级判定（只要满足任一条即可降级到下一层）：

1. 关键目录缺少 `CONTEXT.md`，或文件头部三行注释缺失/与实现明显不一致
2. GitNexus 不可用、`gitnexus-baseline.json` 缺失或差异检测显示 `riskLevel=high` 且未刷新
3. 用户明确要求“别只看文档/图谱，去看源码”

**输出回答时必须声明信息来源**，例如：

- ✅ "本结论基于 `src/user/CONTEXT.md` + GitNexus 模式 A 查询，已通过基线对比"
- ✅ "三层文档不全，已降级到手动阅读 `src/user/*.go`，覆盖 12/12 个文件"
- ❌ 不要在不声明来源的情况下直接给"项目分析"结论

降级原因须同步写入 `docs/progress.md`（不阻断执行）。

---

## GitNexus 快速路径（优先于手动阅读，但晚于三层文档）

如果项目已配置 GitNexus MCP 且索引可用，**在三层文档不足以回答时，优先使用 GitNexus 获取代码理解**，然后仅对 GitNexus 无法覆盖的部分进行手动阅读。

**进入 GitNexus 查询前必须先做基线对比**（详见 `gitnexus-code-intelligence.md` 模式 G），否则可能基于过期图谱给出错误结论。

这条快速路径等价于 GitNexus 自动安装的 `Exploring` skill 在 CodeBuddy 里的承接实现。即使仓库中存在 `.claude/skills/*`，项目阅读阶段的**实际执行规范仍以本规则为准**；`.claude/skills/*` 只作为 GitNexus 查询思路参考，不作为 CodeBuddy 的活跃 skill 源。

### 三阶段递进查询（模糊 → Boss 确认 → 精确）

> **设计原则**：GitNexus 的精确分析（模式 A/D）对"目标函数的精度"敏感——如果目标猜错，后续调用链追踪都基于错误起点。
> 必须先用模糊匹配（模式 F）锁定候选，Boss 核实后，再做深度精确分析。

```
阶段 1  模糊定位（code-explorer ≈ GitNexus 模式 F）
        → 语义搜索 + BM25 + 图扩展，返回 Top 3-5 候选业务函数/文件
        → 按"业务关键词匹配度 × 代码相似度"排序
        → 对每个候选简述：file:line、函数名、一句话职责
        
        ↓ [硬门禁]
        
阶段 2  Boss 核实（候选 > 1 个时强制）
        → 向 Boss 展示候选清单，请求打勾选定目标
        → 候选 = 1 个且置信度高时可跳过（仍需在 progress.md 记录）
        → Boss 确认后，在 docs/progress.md 写入：候选列表、确认目标、排除原因
        
        ↓
        
阶段 3  精确分析（GitNexus 模式 A + D + C）
        → 模式 A：目标文件的 INPUT / OUTPUT / POS / Community
        → 模式 D：目标函数的上下游调用链（callers / callees）
        → 模式 C：本次变更的 blast radius（用于 /write-plan 估算）
        → 模式 B：如需扩展到整个模块全景则追加
```

### 阶段跳过规则

- 阶段 1 可跳过的情形：用户已明确提供**精确的文件路径 + 函数名**（此时直接进阶段 3）
- 阶段 2 可跳过的情形：阶段 1 仅返回 1 个强匹配候选（置信度 ≥ 0.9），但必须在 `docs/progress.md` 声明跳过原因
- 阶段 3 不可跳过：即使目标精确，也必须做模式 A/D 获取上下游影响面

### 降级条件

以下情况自动降级到手动阅读四步法：
- GitNexus MCP 不可用
- GitNexus 索引不存在或已过期
- 目标文件使用了 GitNexus 不支持的语言
- GitNexus 返回的结果明显不完整（如关键依赖缺失）

降级时无需询问 Boss，直接切换，在 `docs/progress.md` 中记录降级原因。降级后的手动四步法也应保持"模糊匹配（grep 语义搜索）→ Boss 核实候选 → 精确阅读"的三段式节奏。

---

## 核心原则

**先理解再行动。** AI 在修改任何代码之前，必须先确认自己对相关模块有足够的理解。不理解就修改 = 盲改。

### 🚫 禁止偷懒式阅读（强制约束）

**严禁以任何理由采用抽样、重点审查、选择性阅读等策略跳过文件。** 以下行为全部禁止：

- ❌ "由于代码量较大，我将采用重点审查策略"
- ❌ "优先审查核心业务逻辑文件，其余跳过"
- ❌ "代码量大，分批读取，先看关键文件"
- ❌ "由于项目规模较大，我将采用抽样审查方式"
- ❌ "继续读取一些核心文件"（暗示只读部分文件）
- ❌ "选取有代表性的文件进行审查"
- ❌ "挑选几个典型模块进行分析"
- ❌ "时间有限，先看最重要的部分"
- ❌ "让我读取一些关键文件来完成审查"
- ❌ "让我先看几个关键文件"
- ❌ "我来读取一些重要的文件"
- ❌ "让我检查一些核心文件"
- ❌ "文件过大，无法完整读取"（不是跳过的理由，分段读）
- ❌ "文件内容较多，我先看主要部分"
- ❌ 任何包含"一些""部分""关键""核心""重要""主要"等词汇来暗示只读部分文件的表述
- ❌ 任何形式的"选择性阅读""抽样审查""重点审查"来回避完整阅读任务范围内的代码

**正确做法**：任务范围内的所有源码文件必须**逐个完整阅读**，不得遗漏。如果文件确实很多，按目录分批读取，但**每个文件都必须读到**，不允许跳过任何一个。

**如果上下文窗口不够一次读完所有文件——分多轮读取，而不是挑几个"重点"文件敷衍了事。**

**全量阅读执行标准**：
1. 先用 `find` 或 `glob` 列出任务范围内的所有源码文件清单
2. 逐个文件阅读，每读完一个在心中打勾
3. 所有文件读完后，对比文件清单确认无遗漏
4. 如果文件数量超过单轮上下文容量，按目录分批读取，确保每批都完整覆盖该目录下所有文件
5. **禁止用"代表性文件"代替全量阅读**——每个文件的实现细节都可能不同

### 大文件分段读取规则（强制）

**文件过大无法一次读取时，必须分段读取，每次读取 200 行，直到读完整个文件。绝不允许以"文件过大"为由跳过或只读部分内容。**

```
分段读取流程：
1. 第一次：读取第 1-200 行（offset=0, limit=200）
2. 第二次：读取第 201-400 行（offset=200, limit=200）
3. 第三次：读取第 401-600 行（offset=400, limit=200）
4. ...依此类推，直到文件末尾
5. 每段都必须实际阅读和理解，不得跳过任何一段
```

**"文件过大"不是偷懒的理由，而是分段读取的触发条件。**

## 项目探索四步法

### 第一步：全局扫描（10 秒定位项目类型）

```bash
# 1. 检查项目配置文件确定技术栈
ls -la package.json go.mod Cargo.toml pom.xml build.gradle CMakeLists.txt \
     Makefile requirements.txt pyproject.toml composer.json Gemfile 2>/dev/null

# 2. 目录结构（最多2层）
find . -maxdepth 2 -type d \
  ! -path '*/node_modules/*' ! -path '*/.git/*' ! -path '*/vendor/*' \
  ! -path '*/target/*' ! -path '*/build/*' ! -path '*/__pycache__/*' \
  ! -path '*/dist/*' ! -path '*/.next/*' | sort

# 3. 检查版本控制
ls -la .git .svn 2>/dev/null

# 4. 检查是否有 CONTEXT.md 文档体系
find . -name "CONTEXT.md" -maxdepth 3 2>/dev/null
```

### 第二步：阅读文档体系（如果存在）

如果项目已经有 CONTEXT.md 文档体系：

```
1. 根目录 CONTEXT.md    → 全局模块地图
2. 目标模块 CONTEXT.md  → 模块职责、约束、文件清单
3. 文件头部三行注释        → INPUT/OUTPUT/POS 快速定位
4. 只在需要时才读文件正文
```

如果没有 CONTEXT.md，进入第三步。

### 第三步：技术栈识别与入口定位

#### Go 项目

```bash
find . -name "main.go" | head -10
ls cmd/ internal/ pkg/ api/ 2>/dev/null
cat go.mod | head -30
grep -rn "type.*interface" internal/ --include="*.go" | head -20
grep -rn "HandleFunc\|Handle\|router\|gin\.\|echo\.\|mux\." --include="*.go" | head -20
```

#### Java/Spring 项目

```bash
grep -rn "@SpringBootApplication" --include="*.java" | head -5
find src/main/java -maxdepth 4 -type d | sort
grep -rn "@RestController\|@Controller" --include="*.java" | head -20
find . -name "*Service.java" -not -path "*/test/*" | head -20
```

#### Python 项目

```bash
ls main.py app.py manage.py wsgi.py asgi.py 2>/dev/null
grep -l "flask\|django\|fastapi\|tornado" requirements.txt pyproject.toml 2>/dev/null
grep -rn "route\|urlpatterns\|@app\.\|@router\." --include="*.py" | head -20
```

#### C/C++ 项目

```bash
ls CMakeLists.txt Makefile configure.ac meson.build 2>/dev/null
grep -rn "int main" --include="*.c" --include="*.cpp" --include="*.cc" | head -5
find include/ -name "*.h" 2>/dev/null | head -20
ls src/ lib/ 2>/dev/null
```

#### 前端项目

```bash
grep -o '"react"\|"vue"\|"angular"\|"svelte"\|"next"\|"nuxt"' package.json 2>/dev/null
find src -name "router*" -o -name "routes*" 2>/dev/null
ls src/pages/ src/views/ src/app/ 2>/dev/null
find src/components -maxdepth 2 -type f 2>/dev/null | head -20
```

### 第四步：依赖关系追踪

```
从入口文件开始：
1. 阅读入口文件，记录它 import 了什么
2. 对每个 import 的模块，阅读其头部（或头部三行注释）
3. 画出模块依赖图（在脑中）
4. 识别核心模块（被最多模块依赖的）
5. 识别边缘模块（依赖少、被依赖少的）
```

---

## 特定语言的阅读策略

### Go 项目阅读要点

| 目录 | 含义 | 阅读优先级 |
|---|---|---|
| `cmd/` | 可执行程序入口 | ⭐⭐⭐ 最先读 |
| `internal/` | 私有包（不可被外部引用） | ⭐⭐⭐ 核心业务逻辑 |
| `pkg/` | 公共包（可被外部引用） | ⭐⭐ 公共能力 |
| `api/` | API 定义（proto/swagger/OpenAPI） | ⭐⭐ 接口契约 |
| `configs/` | 配置文件 | ⭐ 按需 |
| `scripts/` | 脚本工具 | ⭐ 按需 |
| `test/` `testdata/` | 测试数据 | ⭐ 按需 |
| `gen/` `pb/` | 自动生成代码 | ❌ 不读 |
| `vendor/` | 依赖缓存 | ❌ 不读 |

**Go 接口是关键**：找到 `type XxxInterface interface {}` 就找到了模块边界。

### C/C++ 项目阅读要点

| 目录 | 含义 | 阅读优先级 |
|---|---|---|
| `include/` | 公共头文件（API） | ⭐⭐⭐ 最先读 |
| `src/` | 实现源码 | ⭐⭐⭐ 核心实现 |
| `lib/` | 库代码 | ⭐⭐ |
| `tests/` | 测试 | ⭐ |
| `third_party/` `external/` `deps/` | 第三方 | ❌ 不读 |
| `build/` `cmake-build-*/` | 构建产物 | ❌ 不读 |

**头文件是 C/C++ 的接口**：先读 `.h` 文件理解 API，再读 `.c`/`.cpp` 理解实现。

---

## 理解确认清单

在声称"理解了项目"之前，必须能回答以下问题：

```
□ 项目用什么技术栈？（语言、框架、数据库）
□ 项目的入口在哪里？
□ 核心业务模块有哪些？
□ 模块之间的依赖关系是什么？
□ 数据是怎么流动的？（请求路径）
□ 项目使用什么构建/运行方式？
□ 项目使用什么版本控制？
□ 有没有自动生成的代码需要排除？
```

如果任何一个问题答不上来——**继续阅读，不要开始修改代码。**
