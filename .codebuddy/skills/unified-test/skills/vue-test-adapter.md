---
name: vue-test-adapter
description: >
  Vue/Jest 前端测试适配器。实现通用测试接口的前端版本，
  包括 Vue SFC 解析、Jest 测试用例生成、Mock 配置（ComScript/UI组件/$t/$confirm/Vuex）、
  Istanbul 覆盖率解析、未覆盖代码分析等前端特有逻辑。
  整合了原 test-generator 和 test-executor 中的前端部分。
---

# Vue Test Adapter — 前端测试适配器

## Overview

实现通用编排器（test-orchestrator）定义的 8 个适配器接口，
处理所有 Vue + Jest 相关的特有逻辑。

本适配器整合了以下原始文档的前端部分：
- **test-generator**：测试用例生成（→ `generate()` 方法）
- **test-executor**：测试执行、结果解析、修复、覆盖率收集（→ 其他方法）
- **Web单元测试专家**：命令执行规范、报告格式

## 覆盖率要求

| 维度 | 目标 |
|------|------|
| 文件覆盖率 | ≥ 80% |
| 分支覆盖率 | ≥ 80% |
| 行覆盖率 | ≥ 100%（理想） |
| 函数覆盖率 | ≥ 80% |

---

## 接口实现

### 1. generate(targetFile) → testFile

**将原 test-generator 的全部逻辑封装于此。**

#### 输入/输出

- **输入**: Vue 组件文件路径，如 `src/components/systemComponent/dataExchangeConfig.vue`
- **输出**: 生成的 Jest 测试文件路径，如 `__test__/dataExchangeConfig.test.js`

#### 前置校验

- 文件扩展名必须是 `.vue`
- 文件必须位于 `src/` 目录下

#### 生成流程

##### Step 1: 解析 Vue 组件结构

使用 `@vue/compiler-sfc` 解析单文件组件：

```javascript
const { descriptor } = parseComponent(componentContent);
const scriptContent = descriptor.script?.content || descriptor.scriptSetup?.content;
```

使用 Babel AST 分析提取组件信息：

```javascript
const componentInfo = {
  name: extractComponentName(ast),
  props: extractProps(ast),           // 属性定义
  methods: extractMethods(ast),       // 方法列表
  events: extractEvents(ast),         // 事件（$emit）
  computed: extractComputed(ast),     // 计算属性
  data: extractData(ast),             // 响应式数据
  dependencies: extractDependencies(ast)  // 组件依赖
};
```

##### Step 2: 识别组件依赖

| 依赖类型 | 识别方式 | Mock 方式 |
|---------|---------|----------|
| UI 组件库（UButton/UForm 等） | import from 'u-xxx' | 从 `TestMock/UI.js` 导入 |
| 业务子组件 | import from '@/components/...' | 在测试文件中创建简单 render mock |
| 第三方库 | import from 'xxx' | jest.mock('xxx') |

##### Step 3: 生成文件头部

```javascript
// __test__/componentName.test.js
// 源文件: src/components/xxx/ComponentName.vue
import { mount, shallowMount, createLocalVue } from "@vue/test-utils";
import ComponentName from "@/components/xxx/ComponentName.vue";
import Vuex from "vuex";
import flushPromises from "flush-promises";

// 引入UI组件mock
import {
  UButton, UDialog, UForm, UTable, UTableColumn, UPagination,
  UTooltip, USwitch, UTimePicker, UOption, USelect, UInput
} from "@/TestMock/UI.js";

const localVue = createLocalVue();
localVue.use(Vuex);
```

##### Step 4: 生成 Mock 配置

**全局对象 Mock：**

```javascript
// Mock ComScript
const mockComScript = {
  STATUSCODE: { success: 0 },
  MSGType: { SUCCEED: "success", FAIL: "error" },
};
global.ComScript = mockComScript;

// Mock $t函数（国际化）
const mock$t = (key) => key;

// Mock $confirm（确认框）
const mock$confirm = jest.fn().mockResolvedValue(true);
```

**业务子组件 Mock：**

```javascript
const BusinessSubComponent = {
  name: "BusinessSubComponent",
  render(h) { return h("div", this.$slots.default); }
};
```

**注册组件：**

```javascript
localVue.component("u-button", UButton);
localVue.component("u-form", UForm);
localVue.component("business-sub-component", BusinessSubComponent);
```

##### Step 5: 生成 createWrapper 辅助函数

```javascript
const createWrapper = (options = {}) => {
  const mockActions = {
    someAction: jest.fn().mockResolvedValue({ data: {} })
  };
  const store = new Vuex.Store({
    state: { /* 根据组件需要设置 */ },
    actions: mockActions
  });
  return shallowMount(ComponentName, {
    localVue,
    store,
    mocks: {
      ComScript: mockComScript,
      $t: key => key,
      $confirm: jest.fn().mockResolvedValue(true),
      ...options.mocks
    }
  });
};
```

