---
name: go-test-adapter
description: >
  Go/gotest 后端测试适配器。实现通用测试接口的后端版本，
  支持两种项目风格：go_kit（历史模板）与 generic_go（通用 Go 项目）。
  包括 Go 函数解析与依赖分析、表驱动测试生成、Mock 配置、
  go cover 覆盖率解析（-func 和 -html）、未覆盖代码分析（cov0）等后端特有逻辑。
---

# Go Test Adapter — 后端测试适配器

## Overview

实现通用编排器（test-orchestrator）定义的 8 个适配器接口，
处理所有 Go + go test 相关的特有逻辑。

本适配器支持两种测试配置（profile）：

- `go_kit`: 兼容历史 `code/src/mock_test` 目录结构与 `InitService` 模式
- `generic_go`: 适用于标准 Go 项目（无 go-kit、无固定目录约束）

---

## 项目风格识别（Profile Detection）

优先读取手动开关，再自动识别：

### 手动强制模式（推荐在项目识别不稳定时使用）

从编排参数读取：`options.goProfile`

- `goProfile = go_kit`：强制走 `go_kit`
- `goProfile = generic_go`：强制走 `generic_go`
- `goProfile = auto` 或未传：走自动识别
- 非法值：回退 `auto`，并记录告警

### 自动识别规则（goProfile=auto 时）

```text
if targetFile 包含 "code/src/" 且项目中存在 "code/src/mock_test":
  profile = go_kit
else:
  profile = generic_go
```

补充判定信号（命中越多越倾向 `go_kit`）：

- 目录存在 `code/src/mock/`、`code/src/mock_test/`
- 已存在 `initService.go` / `InitService()` 测试辅助
- 被测代码位于 `[模块]/service/` 且依赖 `DaoMgr` / `Handle` 风格字段

---

## 硬性约束

| 约束 | `go_kit` | `generic_go` |
|------|----------|--------------|
| 文件修改范围 | 只允许修改 `code/src/mock_test/` 和 `code/src/mock/` | 只允许修改 `*_test.go` 与测试辅助文件（如 `testutil`）；禁止修改业务源码 `.go` |
| 测试写法 | 始终使用表驱动 `[]struct` | 始终使用表驱动 `[]struct` |
| 环境 | Windows 命令风格 | Windows 命令风格 |
| 兼容策略 | 复用现有 `InitService`/Mock 结构 | 优先同包测试 + 最小依赖 Stub/Mock |

---

## 技术栈

- **语言**: Golang
- **测试**: go test + testing（可选 testify/assert + testify/mock）
- **覆盖率**: go test `-coverprofile` + `go tool cover`

---

## 覆盖率要求

| 维度 | 目标 |
|------|------|
| 函数/核心分支覆盖率（主判断指标） | >= 80% |

---

## 接口实现

### 1. generate(targetFile) -> testFile

#### 输入/输出

- **输入**: Go 函数所在文件路径（可带行号范围），如 `internal/service/user.go:30-120`
- **输出**: 生成或更新的测试文件路径（由 profile 决定）

#### 生成流程

##### Step 0: 识别 profile

按以下优先级确定 `profile`，后续步骤按 profile 分支执行：

1. 若 `options.goProfile` 为 `go_kit` 或 `generic_go`，直接使用
2. 若 `options.goProfile` 为 `auto` 或未提供，执行自动识别
3. 若值非法，告警并回退自动识别

##### Step 1: 读取函数与依赖分析

读取目标函数与所属接收者（如果有），分析函数内部依赖：

| 调用类型 | 处理方式 |
|---------|---------|
| 同 package / 同 receiver 内部调用 | 级联读取相关函数 |
| 外部依赖且可注入（interface） | 生成 mock/stub |
| 外部依赖且不可注入（具体 struct 且强耦合） | 标记风险，优先通过输入构造覆盖；必要时提示人工重构 |

##### Step 2: 确定输出路径

| profile | 输出路径策略 |
|---------|-------------|
| `go_kit` | `code/src/mock_test/[模块名]_mock/[函数名小驼峰]_test.go` |
| `generic_go` | 优先 `[被测文件同目录]/[文件名]_test.go`；若已有测试文件则在原文件追加用例 |

示例（`generic_go`）：

- 被测文件：`internal/user/service.go`
- 测试文件：`internal/user/service_test.go`

##### Step 3: 生成测试初始化骨架

`go_kit` 分支：

- 复用或创建 `InitService()`（保持历史结构）
- 复用已有 `mockStructs.go`，不存在时按依赖补齐

`generic_go` 分支：

- 生成最小初始化辅助（如 `newTestSubject()`）
- 依赖优先顺序：已有 fake/stub > testify/mock > 本地轻量 stub
- 禁止生成与业务框架强绑定的字段模板

示例（`generic_go`）：

```go
func newTestSubject() *Service {
    return &Service{
        repo: &fakeRepo{},
    }
}
```

##### Step 4: 生成表驱动测试框架

```go
func Test[函数名](t *testing.T) {
    tests := []struct {
        name      string
        setup     func()
        input     [输入类型]
        wantErr   bool
        assertFn  func(t *testing.T, got [返回类型], err error)
    }{
        {
            name: "happy path",
            setup: func() {
                // mock/stub setup
            },
            input: [输入值],
            wantErr: false,
            assertFn: func(t *testing.T, got [返回类型], err error) {
                // assert
            },
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if tt.setup != nil {
                tt.setup()
            }
            // call target
        })
    }
}
```

##### Step 5: 先落一条可通过用例

