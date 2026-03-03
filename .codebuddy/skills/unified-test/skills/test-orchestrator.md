---
name: test-orchestrator
description: >
  通用测试编排器。统筹协调测试的完整流程：生成→执行→分析→修复→覆盖率→迭代。
  前后端共享同一套重试逻辑、覆盖率检查和迭代改进策略。
  不包含任何语言特定逻辑，所有差异由适配器（vue-test-adapter / go-test-adapter）处理。
---

# Test Orchestrator — 通用测试编排器

## Overview

前后端共享的编排层。本模块是整个测试框架的"指挥中心"，负责统筹协调测试的完整生命周期。
它**不涉及任何语言特定逻辑**——所有与 Vue/Jest 或 Go/gotest 相关的操作，
都通过统一的适配器接口委托给对应的语言适配器执行。

## 核心原则（前后端一致）

| # | 原则 | 说明 |
|---|------|------|
| 1 | 不改业务代码 | 修复永远优先改测试文件，极端情况（变量未定义、缺少导入等明显错误）需用户确认 |
| 2 | 覆盖率 ≥ 80% | 达标即终止，不过度优化 |
| 3 | 迭代改进 | 未达标时分析未覆盖代码→补充用例→重跑，循环改进 |
| 4 | 自动清理 | 流程结束时清理所有临时文件 |
| 5 | 可执行优先 | 确保生成的代码能正常运行为第一优先级 |

## 工作流程决策树

```
开始
  ↓
接收参数（targetFile, adapter, mode, options）
  ↓
初始化状态 orchestratorState
  ↓
判断 mode：
  ├─ generate → 只执行阶段A → 返回生成结果
  ├─ execute  → 只执行阶段B+C+D → 返回执行结果
  ├─ coverage → 只执行阶段C+D → 返回覆盖率结果
  └─ full     → 执行阶段A+B+C+D+E
  ↓
【阶段A: 测试生成】
  ↓ 调用 adapter.generate(targetFile)
  ↓ 得到 testFile
  ↓
【阶段B: 执行-修复循环】（最多 maxRetries + 1 次）
  ↓ 调用 adapter.execute(testFile, collectCoverage=false)
  ↓ 调用 adapter.parseResult(rawOutput)
  ↓ 所有测试通过？
  ├─ 是 → 进入阶段C
  └─ 否 → 调用 executor-core.classifyErrors(failures)
          → 调用 adapter.fix(testFile, failures)
          → retryCount++
          → 达到上限？
          ├─ 是 → enableModelSwitch? → 建议切换 / 返回失败报告
          └─ 否 → 重新执行（循环回阶段B顶部）
  ↓
【阶段C: 覆盖率收集】（如果 collectCoverage = true）
  ↓ 调用 adapter.execute(testFile, collectCoverage=true)
  ↓ 调用 adapter.collectCoverage(testFile)
  ↓ 调用 executor-core.checkThreshold(coverage, threshold)
  ↓ 达标？
  ├─ 是 → 进入阶段E（成功）
  └─ 否 → 进入阶段D
  ↓
【阶段D: 覆盖率迭代】（最多 maxIterations 轮）
  ↓ 调用 adapter.analyzeUncovered(testFile, targetFile)
  ↓ 有未覆盖代码？
  ├─ 否 → 退出迭代，进入阶段E
  └─ 是 → 调用 adapter.generateSupplementary(uncoveredInfo)
          → 将新用例追加到测试文件
          → 调用 adapter.execute(testFile, collectCoverage=false)
          → 调用 adapter.parseResult → 有失败？→ adapter.fix → 重新执行
          → 调用 adapter.execute(testFile, collectCoverage=true)
          → 调用 adapter.collectCoverage
          → 调用 executor-core.checkThreshold
          → 达标？
          ├─ 是 → 退出迭代，进入阶段E（成功）
          └─ 否 → 调用 executor-core.decideIterate
                  ├─ 继续 → iterationCount++ → 循环
                  └─ 停止（无提升/达到上限）→ 退出迭代
  ↓
【阶段E: 清理 & 报告】
  ↓ 调用 adapter.cleanup()
  ↓ 调用 executor-core.buildReport(state)
  ↓ 返回 UnifiedTestResult
```

