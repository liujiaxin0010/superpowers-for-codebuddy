---
name: cpp-qt-code-reviewer-skill
description: 对 EZStation / EZTools 项目的 C++/Qt 代码（.cpp / .h / .hpp / .c / .ui / .qrc / .pro）进行自动化代码审查。内置缺陷检测规则，动态读取 `.codebuddy/rules/cpp-qt-coding-standard.md` 编码规范，统计代码量，调用 `xlsx` skill 生成包含「代码统计」与「缺陷详情」两个页签的 Excel 报告（默认输出 `D:/Review/{filename}_review.xlsx`）。
allowed-tools:
disable: false
---

# C++/Qt 代码审查 Skill

此技能为 EZStation / EZTools 两个 C++/Qt 项目提供自动化代码审查功能，支持：

1. 缺陷检测（根据内置缺陷分类规则）
2. 编码规范检查（动态读取 `.codebuddy/rules/cpp-qt-coding-standard.md`）
3. 代码量统计（文件数、行数、缺陷数量等）
4. 生成结构化的 Excel 报告

> 本技能完全独立，内置缺陷检测规则；编码规范从 `.codebuddy/rules/` 动态读取，确保使用最新版本。

## 目的

根据内置的缺陷分类规则分析 C++ 和 Qt 代码（.cpp、.h、.hpp、.c、.cxx、.hxx、.ui、.qrc、.pro），识别问题和规范违规，统计代码量指标，并生成标准化的 Excel 报告。

## 何时使用此技能

在以下情况下使用此技能：

- 用户请求对 EZStation / EZTools 项目下的 C++/Qt 文件进行代码审查 / review
- 用户要求检查代码是否符合 `.codebuddy/rules/cpp-qt-coding-standard.md` 编码规范
- 用户要求生成 Excel 格式的代码审查报告
- 用户指定要审查的文件或模块

## 使用流程

### 1. 接收审查请求

等待用户指定：

- 要审查的目标文件路径（必需）
- 可选：Excel 报告输出路径（默认为 `D:/Review/{filename}_review.xlsx`）
- 可选：严重程度过滤器（默认：仅 Major）
- 可选：是否检查编码规范（默认：是）
- 可选：是否统计代码量（默认：是）

### 2. 读取配置和规则

**内置配置（skill 内部）：**

- 读取 `references/缺陷.md` 获取缺陷分类映射
- 读取 `references/code-analysis-guide.md` 获取代码审查方法论

**项目规则（动态读取）：**

- 读取 `.codebuddy/rules/cpp-qt-coding-standard.md` 获取编码规范规则
- 根据项目路径关键字（`ezstation` / `eztools`，大小写不敏感）选用 5.1 或 5.2 节作为日志规范

**注意**：编码规范从 `.codebuddy/rules/` 动态读取，确保始终使用最新版本，避免重复维护。

### 3. 执行代码审查分析

**加载参考材料：**
首先加载代码分析指南以获取详细的审查方法论：

- 阅读 `references/code-analysis-guide.md` 以获得系统性的分析方法
- 阅读 `.codebuddy/rules/cpp-qt-coding-standard.md` 以了解编码规范要求
- 该指南提供了识别缺陷的具体模式、示例和最佳实践

**代码量统计：**
在审查过程中，统计以下指标：

- **文件统计**：文件总数、每个文件的行数
- **行数统计**：
  - 总行数（Total Lines）
  - 代码行数（Code Lines，排除空行和注释）
  - 注释行数（Comment Lines）
  - 空行数（Blank Lines）
- **缺陷统计**：
  - 缺陷总数（按级别：Major / General / Suggest）
  - 编码规范违规数

**审查重点领域：**

#### A. 缺陷检测（根据 `references/缺陷.md`）

- 代码逻辑和实现问题
- 内存管理问题
- 线程安全问题
- 性能关注点
- Qt 特有机制问题（信号槽、对象树、事件循环等）

#### B. 编码规范检查（根据 `.codebuddy/rules/cpp-qt-coding-standard.md`）

**命名规范检查：**