##### Step 6: 生成测试用例

```javascript
describe("组件中文名称", () => {
  let wrapper;

  beforeEach(() => {
    jest.clearAllMocks();
    wrapper = createWrapper();
  });

  afterEach(() => {
    if (wrapper) wrapper.destroy();
  });

  describe("组件基本渲染", () => {
    test("应该正确渲染组件", () => {
      expect(wrapper.exists()).toBe(true);
    });
  });

  describe("方法功能", () => {
    test("应该正确初始化", async () => {
      await wrapper.vm.init();
      expect(wrapper.vm.someData).toBeDefined();
    });
  });

  describe("事件功能", () => {
    test("应该触发事件", () => {
      wrapper.vm.$emit('eventName', payload);
      expect(wrapper.emitted('eventName')).toBeTruthy();
    });
  });

  describe("边界条件", () => {
    test("应该处理空数据", async () => {
      await wrapper.setData({ someArray: [] });
      await wrapper.vm.$nextTick();
      expect(wrapper.exists()).toBe(true);
    });
  });
});
```

##### Step 7: 检查并更新 TestMock/UI.js

如果组件使用了未在 `TestMock/UI.js` 中定义的 UI 组件，自动追加：

```javascript
export const UNewComponent = {
  name: "UNewComponent",
  props: ["value", "disabled", "placeholder"],
  render(h) {
    const attrs = {};
    if (this.$props) {
      Object.keys(this.$props).forEach(key => { attrs[key] = this.$props[key]; });
    }
    return h("div", { attrs, on: this.$listeners }, this.$slots.default);
  }
};
```

#### 命名规范

| 层级 | 格式 | 示例 |
|------|------|------|
| 测试套件 | 中文组件名 | `describe("人脸识别导入组件", ...)` |
| 测试分组 | 功能分类 | `describe("组件基本渲染", ...)` |
| 测试用例 | 中文描述 | `test("应该正确渲染组件", ...)` |

#### 输出路径

统一放在项目根目录的 `__test__` 文件夹下：
- `src/components/xxx/ComponentName.vue` → `__test__/ComponentName.test.js`

---

### 2. execute(testFile, collectCoverage?) → rawOutput

#### 命令格式（PowerShell + UTF-8）

**所有执行单元测试的命令都必须使用以下格式：**

```powershell
powershell -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; npm test -- --testPathPattern=${testFileName} ${coverageFlag} 2>&1 > ${outputFile}; Get-Content ${outputFile}"
```

| 参数 | 说明 |
|------|------|
| `testFileName` | 测试文件名（从路径中提取），如 `dataExchangeConfig.test.js` |
| `coverageFlag` | `collectCoverage=true` 时为空；`false` 时为 `--no-coverage` |
| `outputFile` | `collectCoverage=true` → `test_coverage_output.txt`；`false` → `test_output.txt` |

#### 注意事项

- 必须设置 UTF-8 输出编码以避免中文乱码
- 使用 `2>&1` 将错误输出重定向到标准输出
- 使用 `>` 将所有输出保存到指定文件

---

### 3. parseResult(rawOutput) → TestResult

#### 解析逻辑

```javascript
function parseJestOutput(rawOutput) {
  const lines = rawOutput.split('\n');
  let totalTests = 0, passedTests = 0, failedTests = 0;
  const failedTestCases = [];

  for (const line of lines) {
    // 匹配 Jest 标准输出
    const allPassMatch = line.match(/Tests:\s*(\d+)\s*passed,\s*(\d+)\s*total/);
    if (allPassMatch) {
      passedTests = parseInt(allPassMatch[1]);
      totalTests = parseInt(allPassMatch[2]);
    }

    const failMatch = line.match(/Tests:\s*(\d+)\s*failed,\s*(\d+)\s*passed,\s*(\d+)\s*total/);
    if (failMatch) {
      failedTests = parseInt(failMatch[1]);
      passedTests = parseInt(failMatch[2]);
      totalTests = parseInt(failMatch[3]);
    }
  }

  // AI 智能提取失败用例详情（套件、名称、错误类型、错误信息、堆栈）
  // 匹配 ● TestSuiteName > test case name 格式

  return {
    totalTests,
    passedTests,
    failedTests,
    failedTestCases,
    allPassed: failedTests === 0
  };
}
```

---

### 4. fix(testFile, failures) → boolean

#### 修复原则

**只修改测试文件 (.test.js)，绝不修改组件代码 (.vue)**

#### 修复方式