## 状态管理

```javascript
const orchestratorState = {
  // 输入参数
  targetFile: null,           // 被测文件路径
  testFile: null,             // 测试文件路径
  adapter: null,              // 'vue' | 'go'
  mode: 'full',               // 'full' | 'generate' | 'execute' | 'coverage'

  // 配置选项
  options: {
    maxRetries: 2,
    coverageThreshold: 80,
    maxIterations: 5,
    collectCoverage: true,
    enableModelSwitch: true,
    goProfile: 'auto',          // 仅 adapter='go' 生效: auto | go_kit | generic_go
  },

  // 执行状态
  phase: 'init',              // 'init' | 'generate' | 'execute' | 'coverage' | 'iterate' | 'cleanup'
  retryCount: 0,              // 当前修复重试次数
  iterationCount: 0,          // 当前覆盖率迭代次数

  // 结果数据
  executionResult: null,      // { total, passed, failed, failures[] }
  coverageResult: null,       // { statements, branches, functions, lines }
  iterationHistory: [],       // [{ round, beforeCov, afterCov, improvement, newTests }]
  fixHistory: [],             // [{ round, failuresCount, fixedCount }]
};
```

## 退出条件

| 条件 | 退出状态 | 说明 |
|------|---------|------|
| 全部通过 + 覆盖率达标 | `completed` | 完全成功 ✅ |
| 全部通过 + 覆盖率未达标但已尽力 | `partial` | 建议手动补充 |
| 修复失败达到上限 | `failed` | 建议模型切换或人工介入 |
| 覆盖率无法继续提升 | `stalled` | 已达到当前可达的最大覆盖率 |

## 与适配器的交互接口

编排器通过以下 **8 个统一接口** 与适配器交互。
每个接口在前端（vue-test-adapter）和后端（go-test-adapter）中有各自的实现：

### 接口定义

```typescript
interface TestAdapter {
  /**
   * 生成测试文件
   * @param targetFile 被测源文件路径
   * @returns 生成的测试文件路径
   */
  generate(targetFile: string): string;

  /**
   * 执行测试
   * @param testFile 测试文件路径
   * @param collectCoverage 是否收集覆盖率
   * @returns 原始测试输出
   */
  execute(testFile: string, collectCoverage?: boolean): string;

  /**
   * 解析测试输出
   * @param rawOutput 原始测试输出
   * @returns 结构化的测试结果
   */
  parseResult(rawOutput: string): TestResult;

  /**
   * 修复失败的测试用例
   * @param testFile 测试文件路径
   * @param failures 失败用例列表
   * @returns 是否修复成功
   */
  fix(testFile: string, failures: TestFailure[]): boolean;

  /**
   * 收集覆盖率
   * @param testFile 测试文件路径
   * @returns 覆盖率数据
   */
  collectCoverage(testFile: string): CoverageResult;

  /**
   * 分析未覆盖的代码
   * @param testFile 测试文件路径
   * @param targetFile 被测源文件路径
   * @returns 未覆盖代码信息
   */
  analyzeUncovered(testFile: string, targetFile: string): UncoveredInfo;

  /**
   * 生成补充测试用例
   * @param uncoveredInfo 未覆盖代码信息
   * @returns 新生成的测试用例列表
   */
  generateSupplementary(uncoveredInfo: UncoveredInfo): TestCase[];

  /**
   * 清理临时文件
   */
  cleanup(): void;
}
```

适配器可读取编排器 `options` 中的适配器专属参数。
当前已约定：`options.goProfile`（仅 Go 适配器使用）用于手动强制 profile。

### 接口实现对照