- 类名：以 `C` 开头 + 大驼峰（如 `CImageProcessor`）
- 结构体：`typedef struct tag` + 大驼峰，别名全大写 + `_S`（如 `SERVERCFG_IMPORT_S`）
- 枚举：`typedef enum tag` + 大驼峰，别名全大写 + `_E`（如 `MOUSE_SECTION_E`）
- 公共方法：大驼峰（如 `ConnectToHost()`）
- 私有/保护方法：小驼峰（如 `processFrame()`）
- 成员变量：
  - 整型：`m_l` + 大驼峰（如 `m_lReconnectAttempts`）
  - 浮点：`m_f` + 大驼峰（如 `m_fTemperature`）
  - 类类型：`m_o` + 大驼峰（如 `m_oMessageQueue`）
  - 字符串：`m_str` + 大驼峰（如 `m_strName`）
  - 指针：`m_p` + 大驼峰（如 `m_pInstance`）
- 宏：全大写 + 下划线（如 `DEBUG_LOG`）

**缩进与格式检查：**

- 使用 4 个空格缩进（禁止 Tab）
- 运算符两侧加空格
- 函数参数逗号后加空格
- 控制语句关键词后加空格

**注释规范检查：**

- **严格禁止使用 `//` 注释**
- **所有注释必须使用 `/* */` 格式**
- 头文件函数声明后增加功能注释

**Qt 信号槽检查：**

- 信号命名：`sig` + 大驼峰（如 `sigConnected()`）
- 槽函数命名：`slot` + 大驼峰（如 `slotConnected()`）
- 使用函数指针形式连接，禁止 `SIGNAL` / `SLOT` 宏

**比较运算符规范：**

- 常量放左边，变量放右边（如 `MAX_VALUE > lValue`）
- 禁止变量放左边（如 `lValue < MAX_VALUE` 不允许）

**日志规范检查：**

- 按项目变体选择日志宏：
  - EZStation 项目（路径含 `ezstation`，大小写不敏感）→ 使用 `LOG_MESSAGE` 宏 + `EN_LOG_LEVEL_*` 等级
  - EZTools 项目（路径含 `eztools`，大小写不敏感）→ 使用 `LOG_RECORD` 宏 + `LOG_LEVEL_*` 等级
- 日志内容必须使用英文
- 不允许残留 `console` / `print` / `qDebug` / `std::cout` 等控制台输出

**严重程度分类：**

- Major（严重）：严重影响功能、安全或用户体验的问题
- General（一般）：影响代码质量但不阻碍功能的问题
- Suggest（建议）：微小的改进或最佳实践建议

### 4. 将缺陷映射到分类系统

将识别出的问题映射到 `references/缺陷.md` 中的缺陷分类：

- **缺陷来源**（Source）：来自缺陷.md 中的类别（例如：编码、详细设计、概要设计等）
- **缺陷类型**（Type）：主要缺陷类别
- **缺陷子类型**（Subtype）：具体的缺陷子类型
- **缺陷界定**（Category）：以下之一：代码逻辑类、内存管理类缺陷、线程安全类缺陷、性能表现类缺陷、Qt 机制类缺陷

**编码规范违规映射：**

- `编码 | 编程语言使用 | 编程风格` — 缩进、空格、命名不规范
- `编码 | 编程语言使用 | 标识符和表达式` — 使用 NULL 而非 nullptr
- `编码 | 编程语言使用 | 注释不规范、废弃代码` — 使用 `//` 注释
- `编码 | 常量、变量使用 | 命名` — 命名不规范
- `编码 | 函数、模块接口_编码 | 形参和实参类型匹配、参数说明及校验` — 信号槽连接方式错误

**约束条件**：

- 缺陷来源、类型和子类型必须精确映射到 `references/缺陷.md` 中的某一行
- 不要跨行组合条目
- 不要创建参考文件中没有的新条目
- 输出严重程度为 Major（严重）、General（一般）、Suggest（建议）的缺陷

### 5. 生成 Excel 报告

完成审查后，调用 `xlsx` skill 生成 Excel 报告。

**Excel 报告包含两个页签：**