第一条用例必须是可稳定通过的 happy path，用于建立可迭代基线。

#### Mock 注意事项

| 要点 | 说明 |
|------|------|
| 复用优先 | 优先复用已有 mock/fake，避免重复创建 |
| 断言稳定 | 避免强依赖时间、随机数、全局状态 |
| 全局变量恢复 | 修改全局状态后必须在测试后恢复 |
| 协程场景 | 使用可控同步（channel/waitgroup），减少 `time.Sleep` |

---

### 2. execute(testFile, collectCoverage?) -> rawOutput

#### 命令格式（Windows）

`go_kit` 分支：

```cmd
cd [项目绝对路径]\code\src\mock_test\[模块名]_mock\ && go test "-coverprofile=coverage.out" "-coverpkg=../../[模块名]/service" "."
```

`generic_go` 分支：

```cmd
cd [测试文件所在目录] && go test -v -coverprofile=coverage.out .
```

当需要更完整覆盖范围时（`generic_go`）：

```cmd
cd [项目根目录] && go test -v -coverprofile=coverage.out -coverpkg=./... [目标包]
```

#### 注意事项

- 优先使用 `go test` 标准命令，避免框架特定脚本
- `collectCoverage=false` 时可省略 `-coverprofile`

---

### 3. parseResult(rawOutput) -> TestResult

#### 解析逻辑

```go
func parseGoTestOutput(rawOutput string) TestResult {
  // 成功: 包含 "ok" 且不包含 "FAIL"
  // 失败: 提取 "--- FAIL: TestXxx/CaseName" 和后续错误行
  // 覆盖率: 匹配 "coverage: XX.X% of statements"
}
```

输出统一为：

- `totalTests`
- `passedTests`
- `failedTests`
- `failedTestCases[]`
- `allPassed`

---

### 4. fix(testFile, failures) -> boolean

#### 修复原则

| profile | 修复边界 |
|---------|---------|
| `go_kit` | 只改 `code/src/mock_test/` 和 `code/src/mock/` |
| `generic_go` | 只改 `*_test.go` 与测试辅助（`testutil`/`mocks`）；不改业务源码 |

#### 修复方式

| 错误类型 | 修复方式 |
|---------|---------|
| 断言不匹配 | 调整期望值或输入数据 |
| Mock 方法未注册 | 补充 Mock 行为定义 |
| 返回值类型/空值错误 | 调整 stub 返回值 |
| 缺少 import | 补充必要 import |
| 测试初始化不完整 | 补充 setup / 构造依赖 |

#### 修复后验证

每轮修复后重新执行 `go test`，直到通过或达到重试上限。

---

### 5. collectCoverage(testFile) -> CoverageResult

#### 覆盖率采集流程

1. 确保已生成 `coverage.out`
2. 执行：

```cmd
go tool cover -func coverage.out
```

3. 可选生成 HTML：

```cmd
go tool cover -html coverage.out -o coverage.html
```

#### 结果提取规则

- 优先提取**目标函数**覆盖率（若可定位）
- 若无法定位目标函数，使用 `total:` 行的总覆盖率
- 统一映射到 `branches` 字段作为主判断指标

#### 返回格式

```javascript
{
  statements: null,
  branches: 82.5,       // 主判断指标（目标函数或总覆盖率）
  functions: null,
  lines: null,
  reportPath: "[测试目录]/coverage.html"
}
```

#### 重要：达标即停

覆盖率 >= 80% 后立即终止迭代并输出结果。

---

### 6. analyzeUncovered(testFile, targetFile) -> UncoveredInfo

#### 分析流程

1. 读取 `coverage.html`
2. 定位目标函数/文件区域
3. 查找 `class="cov0"` 代码块（未覆盖）
4. 标注可补测分支（错误路径、条件分支、边界条件）

#### 返回格式

```javascript
{
  sourceFilePath: "internal/user/service.go",
  functionName: "CreateUser",
  currentCoverage: 65.2,
  uncoveredBranches: [
    {
      type: "error-handling",
      code: "if err != nil { ... }",
      lineRange: "48-52",
      suggestion: "mock repo.Create 返回 error"
    }
  ]
}
```

---

### 7. generateSupplementary(uncoveredInfo) -> TestCase[]

#### 生成策略

优先补充以下场景：

1. 错误处理分支（`err != nil`）
2. 边界条件（空值、零值、长度边界）
3. 条件分支（if/switch 默认分支）

模板（表驱动）：

```go
{
  name: "when repo returns error",
  setup: func() {
    repo.On("Create", mock.Anything).Return(errors.New("mock error"))
  },
  input:   validInput,
  wantErr: true,
}
```

---

### 8. cleanup()

#### 需要清理的临时文件

- `coverage.out`
- `coverage.html`
- 中间日志文件（如 `test_output.txt`）

仅清理本次测试流程生成的临时文件。

---

## 项目结构参考

### `go_kit` 典型结构

```text
code/src/
├── [module]/service/
├── mock/
└── mock_test/[module]_mock/
```

### `generic_go` 典型结构

```text
.
├── go.mod
├── internal/.../*.go
├── pkg/.../*.go
└── [same package]/*_test.go
```

---

## 手动强制模式示例

```javascript
{
  targetFile: "internal/user/service.go",
  mode: "full",
  options: {
    goProfile: "generic_go" // auto | go_kit | generic_go
  }
}
```

---

## 参考资源

- `references/go-test-example.go` — 标准表驱动测试样例
- `references/coverage-strategies.md` — 覆盖率提升策略
