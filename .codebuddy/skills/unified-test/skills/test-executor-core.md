---
name: test-executor-core
description: >
  通用测试执行器核心逻辑。包含与语言无关的通用模块：
  错误分类器、修复策略决策器、覆盖率达标判断器、迭代决策器、报告生成器。
  前后端共享这些通用逻辑，语言特定的实现由适配器处理。
---

# Test Executor Core — 通用执行器核心

## Overview

包含前后端共享的执行层通用逻辑，**不涉及任何具体语言实现**。
本模块由编排器（test-orchestrator）在各个阶段中按需调用，
提供错误分析、修复决策、覆盖率判断等公共能力。

## 模块A: 错误分类器 (ErrorClassifier)

### 职责

分析测试失败的错误信息，判断问题根源在于**源码**还是**测试用例**。
这是修复策略的核心决策依据。

### 分类规则

```
输入: failures[] — 失败用例列表，每项包含 { testName, errorType, errorMessage, errorStack }
输出: classifiedFailures[] — 每项增加 { classification, fixStrategy }
```

#### 分类1: 明显的源码错误 (obvious_source_error)

**触发条件**（仅以下 3 种情况才归类为源码错误）：

| 错误特征 | 模式匹配 | 说明 |
|---------|---------|------|
| 变量未定义 | `ReferenceError: (.+) is not defined` | 源码中引用了未声明的变量 |
| 缺少模块导入 | `Error: Cannot find module '(.+)'` | 源码中 import 了不存在的模块 |
| Vue data 属性未声明 | `Property '(.+)' was accessed during render but is not defined` | Vue 组件使用了未在 data 中声明的属性 |

**处理策略**: 需要**用户明确确认**后才修改源码，修改遵循最小修改原则。

#### 分类2: 测试用例问题 (test_code_issue) — 默认分类

**所有不属于分类1的错误，全部归入此类**。包括但不限于：

| 错误特征 | 修复方向 |
|---------|---------|
| 断言不匹配 (`AssertionError`, `expect().toBe()`, `assert.Equal`) | 修改断言的期望值 |
| Mock 返回值错误 | 修改 Mock 配置/返回值 |
| 异步未等待 (`Timeout`, `Promise`, 未完成的异步操作) | 添加 await / flushPromises / $nextTick / time.Sleep |
| 元素未找到 (`Cannot find`, `wrapper.find()`, 选择器问题) | 修改选择器/查找方式 |
| 类型不匹配 (`TypeError`, 参数类型错误) | 修改测试数据类型 |
| 未定义的属性/对象（测试环境 Mock 问题） | 补充 Mock 数据 |
| 运行时错误（测试环境初始化问题） | 修改测试文件的初始化配置 |

**处理策略**: 直接修改测试文件，**绝不修改源码**。

### 分类逻辑伪代码

```javascript
function classifyErrors(failures) {
  return failures.map(failure => {
    const { errorMessage, errorStack } = failure;

    // 检查是否是明显的源码错误（仅 3 种情况）
    const obviousSourcePatterns = [
      /ReferenceError: (.+) is not defined/,
      /Error: Cannot find module '(.+)'/,
      /Property '(.+)' was accessed during render but is not defined/
    ];

    for (const pattern of obviousSourcePatterns) {
      if (pattern.test(errorMessage) || pattern.test(errorStack || '')) {
        return {
          ...failure,
          classification: 'obvious_source_error',
          fixStrategy: 'fix_source_with_user_confirmation'
        };
      }
    }

    // 其他所有情况 → 测试用例问题
    return {
      ...failure,
      classification: 'test_code_issue',
      fixStrategy: 'fix_test_only'
    };
  });
}
```

## 模块B: 修复策略决策器 (FixStrategyDecider)

### 核心原则

**99% 的情况只改测试文件。** 这是前后端统一的最高优先级原则。

### 修复优先级（前后端一致）

| 优先级 | 策略 | 说明 | 适用情况 |
|-------|------|------|---------|
| 1 | 补充/修改 Mock 数据 | 添加缺失的 Mock 配置或修改 Mock 返回值 | Mock 不完整、返回值错误 |
| 2 | 修改断言以匹配实际值 | 调整 expect/assert 的期望值 | 断言与实际结果不一致 |
| 3 | 调整测试数据设置 | 修改测试输入数据、初始状态 | 测试数据不满足前置条件 |
| 4 | 添加异步等待处理 | 添加 await / flush / nextTick / Sleep | 异步操作未完成 |
| 5 | 修改选择器/查找方式 | 更换 CSS 选择器、data-testid、方法名 | 元素未找到 |
| 6 | (极少) 修改源码明显错误 | 仅限变量未定义、缺少导入等 | 需用户确认 |

