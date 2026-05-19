# Code Analysis Guide for C++/Qt Code Review

This guide provides systematic approach for analyzing C++ and Qt code to identify defects.

## Analysis Approach

### 1. Read and Understand the Code

First, thoroughly read the target file to understand:
- The class/module's purpose and functionality
- Data flow and memory management
- Qt-specific mechanisms (signals/slots, object tree, event loop)
- Threading model and synchronization
- Dependencies and external calls

### 2. Identify Potential Issues by Category

#### A. Code Logic Issues (代码逻辑类)

**Common patterns to look for:**

**Function/Method Issues:**
- Functions that do too many things (violates single responsibility principle)
- Missing or incorrect return statements
- Unhandled edge cases
- Incorrect condition logic
- Missing null pointer checks
- Inconsistent error handling

**Control Flow Issues:**
- Missing branches in if/else statements
- Incorrect loop boundaries
- Unreachable code
- Improper use of switch/case without default

**Common defect mappings:**
- `编码 | 函数、模块接口_编码 | 函数功能不单一` - Functions doing multiple things
- `编码 | 函数、模块接口_编码 | 返回值处理、return` - Missing/incorrect return handling
- `编码 | 函数、模块接口_编码 | 代码冗余、逻辑不合理` - Redundant or illogical code
- `详细设计 | 条件、分支、循环 | 判断错误` - Incorrect condition logic
- `详细设计 | 程序结构 | 算法问题` - Algorithmic issues

#### B. Memory Management Issues (内存管理类缺陷)

**Check for:**
- Memory leaks (new without delete, malloc without free)
- Use after free / dangling pointers
- Buffer overflows
- Double free
- Mismatched new/delete (new[] vs delete[])
- Smart pointer misuse (shared_ptr circular references)

**Common defect mappings:**
- `编码 | 资源类 | 内存、fd、句柄、锁管理` - Memory leaks
- `详细设计 | 资源使用问题 | 内存_资源使用问题` - Resource management issues
- `概要设计 | 系统资源问题 | 内存_系统资源问题` - System resource issues

#### C. Thread Safety Issues (线程安全类缺陷)

**Check for:**
- Race conditions on shared data
- Missing mutex locks
- Deadlock risks (lock ordering)
- Thread-unsafe Qt GUI operations
- Improper QThread usage

**Common defect mappings:**
- `编码 | 资源类 | 内存、fd、句柄、锁管理` - Lock management issues
- `详细设计 | 资源使用问题 | 信号量_资源使用问题` - Semaphore issues
- `概要设计 | 系统资源问题 | 任务_系统资源问题` - Task/thread issues

#### D. Performance Issues (性能表现类缺陷)

**Check for:**
- Unnecessary memory copies
- Inefficient algorithms (O(n²) where O(n) possible)
- Frequent dynamic memory allocation in loops
- Resource contention
- Blocking operations in main thread

**Common defect mappings:**
- `概要设计 | 软件效率性能` - Performance issues
- `详细设计 | 程序结构 | 实现过于复杂` - Overly complex implementations
- `详细设计 | 程序结构 | 算法问题` - Algorithmic issues

#### E. Qt Mechanism Issues (Qt机制类缺陷)

**Check for:**
- Incorrect signal/slot connections
- Missing parent for QObject (memory management)
- Direct GUI access from non-GUI threads
- Blocking event loop (long-running operations in main thread)
- Improper QThread subclassing vs worker object pattern

**Common defect mappings:**
- `编码 | 函数、模块接口_编码 | 代码冗余、逻辑不合理` - Qt pattern misuse
- `详细设计 | 函数、模块接口_详细设计 | 子函数调用问题` - Signal/slot issues
- `编码 | 资源类 | 内存、fd、句柄、锁管理` - QObject lifecycle issues

### 3. Determine Severity

**Major (严重) - Report these:**
- Memory leaks or corruption
- Security vulnerabilities (buffer overflow, injection)
- Critical functionality broken
- Thread safety issues causing crashes
- Data loss or corruption risk
- Qt GUI crashes from wrong thread

**General (一般) - Only report if requested:**
- Code quality issues
- Minor performance problems
- Inconsistent patterns
- Poor maintainability

**Suggest (建议) - Only report if requested:**
- Best practice improvements
- Code style suggestions
- Minor optimizations

### 4. Create Defect Records

For each Major defect found, create a record with:

```
{
  reviewer: "x08666",
  description: "问题描述。修改建议：[具体修改建议]",
  location: "文件名:行号",
  module: "完整文件路径",
  severity: "Major",
  source: "从缺陷分类表中选择",
  type: "从缺陷分类表中选择",
  subtype: "从缺陷分类表中选择",
  category: "代码逻辑类/内存管理类缺陷/线程安全类缺陷/性能表现类缺陷/Qt机制类缺陷"
}
```