| 错误类型 | 修复方式 |
|---------|---------|
| Mock 不完整 | 添加必要的 `jest.fn()` / `mockResolvedValue` |
| 断言不匹配 | 修改 `expect().toBe()` 的期望值 |
| 异步未等待 | 添加 `await flushPromises()` / `await wrapper.vm.$nextTick()` |
| 元素未找到 | 修改 CSS 选择器 / 使用 `data-testid` |
| 数据未初始化 | 在 `beforeEach` 或测试开头添加 `wrapper.setData()` |

#### 修复后验证

每次修复后立即重新执行测试，确保修复有效。如果仍有失败，继续修复。

---

### 5. collectCoverage(testFile) → CoverageResult

#### 覆盖率提取流程

```
1. 从测试文件注释读取源文件路径:
   匹配 `// 源文件: xxx.vue`

2. 构造覆盖率报告路径:
   coverage/lcov-report/${sourceFilePath}.html

3. 读取 HTML 报告，提取百分比:
   匹配 statements/branches/functions/lines 的 pct 值

4. 返回 CoverageResult:
   {
     statements: 85.2,
     branches: 82.1,
     functions: 88.0,
     lines: 85.2,
     reportPath: "file:///项目路径/coverage/lcov-report/index.html"
   }
```

#### 备用方案

如果找不到源文件路径注释，根据测试文件名推断：
- `__test__/ComponentName.test.js` → `src/components/xxx/ComponentName.vue`

---

### 6. analyzeUncovered(testFile, targetFile) → UncoveredInfo

#### 分析流程

```
1. 读取源文件（.vue），提取 <script> 中所有 methods

2. 读取测试文件（.test.js），提取所有 describe/test 中出现的方法名

3. 计算差集 = 源文件中的 methods - 测试文件中已测试的 methods
   → 未覆盖的方法列表

4. 在源文件中正则匹配 if/else/try-catch/switch 分支
   → 未覆盖的分支列表（估算）

5. 跳过 Vue 生命周期方法:
   created, mounted, beforeCreate, beforeMount, beforeUpdate,
   updated, beforeDestroy, destroyed
```

#### 返回格式

```javascript
{
  sourceFilePath: "src/components/xxx/Component.vue",
  uncoveredFunctions: [
    { name: "handleSubmit", type: "method", suggestion: "添加对 handleSubmit() 的测试" },
    { name: "validateForm", type: "method", suggestion: "添加对 validateForm() 的测试" }
  ],
  uncoveredBranches: [
    { type: "condition", suggestion: "添加测试覆盖 if 条件分支" },
    { type: "error-handling", suggestion: "添加测试覆盖 try-catch 分支" }
  ]
}
```

---

### 7. generateSupplementary(uncoveredInfo) → TestCase[]

#### 生成策略

**每次最多生成 4 个新测试用例**（3个方法 + 1个分支），避免一次性生成过多导致质量下降。

##### 方法测试模板

```javascript
test("测试 ${methodName} 方法", async () => {
  await wrapper.setData({
    // 根据方法需求设置数据
  });
  await wrapper.vm.${methodName}();
  expect(wrapper.vm.${methodName}).toBeDefined();
});
```

##### 分支测试模板

```javascript
test("测试分支条件 - ${suggestion}", async () => {
  await wrapper.setData({
    // 设置触发分支的条件
  });
  // 验证分支行为
});
```

##### 错误处理测试模板

```javascript
test("应该优雅处理错误", async () => {
  const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  // 触发错误场景
  await wrapper.vm.handleError();
  expect(wrapper.exists()).toBe(true);
  errorSpy.mockRestore();
});
```

#### 插入位置

在测试文件的最后一个 `describe` 块内部、最后一个 `});` 之前插入新测试用例。

---

### 8. cleanup()

#### 需要清理的临时文件

```javascript
const tempFiles = [
  'test_output.txt',
  'test_coverage_output.txt',
  'test_coverage_run.txt',
  'test_final_output.txt',
  'test_final_output2.txt',
  'test_final2_output.txt',
  'test_new_output.txt',
  'test_success_final.txt',
  'test_success_output.txt',
  'test_success_output2.txt',
  'test-report.html',
  'test_all_passed.txt',
  'test_iteration_output.txt',
  'coverage_iteration_output.txt'
];
```

逐个尝试删除，文件不存在时忽略错误。

---

## 异步处理规范

对于异步操作的测试：
- 使用 `async/await` 语法
- 使用 `flushPromises()` 等待 Promise 解决
- 使用 `await wrapper.vm.$nextTick()` 等待 DOM 更新

## 参考资源

- `references/vue-test-example.js` — 标准 Jest 测试样例
- `TestMock/UI.js` — UI 组件 Mock 库
- `__test__/serverPacketCapture.test.js` — 参考测试文件（展示标准格式）
