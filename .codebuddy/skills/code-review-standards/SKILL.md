---
name: code-review-standards
description: "专业的多语言代码审查与优化指导。支持代码审查、代码质量分析、性能优化、安全审计、重构建议、最佳实践评估。支持 Go、Python、Java、JavaScript/TypeScript、Vue、C/C++、Rust、Lua、Shell、BAT、PowerShell 共 11 种语言。"
---

# 编码规范代码审查技能

基于编码规范文档和语言专项审查清单，对指定代码进行系统性审查，输出 MD 审计报告和 XLSX 缺陷汇总表格。

## 与 Web 前端专项审查协同

当审查范围包含 `.vue/.js/.jsx/.ts/.tsx` 文件时，除本技能外，需同时启用：

- `.codebuddy/skills/web-code-review/SKILL.md`

协同规则：

1. 本技能负责多语言通用五维审查和主报告汇总
2. `web-code-review` 负责前端 5 类专项缺陷扫描（代码逻辑/视觉呈现/交互体验/性能表现/内容准确性）
3. 输出要求：
   - 主报告：`code-review-report.md`（包含通用 + Web 专项结果）
   - 缺陷汇总：`code-review-report.xlsx`
   - 前端专项结构化结果：`web-code-review-report.json`（若触发）

## 规范文件映射

### 编码规范（standards/）— 强制编码约定

| 语言 | 规范文件 |
|------|---------|
| Python | `standards/python.md` |
| Java | `standards/java.md` |
| C/C++ | `standards/c-cpp.md` |
| Go | `standards/go.md` |
| JavaScript/TypeScript | `standards/javascript.md` |
| Vue | `standards/vue.md` |
| Rust | `standards/rust.md` |
| Lua | `standards/lua.md` |
| Shell/Bash | `standards/shell.md` |
| BAT/Batch | `standards/bat.md` |
| PowerShell | `standards/powershell.md` |

### 审查清单（references/）— 常见缺陷与反模式

| 语言 | 审查清单 |
|------|---------|
| Go | `references/go-review-checklist.md` |
| Python | `references/python-review-checklist.md` |
| Java | `references/java-review-checklist.md` |
| JavaScript/TypeScript | `references/javascript-review-checklist.md` |
| Vue | `references/vue-review-checklist.md` |
| C/C++ | `references/cpp-review-checklist.md` |
| Rust | `references/rust-review-checklist.md` |
| Lua | `references/lua-review-checklist.md` |
| Shell/Bash | `references/shell-review-checklist.md` |
| PowerShell/Bat | `references/powershell-review-checklist.md` |

审查时**必须同时加载**对应语言的编码规范（standards/）和审查清单（references/），二者缺一不可。规范用于检查编码约定，清单用于发现常见缺陷和反模式。

**⚠️ 禁止只加载 standards/ 而跳过 references/，也禁止反过来。两类文档协同使用才能保证审查的完整性。**

## 审查流程

### 第一步：确定审查范围

1. 根据用户指定的路径或参数确定审查文件范围
2. 如未指定，使用 `git diff` 或 `svn diff` 获取最近变更的文件
3. 识别文件语言类型，加载对应的编码规范文档

### 第二步：加载编码规范

根据检测到的语言类型，读取对应的规范文件和审查清单：
- `.py` → Python, `.java` → Java, `.c/.cpp/.h/.hpp` → C/C++, `.go` → Go
- `.js/.ts/.jsx/.tsx` → JavaScript, `.vue` → Vue, `.rs` → Rust, `.lua` → Lua
- `.sh/.bash` → Shell, `.bat/.cmd` → BAT, `.ps1/.psm1` → PowerShell
- 如果项目包含多种语言，加载所有相关规范和清单

### 第三步：细读分析代码

在正式审查前，必须先深入阅读和理解代码：

1. **通读全部代码**：逐文件阅读，理解整体架构和业务逻辑
2. **梳理调用关系**：识别模块间依赖、函数调用链、数据流向
3. **理解业务上下文**：结合项目文档、注释、测试用例理解代码意图
4. **标记疑点**：记录不确定的逻辑、可疑的实现、潜在的风险点
5. **对照规范**：将代码实现与编码规范逐条对照，标记不符合项

此步骤确保审查基于充分理解，避免误判。

### 第四步：逐文件审查

对每个文件按以下**五大维度**审查（结合对应语言规范和审查清单）：

#### 维度一：正确性（Correctness）
- 逻辑错误与 Bug
- 边界条件处理（null、空值、越界、off-by-one）
- 错误处理完整性与异常传播
- 资源泄漏（内存、连接、文件句柄、锁）
- 数据类型不匹配与精度问题
- 死代码与不可达分支
- 未初始化变量

#### 维度二：性能（Performance）
- 算法复杂度（时间/空间）
- 不必要的计算或内存分配
- 数据库查询优化（N+1 查询、缺少索引、SELECT *）
- 并发问题（竞态条件、死锁、线程/协程泄漏）
- I/O 瓶颈与缓存利用
- 字符串拼接效率（各语言有不同最佳实践）

