# C++/Qt Code Reviewer Skill

完全独立的 C++/Qt 代码审查技能，支持缺陷检测、编码规范检查和代码量统计，自动生成 Excel 格式审查报告。专为 EZStation / EZTools 两个 C++/Qt 项目设计。

## 特点

- ✅ **完全独立**：不依赖外部环境或项目
- ✅ **内置规则**：缺陷检测规则内嵌在 skill 内部
- ✅ **动态读取**：编码规范从 `.codebuddy/rules/cpp-qt-coding-standard.md` 动态读取
- ✅ **双重检查**：同时检查代码缺陷和编码规范合规性
- ✅ **简单易用**：只需提供文件路径，自动执行审查
- ✅ **结构化报告**：生成包含详细缺陷信息的 Excel 报告
- ✅ **多项目支持**：根据项目路径自动选择 EZStation / EZTools 日志变体

## 规则来源

### 1. 内置规则（skill 内部）

- **缺陷分类映射**：`references/defect-classification.md`
- **分析指南**：`references/code-analysis-guide.md`
- **缺陷检测规则**：代码逻辑、内存管理、线程安全、性能、Qt 机制

### 2. 项目规则（动态读取）

- **编码规范**：`.codebuddy/rules/cpp-qt-coding-standard.md`
  - 通用章节（1~4、6~7）：两个项目共享
  - 日志章节（5.1 / 5.2）：按项目路径关键字自动选用
    - `ezstation` → 5.1 EZStation（`LOG_MESSAGE` 宏）
    - `eztools` → 5.2 EZTools（`LOG_RECORD` 宏）

## 功能特性

### 1. 缺陷检测

- 代码逻辑类缺陷
- 内存管理类缺陷
- 线程安全类缺陷
- 性能表现类缺陷
- Qt 机制类缺陷

### 2. 编码规范检查

- **命名规范**：类、结构体、枚举、方法、成员变量、宏的命名规则
- **缩进与格式**：4 空格缩进、运算符空格、关键字空格
- **注释规范**：禁止使用 `//`，必须使用 `/* */`
- **Qt 信号槽**：`sig` / `slot` 前缀、函数指针连接方式
- **比较运算符**：常量放左边的比较规范
- **日志规范**：项目变体（EZStation 用 `LOG_MESSAGE`，EZTools 用 `LOG_RECORD`）、英文日志内容

### 3. 代码量统计

- **文件统计**：文件总数、每个文件的行数
- **行数统计**：总行数、代码行数、注释行数、空行数
- **注释率**：注释行数 / 总行数
- **缺陷统计**：按级别统计（Major / General / Suggest）

## 使用方法

### 基本用法

1. 在对话中请求代码审查：

   ```
   请帮我审查这个文件：path/to/your/source.cpp
   ```

2. Skill 会自动：

   - 读取待审查文件
   - 加载内置的审查规则
   - 动态读取 `.codebuddy/rules/cpp-qt-coding-standard.md`
   - 根据文件路径关键字选择日志变体
   - 执行静态代码分析
   - 识别 Major 级别缺陷
   - 生成 Excel 报告

### 自定义输出路径

可以指定 Excel 报告的输出位置：

```
请审查 src/mainwindow.cpp，报告保存到 /path/to/output/mainwindow_review.xlsx
```

### 审查结果

审查完成后会生成 Excel 报告，包含两个页签：

#### 页签 1：代码统计

**总体统计：**

- 审查文件数、总行数、代码行数、注释行数、空行数
- 注释率、缺陷总数

**每个文件的统计：**

- 文件名、总行数、代码行数、注释行数、空行数
- 各级别缺陷数量（Major / General / Suggest）

#### 页签 2：缺陷详情

- 评审人员：x08666
- 缺陷描述：问题描述 + 修改建议
- 位置：文件名:行号
- 模块：完整文件路径
- 缺陷严重程度：Major / General / Suggest
- 缺陷来源：编码 / 详细设计 / 概要设计等
- 缺陷类型和子类型：具体分类
- 缺陷界定：代码逻辑类 / 内存管理类 / 线程安全类 / 性能表现类 / Qt 机制类 / 编码规范类

## 审查重点

Skill 会重点关注以下方面的 Major 缺陷：

### 代码逻辑类

- 函数返回值处理问题
- 缺少错误处理
- 参数校验缺失
- 条件判断错误
- 指针空值检查缺失

### 内存管理类缺陷

- 内存泄漏（new/delete 不匹配）
- 野指针访问
- 缓冲区溢出
- 智能指针使用不当
- 资源未释放

### 线程安全类缺陷

- 竞态条件
- 死锁风险
- 共享数据未加锁保护
- 线程间通信问题

### 性能表现类缺陷

- 不必要的内存拷贝
- 低效算法
- 资源竞争
- 频繁动态内存分配

### Qt 机制类缺陷

- 信号槽连接错误
- 对象树内存管理问题
- 事件循环阻塞
- 跨线程 UI 操作
- QThread 误用

## 技能结构

```
.codebuddy/skills/cpp-qt-code-reviewer-skill/
├── SKILL.md              # 技能主定义文件
├── README.md             # 本文件
└── references/
    ├── defect-classification.md            # 缺陷分类映射表
    └── code-analysis-guide.md  # 代码分析指南

项目规则（动态读取）：
.codebuddy/
└── rules/
    └── cpp-qt-coding-standard.md   # 编码规范规则（动态读取）
```

## 缺陷分类

所有缺陷都按照内置的分类标准进行归类，包括：

- **缺陷来源**：编码、详细设计、概要设计、需求分析、测试用例、测试计划
- **缺陷类型**：具体的缺陷类别
- **缺陷子类型**：详细的缺陷子类型
- **缺陷界定**：5 大类别

## 注意事项

1. **内置规则**：缺陷检测规则已内置在 skill 中，无需额外配置
2. **动态读取**：编码规范从 `.codebuddy/rules/cpp-qt-coding-standard.md` 动态读取，确保使用最新版本
3. **项目变体**：日志规范按项目路径自动选用（ezstation → 5.1；eztools → 5.2）
4. **默认启用**：编码规范检查和代码量统计默认启用
5. **即时生效**：修改项目规则后，下次审查立即生效，无需更新 skill
6. **可操作建议**：每个缺陷都提供具体的修改建议
7. **报告格式**：Excel 报告包含「代码统计」和「缺陷详情」两个页签

## 示例

### 示例 1：基本审查

```
用户：请帮我审查 d:/pro/ezstation/src/mainwindow.cpp

系统：
- 读取文件
- 检测项目路径含 "ezstation" → 选用 5.1 节（LOG_MESSAGE 宏）
- 分析代码
- 识别 6 个 Major 缺陷
- 生成 Excel 报告到 D:/Review/mainwindow_review.xlsx
```

### 示例 2：自定义输出路径

```
用户：审查 src/eztools/network/client.cpp，报告保存到 reports/client_review.xlsx

系统：
- 检测项目路径含 "eztools" → 选用 5.2 节（LOG_RECORD 宏）
- 执行代码审查
- 生成报告到指定路径 reports/client_review.xlsx
```

## 版本信息

- **版本**：1.1.0
- **最后更新**：2026-05-19
- **依赖**：`xlsx` skill（用于生成 Excel 报告）
- **变更说明**：从 `.lingma/rules/` 迁移到 `.codebuddy/rules/`；新增项目变体支持（EZStation / EZTools 日志宏自动切换）