| 接口方法 | 前端适配器 (Vue) | 后端适配器 (Go) |
|---------|----------------|----------------|
| `generate()` | 解析 Vue SFC → Jest describe/test | 解析 Go 函数 → 表驱动 []struct |
| `execute()` | `powershell npm test --testPathPattern` | `go test -coverprofile -coverpkg` |
| `parseResult()` | 匹配 `Tests: X passed, Y failed` | 匹配 `ok` / `FAIL` / `--- FAIL` |
| `fix()` | 修改 Jest Mock/断言/选择器 | 修改 Mock.On()/assert.Equal |
| `collectCoverage()` | 读取 Istanbul lcov-report HTML | `go tool cover -func` / `-html` |
| `analyzeUncovered()` | 正则提取未测试的 methods | 解析 coverage.html 中 cov0 |
| `generateSupplementary()` | 生成 Jest test() 用例 | 生成 Go 表驱动测试项 |
| `cleanup()` | 删除 test_output.txt 等 | 删除 coverage.out/.html |

## 阶段详细逻辑

### 阶段A: 测试生成

```
输入: targetFile
输出: testFile

步骤:
1. 打印日志: "📝 阶段A: 生成测试文件..."
2. 调用 adapter.generate(targetFile)
3. 记录 state.testFile = 返回的测试文件路径
4. 打印日志: "✅ 测试文件生成完成: {testFile}"
```

### 阶段B: 执行-修复循环

```
输入: testFile
输出: executionResult (所有通过) 或 failureReport

步骤:
while (state.retryCount <= options.maxRetries):
  1. 打印日志: "🧪 第 {retryCount+1} 次测试执行..."
  2. rawOutput = adapter.execute(testFile, collectCoverage=false)
  3. result = adapter.parseResult(rawOutput)
  4. state.executionResult = result
  
  5. 如果 result.allPassed:
       打印: "🎉 所有 {result.total} 个测试通过！"
       退出循环
     
  6. 否则:
       打印: "⚠️ {result.failed} 个用例失败"
       
       // 读取 test-executor-core.md 进行错误分类
       分类结果 = executor-core.classifyErrors(result.failures)
       
       // 调用适配器修复
       fixed = adapter.fix(testFile, result.failures)
       
       // 记录修复历史
       state.fixHistory.push({
         round: state.retryCount + 1,
         failuresCount: result.failed,
         fixedCount: fixed ? result.failed : 0
       })
       
       state.retryCount++

如果循环结束仍有失败:
  如果 options.enableModelSwitch:
    返回模型切换建议
  否则:
    返回失败报告
```

### 阶段C: 覆盖率收集

```
输入: testFile（所有测试已通过）
输出: coverageResult

步骤:
1. 如果 options.collectCoverage == false:
     跳过，直接进入阶段E
     
2. 打印日志: "📊 阶段C: 收集覆盖率..."
3. rawOutput = adapter.execute(testFile, collectCoverage=true)
4. coverage = adapter.collectCoverage(testFile)
5. state.coverageResult = coverage

6. 读取 test-executor-core.md 进行达标检查:
   thresholdResult = executor-core.checkThreshold(coverage, options.coverageThreshold)

7. 打印覆盖率详情:
   "  语句覆盖率: {coverage.statements}%"
   "  分支覆盖率: {coverage.branches}%"
   "  函数覆盖率: {coverage.functions}%"
   "  行覆盖率:   {coverage.lines}%"
   "  达标情况:   {达标 ? '✅ 达标' : '❌ 未达标'}"

8. 如果达标:
     打印: "🎉 覆盖率达标！"
     进入阶段E
   否则:
     打印: "⚠️ 覆盖率未达标，进入迭代改进..."
     进入阶段D
```

### 阶段D: 覆盖率迭代