### "极少修改源码"的决策流程

```
检测到 obvious_source_error
  ↓
生成修改建议（最小修改原则）
  ↓
向用户展示：
  - 问题位置
  - 问题描述
  - 修改建议
  ↓
等待用户确认：
  ├─ 用户同意 → 应用最小修改
  └─ 用户拒绝 → 改为修改测试文件来适配（推荐）
```

## 模块C: 覆盖率达标判断器 (CoverageThresholdChecker)

### 职责

根据覆盖率数据和阈值，判断是否达标。

### 判断逻辑

```javascript
function checkThreshold(coverage, threshold = 80) {
  // coverage 结构:
  // { statements: number, branches: number, functions: number, lines: number }

  const result = {
    meetsThreshold: false,
    details: {},
    primaryMetric: null,     // 主要判断指标
    primaryValue: null,
  };

  // 各维度判断
  if (coverage.statements !== null) {
    result.details.statements = {
      value: coverage.statements,
      meets: coverage.statements >= threshold
    };
  }
  if (coverage.branches !== null) {
    result.details.branches = {
      value: coverage.branches,
      meets: coverage.branches >= threshold
    };
  }
  if (coverage.functions !== null) {
    result.details.functions = {
      value: coverage.functions,
      meets: coverage.functions >= threshold
    };
  }
  if (coverage.lines !== null) {
    result.details.lines = {
      value: coverage.lines,
      meets: coverage.lines >= threshold
    };
  }

  // 达标判断策略:
  // 前端: 以语句覆盖率(statements)为主要指标
  // 后端: 以函数覆盖率为主要指标（go tool cover -func 输出的就是函数覆盖率）
  // 通用规则: 分支覆盖率 >= threshold 视为达标
  //
  // 简化判断: 只要 分支覆盖率 >= threshold 就视为达标
  // 如果没有分支覆盖率数据，则用语句覆盖率或函数覆盖率替代

  if (coverage.branches !== null) {
    result.primaryMetric = 'branches';
    result.primaryValue = coverage.branches;
    result.meetsThreshold = coverage.branches >= threshold;
  } else if (coverage.statements !== null) {
    result.primaryMetric = 'statements';
    result.primaryValue = coverage.statements;
    result.meetsThreshold = coverage.statements >= threshold;
  } else if (coverage.functions !== null) {
    result.primaryMetric = 'functions';
    result.primaryValue = coverage.functions;
    result.meetsThreshold = coverage.functions >= threshold;
  }

  return result;
}
```

### 覆盖率目标参考

| 维度 | 前端目标 | 后端目标 | 说明 |
|------|---------|---------|------|
| 文件/语句覆盖率 | ≥ 80% | — | 前端关注 |
| 分支覆盖率 | ≥ 80% | ≥ 80% | **核心指标，前后端一致** |
| 行覆盖率 | ≥ 100% | — | 前端理想目标 |
| 函数覆盖率 | ≥ 80% | ≥ 80% | 前后端一致 |

## 模块D: 迭代决策器 (IterationDecider)

### 职责

判断覆盖率迭代是否应该继续。

### 决策逻辑

```javascript
function decideIterate(iterationHistory, currentCoverage, options) {
  const { maxIterations, coverageThreshold } = options;
  const currentIteration = iterationHistory.length;

  // 条件1: 已达标
  if (currentCoverage >= coverageThreshold) {
    return { shouldContinue: false, reason: 'threshold_met' };
  }

  // 条件2: 达到最大迭代次数
  if (currentIteration >= maxIterations) {
    return { shouldContinue: false, reason: 'max_iterations_reached' };
  }

  // 条件3: 覆盖率无法继续提升（连续两轮无提升）
  if (currentIteration >= 2) {
    const lastImprovement = iterationHistory[currentIteration - 1].improvement;
    const prevImprovement = iterationHistory[currentIteration - 2].improvement;
    if (Math.abs(lastImprovement) < 0.1 && Math.abs(prevImprovement) < 0.1) {
      return { shouldContinue: false, reason: 'stalled' };
    }
  }

  // 条件4: 上一轮无法生成新测试用例
  if (currentIteration > 0) {
    const lastRound = iterationHistory[currentIteration - 1];
    if (lastRound.newTestsGenerated === 0) {
      return { shouldContinue: false, reason: 'no_new_tests' };
    }
  }

  // 继续迭代
  return { shouldContinue: true, reason: 'continue' };
}
```

### 退出原因说明

