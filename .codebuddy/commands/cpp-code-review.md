你的任务是：使用 `cpp-qt-code-reviewer-skill` 对 EZStation / EZTools 项目的 C++/Qt 代码进行专业审查。

## 核心流程

### 1. 触发条件

当用户输入以下关键词时触发本命令：

- "代码 review"
- "代码审查"
- "cpp review"
- "C++ 代码审查"
- "Qt 代码审查"
- "cpp-qt-code-reviewer-skill"
- "使用 cpp-qt-code-reviewer-skill"

### 2. 文件类型识别

自动识别以下文件类型：

- C++ 源文件：`.cpp`, `.h`, `.hpp`, `.cxx`, `.hxx`
- C 源文件：`.c`, `.h`
- Qt 相关文件：`.ui`, `.qrc`, `.pro`

### 3. 项目变体识别

检测文件路径关键字（大小写不敏感）选用日志规范：

- 路径含 `ezstation` → EZStation 项目 → 5.1 节 `LOG_MESSAGE` 宏
- 路径含 `eztools` → EZTools 项目 → 5.2 节 `LOG_RECORD` 宏
- 两者都不匹配 → 询问 Boss 应按哪个项目变体审查

### 4. 执行步骤

#### 步骤 1：调用 cpp-qt-code-reviewer-skill

```
使用 cpp-qt-code-reviewer-skill 技能审查以下代码：
[用户提供的文件路径或代码内容]
```

#### 步骤 2：等待技能完成

技能将自动：

- 读取编码规范：`.codebuddy/rules/cpp-qt-coding-standard.md`
- 读取缺陷分类：`.codebuddy/skills/cpp-qt-code-reviewer-skill/references/defect-classification.md`
- 按项目变体选用日志规范章节
- 执行代码分析
- 识别 Major / General / Suggest 级别缺陷
- 识别编码规范违规

#### 步骤 3：生成 Excel 报告

技能将调用 `xlsx` skill 生成报告，包含：

- **页签 1：代码统计**
  - 审查文件数、总行数、代码行数
  - 注释行数、空行数、注释率
  - 缺陷统计（Major / General / Suggest / 编码规范违规）

- **页签 2：缺陷详情**
  - 评审人员：x08666
  - 详细描述（问题 + 修改建议）
  - 精确位置（文件名:行号）
  - 完整模块路径
  - 缺陷严重程度：Major / General / Suggest
  - 缺陷分类（来源、类型、子类型、界定）

#### 步骤 4：报告输出

默认输出位置：`D:/Review/[filename]_review.xlsx`

### 5. 输出格式

```
========================================
代码审查完成
========================================

【项目变体】
项目类型：EZStation / EZTools
日志规范：LOG_MESSAGE / LOG_RECORD（按变体显示）

【代码统计】
审查文件数：N
总行数：N
代码行数：N
注释行数：N
空行数：N
注释率：N%

【缺陷统计】
Major：N
General：N
Suggest：N
编码规范违规：N
缺陷总数：N

报告路径：D:/Review/[filename]_review.xlsx
========================================
```

### 6. 关键特性

#### ✅ 严格遵守项目编码规范

- 动态读取 `.codebuddy/rules/cpp-qt-coding-standard.md`
- 检查命名规范（类、函数、变量、宏）
- 检查缩进规范（4 个空格，禁止 Tab）
- 检查注释规范（禁止 `//`，必须使用 `/* */`）
- 检查 Qt 信号槽规范（命名、连接方式）
- 检查比较运算符规范（常量在左，变量在右）
- 检查日志规范（按项目变体选用 5.1 或 5.2 节）

#### ✅ 识别五大类缺陷

1. **代码逻辑类缺陷**
   - 函数功能不单一
   - 判断错误
   - 算法问题
   - 代码冗余

2. **内存管理类缺陷**
   - 内存泄漏
   - 使用后释放
   - 资源管理问题

3. **线程安全类缺陷**
   - 竞态条件
   - 缺少互斥锁
   - 锁管理问题

4. **性能表现类缺陷**
   - 效率问题
   - 实现过于复杂
   - 资源竞争

5. **Qt 机制类缺陷**
   - 信号槽连接错误
   - 对象生命周期问题
   - 事件循环阻塞

### 7. 严格约束

#### 禁止事项

❌ 禁止使用其他代码审查 skill（如 `code-review-standards`、`web-code-review`）
❌ 禁止直接修改代码
❌ 禁止跳过编码规范检查
❌ 禁止自动修复代码
❌ 禁止输出非 Excel 格式的报告

#### 必须事项

✅ 必须使用 `cpp-qt-code-reviewer-skill`
✅ 必须生成 Excel 格式报告
✅ 必须报告到默认目录 `D:/Review/`
✅ 必须包含完整的缺陷分类信息
✅ 必须提供具体的修改建议
✅ 必须按项目变体（EZStation / EZTools）选用日志规范

### 8. 参数说明

本命令支持以下可选参数：

```
/cpp-code-review [文件路径] [output=自定义路径] [severity=Major|General|Suggest|All]
```

参数说明：

- `[文件路径]`：要审查的文件路径（必需）
- `output=`：自定义输出路径（可选，默认：`D:/Review/`）
- `severity=`：过滤严重程度（可选，默认：Major）

示例：

```
/cpp-code-review code/Svc/station/src/mc_tcpclientmanager.cpp
/cpp-code-review code/Svc/station/src/mc_tcpclientmanager.cpp output=D:/Custom/
/cpp-code-review code/Svc/station/src/mc_tcpclientmanager.cpp severity=All
```

### 9. 错误处理

- **文件不存在**：提示用户检查路径
- **不支持的文件类型**：提示仅支持 C++/Qt/C 文件
- **技能调用失败**：建议检查技能配置或重试
- **Excel 生成失败**：检查 openpyxl 是否已安装
- **项目变体未识别**：路径既不含 `ezstation` 也不含 `eztools` 时，先询问 Boss

### 10. 工作原理

```
用户输入 → 触发本命令
    ↓
识别项目变体（ezstation / eztools）
    ↓
调用 cpp-qt-code-reviewer-skill
    ↓
读取 .codebuddy/rules/cpp-qt-coding-standard.md 和 references/defect-classification.md
    ↓
按项目变体选用日志规范章节（5.1 / 5.2）
    ↓
执行代码分析
    ↓
调用 xlsx skill 生成报告
    ↓
输出到 D:/Review/[filename]_review.xlsx
    ↓
报告完成
```

---

**注意**：本命令专门用于 EZStation / EZTools 项目的 C++/Qt 代码审查，自动调用 `cpp-qt-code-reviewer-skill`，不会与其他代码审查工具冲突。

$ARGUMENTS
