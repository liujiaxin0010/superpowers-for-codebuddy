---
name: unified-test
description: >
  通用单元测试主技能。根据目标文件类型自动路由到对应的语言适配器（.vue → Jest / .go → go test），
  统筹测试生成、执行、修复、覆盖率收集、迭代改进的完整流程。
  当用户需要为 .vue 或 .go 文件编写、运行、修复单元测试或提升覆盖率时触发此技能。
  即使用户只提到"单元测试"、"测试用例"、"覆盖率"等关键词，也应触发此技能。
---

# Unified Test — 通用单元测试主技能

## Overview

统一的单元测试入口技能。接收目标文件路径，自动识别语言类型，
选择对应的语言适配器（vue-test-adapter 或 go-test-adapter），
然后调用通用编排器（test-orchestrator）驱动完整的测试流程。

本技能的核心价值是**语言无关的统一调度**——所有语言特定逻辑由适配器封装，
编排逻辑（重试、覆盖率迭代等）完全共享。

## 输入参数

```typescript
interface UnifiedTestInput {
  targetFile: string;           // 被测文件路径（.vue 或 .go），必填
  testFile?: string;            // 已有测试文件路径（可选）
  mode?: string;                // full | generate | execute | coverage（默认 full）
  options?: {
    maxRetries?: number;        // 最大修复重试次数（默认 2）
    coverageThreshold?: number; // 覆盖率阈值（默认 80）
    maxIterations?: number;     // 最大覆盖率迭代次数（默认 5）
    collectCoverage?: boolean;  // 是否收集覆盖率（默认 true）
    enableModelSwitch?: boolean;// 是否启用模型切换建议（默认 true）
    goProfile?: string;         // Go 项目风格: auto | go_kit | generic_go（默认 auto，仅 .go 生效）
  };
}
```

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

```typescript
interface UnifiedTestResult {
  status: "completed" | "partial" | "failed" | "stalled" | "unsupported";
  message: string;
  summary: {
    targetFile: string;
    testFile: string;
    language: "vue" | "go";
    timestamp: string;
  };
  execution: {
    total: number;
    passed: number;
    failed: number;
    duration?: number;
    success: boolean;
  };
  coverage?: {
    statements?: string;
    branches?: string;
    functions?: string;
    lines?: string;
    meetsThreshold: boolean;
    reportPath?: string;
  };
  fixAttempts: {
    count: number;
    details: Array<{
      round: number;
      failuresCount: number;
      result: string;
    }>;
  };
  iterations?: Array<{
    round: number;
    beforeCoverage: number;
    afterCoverage: number;
    improvement: number;
    newTestsGenerated: number;
  }>;
}
```

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