| reason | 说明 | 报告状态 |
|--------|------|---------|
| `threshold_met` | 覆盖率已达标 | completed |
| `max_iterations_reached` | 达到最大迭代次数 | partial |
| `stalled` | 连续两轮无提升 | stalled |
| `no_new_tests` | 无法生成新测试用例 | stalled |

## 模块E: 报告生成器 (ReportGenerator)

### 职责

根据编排器的状态数据，生成统一格式的测试报告。

### 报告生成逻辑

```javascript
function buildReport(state) {
  // 确定状态
  let status = 'failed';
  let message = '';

  if (state.executionResult && state.executionResult.allPassed) {
    if (state.coverageResult) {
      const covMeets = state.coverageResult.branches >= state.options.coverageThreshold
                    || state.coverageResult.statements >= state.options.coverageThreshold;
      if (covMeets) {
        status = 'completed';
        message = '所有测试通过，覆盖率达标';
      } else {
        status = 'partial';
        message = `所有测试通过，但覆盖率未达标（${state.coverageResult.branches || state.coverageResult.statements}% < ${state.options.coverageThreshold}%）`;
      }
    } else {
      status = 'completed';
      message = '所有测试通过';
    }
  } else {
    status = 'failed';
    message = `测试失败，经过 ${state.retryCount} 次修复尝试仍有 ${state.executionResult?.failed || 0} 个用例失败`;
  }

  // 构建报告
  return {
    status: status,
    message: message,
    summary: {
      targetFile: state.targetFile,
      testFile: state.testFile,
      language: state.adapter,
      timestamp: new Date().toISOString()
    },
    execution: {
      total: state.executionResult?.total || 0,
      passed: state.executionResult?.passed || 0,
      failed: state.executionResult?.failed || 0,
      success: state.executionResult?.allPassed || false
    },
    coverage: state.coverageResult ? {
      statements: state.coverageResult.statements
        ? `${state.coverageResult.statements.toFixed(2)}%` : null,
      branches: state.coverageResult.branches
        ? `${state.coverageResult.branches.toFixed(2)}%` : null,
      functions: state.coverageResult.functions
        ? `${state.coverageResult.functions.toFixed(2)}%` : null,
      lines: state.coverageResult.lines
        ? `${state.coverageResult.lines.toFixed(2)}%` : null,
      meetsThreshold: status === 'completed',
      reportPath: state.coverageResult.reportPath || null
    } : null,
    fixAttempts: {
      count: state.retryCount,
      details: state.fixHistory
    },
    iterations: state.iterationHistory.length > 0
      ? state.iterationHistory : undefined
  };
}
```

### 报告输出格式

```
╔════════════════════════════════════════════════════════════╗
║                  📊 单元测试最终报告                        ║
╚════════════════════════════════════════════════════════════╝

📁 被测文件:  src/components/xxx/Component.vue
📝 测试文件:  __test__/Component.test.js
🔤 语言类型:  Vue (Jest)
📅 执行时间:  2026-03-02T10:30:00.000Z

━━━━━━━━━━━━━━━━━━ 测试执行结果 ━━━━━━━━━━━━━━━━━━
  总用例数:  25
  通过:      25 ✅
  失败:      0
  修复次数:  1

━━━━━━━━━━━━━━━━━━ 覆盖率报告 ━━━━━━━━━━━━━━━━━━━━
  语句覆盖率: 85.20%  ████████████████████░░░░ 🟢
  分支覆盖率: 82.10%  ████████████████████░░░░ 🟢
  函数覆盖率: 88.00%  █████████████████████░░░ 🟢
  行覆盖率:   85.20%  ████████████████████░░░░ 🟢
  达标情况:   ✅ 达标（≥80%）

━━━━━━━━━━━━━━━━━━ 迭代改进历程 ━━━━━━━━━━━━━━━━━━
  第1轮: 65.00% → 72.30%  +7.30%  (新增3个用例)
  第2轮: 72.30% → 82.10%  +9.80%  (新增2个用例)

🏁 最终状态: completed — 所有测试通过，覆盖率达标
```

### 覆盖率进度条格式化

```javascript
function formatPercentageBar(pct) {
  if (pct === null) return 'N/A';
  const percentage = Math.round(pct * 100) / 100;
  const barLength = Math.floor(percentage / 2);
  const bar = '█'.repeat(barLength) + '░'.repeat(50 - barLength);
  const color = percentage >= 80 ? '🟢' : percentage >= 60 ? '🟡' : '🔴';
  return `${percentage.toFixed(2)}% ${bar} ${color}`;
}
```
