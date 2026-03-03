---
alwaysApply: true
---

# 项目阅读与理解

增强 AI 的代码阅读能力。**在任何需要理解项目代码的场景中自动生效。** 本技能定义了系统化的项目探索策略，确保 AI 能在最短时间内建立对任意项目的准确理解。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

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