#### 页签 1：代码统计

| 统计项 | 数值 | 说明 |
|--------|------|------|
| 审查文件数 | N | 审查的文件总数 |
| 总行数 | N | 所有文件的总行数 |
| 代码行数 | N | 排除空行和注释后的实际代码行 |
| 注释行数 | N | 注释行数 |
| 空行数 | N | 空行数 |
| 注释率 | N% | 注释行数 / 总行数 |
| Major 缺陷数 | N | 严重缺陷数量 |
| General 缺陷数 | N | 一般缺陷数量 |
| Suggest 缺陷数 | N | 建议缺陷数量 |
| 编码规范违规 | N | 编码规范违规数量 |
| 缺陷总数 | N | 所有缺陷总和 |

**每个文件的详细统计：**

| 文件名 | 总行数 | 代码行数 | 注释行数 | 空行数 | Major | General | Suggest |
|--------|--------|----------|----------|--------|-------|---------|---------|
| file1.cpp | 100 | 80 | 10 | 10 | 2 | 1 | 0 |
| file2.cpp | 200 | 150 | 30 | 20 | 1 | 3 | 2 |

#### 页签 2：缺陷详情

**报告字段：**

- 评审人员：固定值 "x08666"
- 描述：描述问题并提供具体的改进建议。不要包含指向方法或文件的超链接。
- 位置：格式为 "filename:lineNumber"（原始文件中的精确行号）
- 模块：完整文件路径
- 缺陷严重程度：严重问题为 "Major"，一般问题为 "General"、建议问题为 "Suggest"
- 缺陷来源：从缺陷分类映射
- 缺陷类型：从缺陷分类映射
- 缺陷子类型：从缺陷分类映射
- 缺陷界定：5 个类别之一

**使用 `xlsx` skill：**

使用审查数据调用 `xlsx` skill：

1. 将审查数据准备为包含所需字段的对象数组
2. 调用 `xlsx` skill 创建 Excel 文件
3. 指定输出路径（用户指定或默认位置）

**输出路径：**
默认为 `D:/Review/{filename}_review.xlsx`，用户可自定义输出路径。

**注意：**

- Excel 文件将使用 `xlsx` skill 生成
- 列应适当调整大小以提高可读性

### 6. 确认完成

生成报告后，在控制台输出统计摘要：

```
========================================
代码审查完成
========================================
【代码统计】
审查文件数：3
总行数：1,250
代码行数：980
注释行数：150
空行数：120
注释率：12.0%
【缺陷统计】
Major：5
General：8
Suggest：3
编码规范违规：6
缺陷总数：16
报告路径：D:/Review/multi_files_review.xlsx
========================================
```

同时报告：

- 报告发现的 Major 缺陷数量
- 确认 Excel 文件位置
- 如有要求，提供缺陷类型摘要

## 数据结构

### 审查结果对象

```javascript
{
  reviewer: "x08666",
  description: "问题描述。修改建议：...",
  location: "mainwindow.cpp:123",
  module: "d:/pro/project/src/mainwindow.cpp",
  severity: "Major",
  source: "编码",
  type: "函数、模块接口_编码",
  subtype: "函数返回值的处理问题",
  category: "代码逻辑类"
}
```

### 代码统计对象

```javascript
{
  summary: {
    totalFiles: 3,           // 文件总数
    totalLines: 1250,        // 总行数
    codeLines: 980,          // 代码行数
    commentLines: 150,       // 注释行数
    blankLines: 120,         // 空行数
    commentRate: "12.0%",    // 注释率
    majorCount: 5,           // Major 缺陷数
    generalCount: 8,         // General 缺陷数
    suggestCount: 3,         // Suggest 缺陷数
    standardViolations: 6,   // 编码规范违规数
    totalDefects: 16,        // 缺陷总数
  },
  fileStats: [               // 每个文件的统计
    {
      filename: "file1.cpp",
      totalLines: 100,
      codeLines: 80,
      commentLines: 10,
      blankLines: 10,
      major: 2,
      general: 1,
      suggest: 0
    }
    // ...
  ]
}
```
