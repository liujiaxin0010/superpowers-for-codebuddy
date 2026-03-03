---
description: 自定义测试方法论，定义项目专属的单元测试生成规范
---

# 自定义测试方法论

本规则允许 Boss 定义项目专属的单元测试生成方法论。AI 生成测试时**必须严格遵循**本规则中的自定义配置，不得使用 AI 自己"习惯"的测试风格。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

---

## 工作机制

本规则提供两种配置方式：

### 方式一：在本文件中直接定义规则

Boss 在下方的 `## 自定义测试规则` 区域直接编写测试规则。AI 读取后严格遵循。

### 方式二：指定外部规则文件

Boss 在项目中放置一个自定义测试规则文件（如 `docs/test-rules.md` 或 `.codebuddy/test-rules.md`），然后在下方配置路径。AI 在生成测试前先读取该文件。

---

## 自定义测试配置

### 测试框架与工具

```yaml
# Boss 在此定义项目使用的测试框架（取消注释并修改）
# framework: JUnit 5          # Java: JUnit 5 / TestNG / Spock
# framework: pytest            # Python: pytest / unittest
# framework: Jest              # JS/TS: Jest / Vitest / Mocha
# framework: Go testing        # Go: testing / testify
# mock_library: Mockito        # Java: Mockito / PowerMock / EasyMock
# mock_library: pytest-mock    # Python: pytest-mock / unittest.mock
# assertion_style: AssertJ     # Java: AssertJ / Hamcrest / JUnit assert
# coverage_tool: JaCoCo        # 覆盖率工具
# test_runner: Maven Surefire  # 测试运行器
```

### 外部规则文件路径

```yaml
# 如果 Boss 有单独的测试规则文档，在此指定路径
# AI 在生成测试前必须先读取此文件
# external_test_rules: docs/test-rules.md
# external_test_rules: .codebuddy/test-rules.md
```

---

## 自定义测试规则

**Boss 在此区域编写项目专属的测试规则。以下是模板，Boss 可以自由修改：**

<!-- 
======================================================================
Boss：请在这里编写你的自定义测试规则。
AI 生成测试时必须严格遵循。以下是模板示例，请根据项目实际情况修改。
======================================================================
-->

### 测试命名规范

```
# 定义你的测试方法命名规范，例如：
# 方案 A: should_动作_when_条件（BDD 风格）
# 方案 B: test_功能_场景_期望结果
# 方案 C: 方法名_输入状态_期望输出
# 方案 D: given_前置_when_动作_then_结果

# 当前项目使用（Boss 请选择或自定义）：
# naming: should_{action}_when_{condition}
```

### 测试文件组织

```
# 测试文件的存放位置和命名规则，例如：
# 方案 A: 与源码同目录的 __tests__/ 子目录
# 方案 B: 独立的 test/ 或 tests/ 目录，镜像 src/ 结构
# 方案 C: 与源码同目录，文件名加 .test. 或 .spec. 后缀

# 当前项目使用（Boss 请选择或自定义）：
# location: src/__tests__/
# file_naming: {SourceFileName}.test.{ext}
```

### 测试结构模板

```
# 每个测试文件的结构模板，例如：
# - 是否使用 describe/it 嵌套分组
# - 是否使用 setup/teardown
# - 是否使用 AAA 模式（Arrange-Act-Assert）
# - 是否使用 Given-When-Then 模式
# - 是否要求每个 describe 块对应一个公共方法

# 当前项目使用（Boss 请选择或自定义）：
# structure: AAA  # Arrange-Act-Assert
# grouping: describe_per_method  # 每个公共方法一个 describe 块
```

### 覆盖要求

```
# 测试覆盖的最低要求，例如：
# - 每个公共方法至少 N 个测试用例
# - 必须覆盖：正常路径、边界条件、异常路径
# - 分支覆盖率目标
# - 是否需要测试 private 方法（通常不需要）

# 当前项目使用（Boss 请选择或自定义）：
# min_cases_per_method: 3  # 每个公共方法至少3个用例
# required_scenarios: [normal, boundary, error]
# branch_coverage: 80%
# test_private: false
```

### Mock/Stub 策略

```
# 如何使用 Mock 和 Stub，例如：
# - 哪些依赖应该被 mock（外部服务、数据库、文件系统）
# - 哪些依赖不应该被 mock（纯内存工具类）
# - 是否使用 spy 代替 mock
# - 是否使用 test doubles 的命名约定

# 当前项目使用（Boss 请选择或自定义）：
# mock_external: true    # mock 所有外部依赖
# mock_database: true    # mock 数据库层
# mock_utils: false      # 不 mock 工具类
# prefer_spy: false      # 不优先使用 spy
```

### 断言风格

```
# 断言的编写风格，例如：
# - 使用哪个断言库
# - 是否使用流式断言（assertThat().isEqualTo()）
# - 是否在每个测试中只用一个逻辑断言
# - 错误消息是否必须包含业务描述

# 当前项目使用（Boss 请选择或自定义）：
# style: fluent  # assertThat 风格
# one_assert_per_test: false  # 允许多个相关断言
# custom_message: true  # 断言必须包含描述性消息
```

### 项目特殊规则

```
# Boss 在此添加项目特有的测试规则，例如：
# - 特定的数据准备方式（Builder模式、Factory、Fixture文件）
# - 特定的清理策略（@AfterEach、事务回滚）
# - 对特定组件的测试要求（Controller 用 MockMvc、Service 用单元测试）
# - 禁止的做法
# - 强制的做法

# 当前项目特殊规则（Boss 请自定义）：
# [在此编写]
```

---

## AI 的执行纪律

1. **读取配置优先**：生成测试前，必须先读取本文件中的所有自定义配置
2. **如果指定了外部规则文件**，必须先读取外部文件，外部文件的规则优先级高于本文件的默认模板
3. **严格遵循命名规范**：测试方法名必须符合 Boss 定义的命名模式
4. **严格遵循结构模板**：测试文件组织和内部结构必须符合 Boss 的要求
5. **覆盖要求不打折**：每个方法的测试用例数量不得少于 Boss 要求的最低值
6. **Mock 策略不擅改**：按 Boss 的 mock 策略决定哪些依赖需要 mock
7. **不确定就问**：如果 Boss 的配置中有歧义或未覆盖的场景，**必须询问 Boss**

---

## 与 TDD 规则的关系

本规则**不替代** `test-driven-development` 规则，而是**补充**它：

- TDD 规则定义**何时**写测试（先写测试）和**流程**（红-绿-重构）
- 本规则定义**如何**写测试（命名、结构、覆盖、风格）

两者同时生效。AI 必须同时遵循 TDD 流程和本规则中的自定义测试方法论。