#### 维度三：安全（Security）
- 输入验证与过滤（SQL 注入、XSS、CSRF、命令注入、路径遍历）
- 认证/授权问题
- 敏感数据泄露（日志、错误信息、响应体）
- 硬编码凭证/密钥
- 不安全的反序列化
- 弱加密算法
- CORS 配置

#### 维度四：代码质量（Code Quality）
- 文件组织与命名规范
- 函数长度与圈复杂度
- 代码重复（DRY 原则）
- 职责分离与单一职责原则
- 注释规范与必要性
- 魔法数字与硬编码字符串
- 接口设计与模块耦合度

#### 维度五：最佳实践（Best Practices）
- 语言特定惯用写法（参照 references/ 审查清单）
- 框架约定与设计模式
- SOLID 原则
- 错误处理模式与日志规范
- 编程语言特定规则（编译预处理、宏定义、类型系统等）

### 第五步：生成 MD 审计报告

在项目根目录生成 `code-review-report.md`，格式如下：

```markdown
# 代码审查报告

**审查日期**: YYYY-MM-DD
**审查范围**: [文件列表/模块]
**审查依据**: [使用的编码规范]
**审查结论**: 通过 / 不通过

## 审查统计

| 严重程度 | 数量 |
|---------|------|
| 严重 | N |
| 一般 | N |
| 提示 | N |

## 缺陷详情

### 严重问题（N项）

#### 1. [问题标题]
- **位置**: `文件路径:行号`
- **模块**: [所属模块]
- **缺陷来源**: [来源阶段]
- **缺陷类型**: [类型] > [子类型]
- **问题描述**: [详细描述]
- **违反规范**: [对应规范条目]
- **改进方式**:
  [具体修复建议或示例代码]

### 一般问题（N项）
...

### 提示（N项）
...

## 总结
[审查结论总结，关键发现和改进建议]
```

### 第六步：生成 XLSX 缺陷汇总表

使用 `xlsx` 技能生成 `code-review-report.xlsx`，包含以下表头：

| 列 | 字段名 | 是否必填 | 说明 |
|----|--------|---------|------|
| A | 评审人员 | * | 审查执行者名称 |
| B | 描述 | * | 缺陷的详细描述 |
| C | 位置 | | 文件路径:行号 |
| D | 模块 | | 所属功能模块 |
| E | 缺陷严重程度 | * | 严重/一般/提示 |
| F | 缺陷来源 | * | 见缺陷分类数据 |
| G | 缺陷类型 | | 见缺陷分类数据 |
| H | 缺陷子类型 | | 见缺陷分类数据 |
| I | 缺陷界定 | * | 确认/不是缺陷/重复/延期处理 |

XLSX 格式要求：
- **表格内所有内容必须使用中文**（表头、缺陷描述、模块名称、改进建议、严重程度等全部中文）
- 表头行加粗，背景色浅蓝，冻结首行
- 必填字段列标题带 `*` 标记
- 列宽自适应内容
- 使用数据验证（下拉列表）限制枚举字段的可选值
- 缺陷分类的下拉选项参考 `defect-classification.json`

---

## 缺陷分类扩展

### 缺陷严重程度

| 等级 | 标记 | 说明 |
|------|------|------|
| 严重 | 🔴 | 导致崩溃、安全漏洞、数据丢失、严重性能问题 |
| 一般 | 🔵 | 代码风格、命名规范、文档缺失、可维护性 |
| 提示 | 🟢 | 优化建议、最佳实践推荐 |

### 缺陷来源

需求 / 设计 / 编码 / 测试 / 文档

### 缺陷类型

安全 / 性能 / 正确性 / 代码质量 / 最佳实践 / 逻辑 / 接口 / 规范

### 缺陷界定

确认 / 不是问题 / 待确认 / 延后处理

---

## 特殊审查类型

### 遗留代码审查
- 优先关注高风险区域
- 建议渐进式改进
- 重构前先补充测试
- 为不清晰的逻辑添加文档

### Pull Request 审查
- 检查是否有破坏性变更
- 验证测试覆盖率
- 审查 commit message 规范

### 上线前审查
- 安全审计
- 性能测试结果确认
- 错误处理完整性
- 日志与监控就绪

---

## 推荐静态分析工具

| 语言 | 工具 |
|------|------|
| Go | golangci-lint, go vet, staticcheck |
| Python | pylint, flake8, mypy, bandit |
| Java | SpotBugs, PMD, SonarQube |
| JavaScript/TS | ESLint, TypeScript compiler |
| Vue | eslint-plugin-vue, Vetur |
| C/C++ | clang-tidy, cppcheck, Valgrind, AddressSanitizer |
| Rust | clippy, rustfmt, cargo-audit |
| Lua | luacheck, selene |
| Shell/Bash | shellcheck, shfmt |
| PowerShell | PSScriptAnalyzer |

---

## 重构建议模式

当代码需要重构时，按以下模式给出建议：

- **提取方法**：函数超过 30 行或做多件事
- **提取变量**：复杂表达式或重复计算
- **消除魔法数字**：使用命名常量
- **简化条件**：减少嵌套，使用卫语句
- **消除重复**：DRY 原则
