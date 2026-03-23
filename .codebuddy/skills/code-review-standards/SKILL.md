---
name: code-review-standards
description: "多语言代码审查技能。用于对 Go、Python、Java、JavaScript/TypeScript、Vue、C/C++、Rust、Lua、Shell、BAT、PowerShell 代码做结构化审查，输出按严重度分组的问题清单、修复建议和 XLSX 缺陷汇总。用户提到“代码审查/code review/检查代码质量/PR 审查/审计代码/有没有问题”时触发。"
---

# 编码规范代码审查技能

基于编码规范文档和语言专项审查清单，对指定代码进行系统性审查，输出 MD 审计报告和 XLSX 缺陷汇总表格。

## 审查执行边界（强制）

1. 本技能默认只读审查：先给出完整问题清单，不直接改代码。
2. 输出必须包含：
   - 问题列表（按 `严重/一般/提示` 分组）
   - 每个问题的位置、影响、修复建议
   - 建议下一步命令（如 `/execute-plan`、`/fix-bug`、`/code-self-check applyFix=true`）
3. 只有在 Boss 明确确认“开始修复”后，才允许进入修复流程；修复不在本技能主体内执行。

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

## 资源加载规则

### 必须加载什么

对每种被审查语言，**必须同时加载**：

1. 对应的 `standards/*.md`
2. 对应的 `references/*-review-checklist.md`

### 何时加载什么

- 只审查 Python 文件：只加载 `standards/python.md` + `references/python-review-checklist.md`
- 只审查 Java 文件：只加载 `standards/java.md` + `references/java-review-checklist.md`
- 混合语言变更：只加载变更涉及语言的规范与清单，不要一次性加载全部 20+ 份文件
- 生成 XLSX 汇总表时，再读取 `defect-classification.json`
- 审查包含前端文件时，再协同加载 `web-code-review`

### 禁止的加载方式

1. 禁止只加载 `standards/` 而跳过 `references/`
2. 禁止只加载 `references/` 而跳过 `standards/`
3. 禁止因为“看起来保险”而把全部语言规范一次性读入上下文

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

若只审查当前 diff，优先按 diff 中出现的语言决定加载范围；不要因为仓库里存在其他语言而扩大加载范围。

### 第三步：细读分析代码

在正式审查前，必须先深入阅读和理解代码：

1. **通读全部代码**：逐文件阅读，理解整体架构和业务逻辑
2. **梳理调用关系**：识别模块间依赖、函数调用链、数据流向
3. **理解业务上下文**：结合项目文档、注释、测试用例理解代码意图
4. **标记疑点**：记录不确定的逻辑、可疑的实现、潜在的风险点
5. **对照规范**：将代码实现与编码规范逐条对照，标记不符合项

此步骤确保审查基于充分理解，避免误判。

若审查目标是 PR 或 diff：

1. 先读 diff
2. 再补读受影响文件的必要上下文
3. 只有当 diff 无法解释问题时，才扩大到相关模块

### 第四步：逐文件审查

对每个文件按以下**五大维度**审查：正确性、性能、安全、代码质量、最佳实践。

具体检查项以对应语言的 `references/*-review-checklist.md` 为准，不要依赖通用经验自行发散。

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

使用 `xlsx` 技能生成 `code-review-report.xlsx`。XLSX 列定义和格式要求见 `references/xlsx-column-spec.md`。

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

各语言推荐的静态分析工具见 `references/static-analysis-tools.md`。

## 禁止事项

1. 不要只凭风格偏好给出审查结论——风格偏好因人而异且不影响正确性，以此为据会降低审查公信力
2. 不要在未读上下文时直接判断”这是 bug”——缺少上下文的判断误报率极高，浪费开发者时间
3. 不要一次性加载所有语言规范，稀释重点——多语言规范同时加载会占满上下文窗口，导致真正相关的规则被截断
4. 不要把”代码修改”混进默认只读审查阶段——审查和修复的职责边界不同，混合操作会跳过 owner 确认环节
5. 不要遗漏严重度、位置、影响和修复建议中的任一项——缺项的审查报告无法被执行者直接消费，需要额外沟通确认