```
输入: testFile, targetFile, 当前覆盖率
输出: 更新后的 coverageResult

步骤:
while (state.iterationCount < options.maxIterations):
  1. 打印日志: "🔄 覆盖率迭代 第 {iterationCount+1}/{maxIterations} 轮"
  
  // 记录迭代前覆盖率
  2. beforeCov = state.coverageResult.branches (或 statements)
  
  // 分析未覆盖代码
  3. uncoveredInfo = adapter.analyzeUncovered(testFile, targetFile)
  4. 如果没有可分析的未覆盖代码:
       打印: "✅ 所有可覆盖代码已覆盖"
       退出循环
  
  // 生成补充测试
  5. newCases = adapter.generateSupplementary(uncoveredInfo)
  6. 如果 newCases 为空:
       打印: "⚠️ 无法生成新测试用例"
       退出循环
  
  // 追加到测试文件并执行
  7. 将 newCases 追加到测试文件
  8. rawOutput = adapter.execute(testFile, collectCoverage=false)
  9. result = adapter.parseResult(rawOutput)
  
  // 如果新增用例有失败，先修复
  10. 如果 result.failed > 0:
        adapter.fix(testFile, result.failures)
        重新执行直到通过
  
  // 收集新覆盖率
  11. adapter.execute(testFile, collectCoverage=true)
  12. newCoverage = adapter.collectCoverage(testFile)
  13. afterCov = newCoverage.branches (或 statements)
  14. improvement = afterCov - beforeCov
  
  // 记录迭代结果
  15. state.iterationHistory.push({
        round: state.iterationCount + 1,
        beforeCoverage: beforeCov,
        afterCoverage: afterCov,
        improvement: improvement,
        newTestsGenerated: newCases.length
      })
  
  // 打印迭代结果
  16. "  迭代前: {beforeCov}%  →  迭代后: {afterCov}%  提升: {improvement}%"
  
  // 检查是否达标
  17. 如果 afterCov >= options.coverageThreshold:
        打印: "🎉 覆盖率达标！"
        state.coverageResult = newCoverage
        退出循环
  
  // 检查是否有提升
  18. 读取 executor-core.decideIterate:
      如果 improvement < 0.1:
        打印: "⚠️ 覆盖率无法继续提升，提前退出"
        退出循环
  
  19. state.coverageResult = newCoverage
  20. state.iterationCount++
```

### 阶段E: 清理 & 报告

```
步骤:
1. 调用 adapter.cleanup() 清理临时文件
2. 调用 executor-core.buildReport(state) 生成报告
3. 返回 UnifiedTestResult
```

## 完整使用示例

### 示例1: 前端 Vue 组件完整测试

```javascript
// 输入
{
  targetFile: "src/components/systemComponent/dataExchangeConfig.vue",
  adapter: "vue",
  mode: "full",
  options: {
    maxRetries: 2,
    coverageThreshold: 80,
    maxIterations: 5,
    collectCoverage: true
  }
}

// 流程
// 阶段A → 生成 __test__/dataExchangeConfig.test.js
// 阶段B → 执行 Jest → 3个失败 → 修复 → 重新执行 → 全部通过
// 阶段C → 收集覆盖率 → 65% → 未达标
// 阶段D → 迭代1: 65%→72% → 迭代2: 72%→81% → 达标！
// 阶段E → 清理 → 返回 completed 报告
```

### 示例2: 后端 Go 函数完整测试

```javascript
// 输入
{
  targetFile: "code/src/parking_lot/service/parkService.go",
  adapter: "go",
  mode: "full",
  options: {
    maxRetries: 2,
    coverageThreshold: 80,
    maxIterations: 5,
    collectCoverage: true,
    goProfile: "auto" // 可强制: "go_kit" | "generic_go"
  }
}

// 流程
// 阶段A → 生成 code/src/mock_test/parking_lot_mock/addPark_test.go
// 阶段B → 执行 go test → 通过
// 阶段C → go tool cover → 55% → 未达标
// 阶段D → 分析 cov0 → 补充错误分支用例 → 迭代至 82% → 达标！
// 阶段E → 清理 coverage.out → 返回 completed 报告
```

### 示例3: 仅提升覆盖率

```javascript
// 输入
{
  targetFile: "src/components/xxx/Component.vue",
  testFile: "__test__/Component.test.js",
  adapter: "vue",
  mode: "coverage",
  options: { coverageThreshold: 80, maxIterations: 5 }
}

// 流程：跳过阶段A和B，直接进入阶段C+D
```