**Description Format:**
- First, clearly describe the problem
- Second, provide specific, actionable improvement suggestions
- Do NOT include hyperlinks to methods or files
- Be specific about what needs to change

**Location Format:**
- Must be exact: `filename:lineNumber`
- Line numbers from original file (no compression)
- Example: `mainwindow.cpp:45`

### 5. Examples

#### Example 1: Memory Leak

**Code:**
```cpp
void processData() {
    char* buffer = new char[1024];
    // use buffer...
    // missing delete[]
}
```

```javascript
{
  reviewer: "x08666",
  description: "函数中存在内存泄漏。使用new分配的内存未释放。修改建议：添加delete[] buffer;释放内存，或改用std::vector<char>或std::unique_ptr<char[]>自动管理内存。",
  location: "utils.cpp:45",
  module: "d:/pro/project/src/utils.cpp",
  severity: "Major",
  source: "编码",
  type: "资源类",
  subtype: "内存、fd、句柄、锁管理",
  category: "内存管理类缺陷"
}
```

#### Example 2: Qt Thread Safety Issue

**Code:**
```cpp
void WorkerThread::run() {
    // Running in separate thread
    ui->label->setText("Processing...");  // Wrong! GUI access from non-GUI thread
}
```

**Defect Record:**
```javascript
{
  reviewer: "x08666",
  description: "在非GUI线程中直接访问UI控件，会导致程序崩溃或不稳定行为。修改建议：使用信号槽机制跨线程通信，或通过QMetaObject::invokeMethod在主线程中执行UI更新操作。",
  location: "worker.cpp:23",
  module: "d:/pro/project/src/worker.cpp",
  severity: "Major",
  source: "编码",
  type: "函数、模块接口_编码",
  subtype: "代码冗余、逻辑不合理",
  category: "Qt机制类缺陷"
}
```

#### Example 3: Missing Null Check

**Code:**
```cpp
void processNode(TreeNode* node) {
    int value = node->data;  // No null check
    // ...
}
```

**Defect Record:**
```javascript
{
  reviewer: "x08666",
  description: "函数缺少空指针检查。当node为nullptr时，会导致程序崩溃。修改建议：在访问node成员前添加if (node == nullptr)检查，并适当处理错误情况。",
  location: "tree.cpp:56",
  module: "d:/pro/project/src/tree.cpp",
  severity: "Major",
  source: "编码",
  type: "函数、模块接口_编码",
  subtype: "形参和实参类型匹配、参数说明及校验",
  category: "代码逻辑类"
}
```
#### Example 4: Buffer Overflow Risk

**Code:**
```cpp
void copyString(const char* src) {
    char dest[10];
    strcpy(dest, src);  // Risk of buffer overflow
}
```

**Defect Record:**
```javascript
{
  reviewer: "x08666",
  description: "使用strcpy存在缓冲区溢出风险，当src长度超过dest容量时会导致内存损坏。修改建议：改用strncpy(dest, src, sizeof(dest)-1)并确保dest以null结尾，或使用std::string替代C风格字符串。",
  location: "stringutils.cpp:34",
  module: "d:/pro/project/src/stringutils.cpp",
  severity: "Major",
  source: "编码",
  type: "常量、变量使用",
  subtype: "大小、初始化、变量访问",
  category: "内存管理类缺陷"
}
```

## Review Checklist

Use this checklist during code review:

- [ ] Are all pointers checked for null before dereferencing?
- [ ] Is every new/malloc matched with delete/free?
- [ ] Are smart pointers used appropriately?
- [ ] Are buffer operations bounded to prevent overflow?
- [ ] Are shared resources protected by locks in multi-threaded code?
- [ ] Is GUI only accessed from the main thread?
- [ ] Are signal/slot connections correct and appropriate?
- [ ] Are QObject parent-child relationships properly set?
- [ ] Are return statements present in all code paths?
- [ ] Are all error conditions handled?
- [ ] Is there potential for memory leaks in exception paths?
- [ ] Are thread synchronization primitives used correctly?
- [ ] Is the event loop blocked by long-running operations?

## Best Practices

1. **Be thorough**: Check every function, method, and class
2. **Be specific**: Provide exact line numbers and clear suggestions
3. **Be consistent**: Use the same classification criteria for all reviews
4. **Be constructive**: Focus on actionable improvements
5. **Be accurate**: Only report actual defects, not style preferences unless they cause real issues
