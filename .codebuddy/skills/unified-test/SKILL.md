---
name: unified-test
description: "通用单元测试主技能。用于为 `.vue` 或 `.go` 文件生成、执行、修复单元测试并提升覆盖率；会根据目标文件自动路由到对应适配器和编排器。用户提到“单元测试/测试用例/覆盖率/修测试/给这个文件补测试”时触发。"
---

# Unified Test — 通用单元测试主技能

## Overview

统一的单元测试入口技能。接收目标文件路径，自动识别语言类型，
选择对应的语言适配器（vue-test-adapter 或 go-test-adapter），
然后调用通用编排器（test-orchestrator）驱动完整的测试流程。

本技能的核心价值是**语言无关的统一调度**——所有语言特定逻辑由适配器封装，
编排逻辑（重试、覆盖率迭代等）完全共享。

## 资源加载规则

### 先按目标文件类型决定适配器

1. `.vue`：读取 `skills/vue-test-adapter.md`
2. `.go`：读取 `skills/go-test-adapter.md`
3. 其他类型：直接返回不支持，不继续加载其他资源

### 再按模式读取编排资源

确定适配器后，再读取：

- `skills/test-orchestrator.md`

只有在需要理解执行失败分类、修复决策或统一结果时，再读取：

- `skills/test-executor-core.md`

### 覆盖率或示例需要时

按需读取：

- `references/coverage-strategies.md`
- `references/vue-test-example.js`
- `references/go-test-example.go`

### 不要怎么加载

1. 不要一开始就把 `skills/` 和 `references/` 全部读入上下文
2. 不要在文件类型尚未确认时加载无关适配器

## 输入参数

参数结构见 `references/type-definitions.md`（`UnifiedTestInput`）——**仅在需要确认字段含义或默认值时读取，不要提前加载**。

核心参数：`targetFile`（必填）、`testFile`（可选）、`mode`（默认 `full`）、`options`（可选配置项）。

## Step 1: 语言识别 & 适配器选择

根据 `targetFile` 的扩展名选择适配器：

| 扩展名 | 适配器 Skill | 测试框架 | 说明 |
|--------|-------------|---------|------|
| `.vue` | `skills/vue-test-adapter.md` | Jest + @vue/test-utils | Vue 单文件组件 |
| `.go` | `skills/go-test-adapter.md` | go test（可选 testify） | Go 函数/方法（自动识别 `go_kit/generic_go`） |
| 其他 | — | — | 提示用户不支持，终止 |

**决策逻辑：**

```
如果 targetFile 以 .vue 结尾：
  → 读取 skills/vue-test-adapter.md
  → adapter = 'vue'

如果 targetFile 以 .go 结尾：
  → 读取 skills/go-test-adapter.md
  → adapter = 'go'

否则：
  → 返回 { status: 'unsupported', message: '当前仅支持 .vue 和 .go 文件' }
  → 终止
```

说明：`.go` 适配器内部会进一步自动识别项目风格（`go_kit` 或 `generic_go`），
并据此选择测试文件路径、执行命令和修复边界。

如果显式传入 `options.goProfile`，则使用**手动强制模式**：

- `goProfile = go_kit`：强制走历史目录约定
- `goProfile = generic_go`：强制走通用 Go 约定
- `goProfile = auto` 或未传：自动识别

## Step 2: 模式确认

| mode | 说明 | 调用范围 |
|------|------|---------|
| `full` | 完整流程（默认） | 生成 → 执行 → 修复 → 覆盖率 → 迭代 |
| `generate` | 仅生成测试 | 只调用 adapter.generate() |
| `execute` | 仅执行测试 | 需要 testFile，执行 → 修复 → 覆盖率 |
| `coverage` | 覆盖率补充 | 需要 testFile，分析未覆盖 → 补充 → 迭代 |

**模式校验：**

- `generate` 模式：必须有 targetFile
- `execute` 模式：必须有 testFile
- `coverage` 模式：必须有 testFile 和 targetFile
- `full` 模式：必须有 targetFile

若模式参数与必需输入不匹配，直接返回 `unsupported` 或 `blocked`，不要继续进入编排器。

## Step 3: 调用通用编排器

将适配器类型和参数传递给 test-orchestrator：

```
读取 skills/test-orchestrator.md

调用编排器：
use_skill({
  command: 'test-orchestrator',
  input: {
    targetFile: targetFile,
    testFile: testFile,
    adapter: selectedAdapter,   // 'vue' 或 'go'
    mode: mode,
    options: {
      maxRetries: options.maxRetries || 2,
      coverageThreshold: options.coverageThreshold || 80,
      maxIterations: options.maxIterations || 5,
      collectCoverage: options.collectCoverage !== false,
      enableModelSwitch: options.enableModelSwitch !== false,
      goProfile: options.goProfile || 'auto'
    }
  }
})
```

## Step 4: 返回统一结果

编排器返回的 `UnifiedTestResult` 直接传递给 Agent，无需额外转换。

结果结构见 `references/type-definitions.md`（`UnifiedTestResult`）——**仅在需要理解结果字段含义时读取**。

## 扩展新语言

新增语言只需 3 步：

1. 创建 `skills/xxx-test-adapter.md`（如 `java-test-adapter.md`）
2. 实现 8 个标准适配器接口方法（见 test-orchestrator.md 中的接口定义）
3. 在本文件 Step 1 的路由表中添加扩展名映射

无需修改编排器（test-orchestrator）和通用核心（test-executor-core）的任何逻辑。

## 技能文件索引

| 文件 | 类型 | 职责 |
|------|------|------|
| `SKILL.md`（本文件） | 主入口 | 语言识别、路由分发 |
| `skills/test-orchestrator.md` | 通用编排器 | 重试、覆盖率、迭代（前后端共享） |
| `skills/test-executor-core.md` | 通用核心 | 错误分类、修复决策、报告生成（前后端共享） |
| `skills/vue-test-adapter.md` | 前端适配器 | Vue/Jest 特有逻辑 |
| `skills/go-test-adapter.md` | 后端适配器 | Go/gotest 特有逻辑（支持 `go_kit/generic_go` 双模式） |
| `references/defect-classification.md` | 参考 | 缺陷分类表 |
| `references/vue-test-example.js` | 参考 | 前端测试样例 |
| `references/go-test-example.go` | 参考 | 后端测试样例 |
| `references/coverage-strategies.md` | 参考 | 覆盖率提升策略 |

## 禁止事项

1. 不要在不支持的文件类型上硬走统一测试流程——强行执行会产生无效测试代码且浪费上下文窗口
2. 不要在未确认模式参数合法时继续进入编排器——参数不匹配会导致编排器在中途失败，已消耗的上下文无法回收
3. 不要一次性加载全部 adapter 和 reference 文件——多语言适配器同时加载会占满上下文窗口，挤压实际测试生成空间
4. 不要把 `README.md` 这类辅助说明当成主执行依据——README 是给人读的概述，不包含适配器接口和编排协议的可执行细节
5. 不要在测试失败时直接修改被测源码来让测试通过——测试的目的是验证行为正确性，改源码适配测试是本末倒置
6. 不要生成只断言"不抛异常"的空壳测试来凑覆盖率——这类测试无法检测回归，给出虚假的安全感
