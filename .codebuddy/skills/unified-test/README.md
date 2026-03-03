# unified-test — 通用单元测试框架

> 前后端统一的单元测试智能体框架，支持 Vue(Jest) 和 Go(go test) 两种技术栈。

## 快速导航

```
unified-test/
├── SKILL.md                          ← 主技能入口（路由 + 调度）
├── README.md                         ← 本文件
├── agents/
│   └── unified-test-agent.md         ← Agent 配置（统一入口）
├── skills/
│   ├── test-orchestrator.md          ← 通用编排器（前后端共享）
│   ├── test-executor-core.md         ← 通用执行器核心（前后端共享）
│   ├── vue-test-adapter.md           ← 前端适配器（Vue/Jest）
│   └── go-test-adapter.md            ← 后端适配器（Go/gotest）
├── references/
│   ├── defect-classification.md      ← 缺陷分类表
│   ├── vue-test-example.js           ← 前端测试参考样例
│   ├── go-test-example.go            ← 后端测试参考样例
│   └── coverage-strategies.md        ← 覆盖率提升策略
└── scripts/
    └── cleanup.sh                    ← 临时文件清理脚本
```

## 架构概览

```
用户: "为 xxx.vue 生成单元测试"
         │
         ▼
┌─────────────────────────┐
│  Agent: 通用单元测试专家   │  ← agents/unified-test-agent.md
│  识别 .vue → 前端         │
│  识别 .go  → 后端         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  SKILL.md (主技能入口)    │  ← 选择适配器 + 调用编排器
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  test-orchestrator       │  ← 通用编排逻辑（前后端共享）
│  ┌───────────────────┐  │
│  │ A: 生成            │  │ → adapter.generate()
│  │ B: 执行-修复循环    │  │ → adapter.execute() / fix()
│  │ C: 覆盖率收集      │  │ → adapter.collectCoverage()
│  │ D: 覆盖率迭代      │  │ → adapter.analyzeUncovered()
│  │ E: 清理 & 报告     │  │ → adapter.cleanup()
│  └───────────────────┘  │
└────────┬────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│  Vue   │ │  Go    │     ← 语言适配器（各实现 8 个接口）
│ Adapter│ │ Adapter│
└────────┘ └────────┘
```

## 统一核心原则

| # | 原则 | 说明 |
|---|------|------|
| 1 | 不改业务代码 | 修复永远优先改测试文件 |
| 2 | 覆盖率 ≥ 80% | 达标即停，不过度优化 |
| 3 | 自动迭代改进 | 未达标时自动分析未覆盖代码 → 补充用例 → 重跑 |
| 4 | 自动化最大化 | 失败自动修复，覆盖率自动迭代 |
| 5 | 清理临时文件 | 流程结束后自动清理 |

## 适配器接口（8 个）

| 接口 | 前端实现 | 后端实现 |
|------|---------|---------|
| `generate()` | Vue SFC → Jest | Go func → 表驱动 |
| `execute()` | npm test | go test |
| `parseResult()` | Jest 输出 | go test 输出 |
| `fix()` | 修改 Jest Mock/断言 | 修改 Mock.On/assert |
| `collectCoverage()` | Istanbul HTML | go tool cover |
| `analyzeUncovered()` | 正则提取 methods | 解析 cov0 |
| `generateSupplementary()` | Jest test() | Go 表驱动项 |
| `cleanup()` | 删 txt 等 | 删 coverage.out |

## 扩展新语言

新增语言（如 Java/Python）只需 3 步：

1. 创建 `skills/xxx-test-adapter.md`
2. 实现 8 个适配器接口
3. 在 `SKILL.md` 路由表中添加扩展名映射

**无需修改编排器和执行器核心。**

## 原始文档映射

| 原文档 | → 合并去向 |
|--------|-----------|
| Web单元测试专家 (Agent) | → Agent + SKILL.md |
| test-orchestrator | → test-orchestrator.md (提取通用逻辑) |
| test-executor (10模块) | → test-executor-core.md + vue-test-adapter.md |
| test-generator | → vue-test-adapter.md 的 generate() |
| 停车场单元测试Agent | → Agent + go-test-adapter.md |
| golang-testing | → go-test-adapter.md + references/ |
| Code Analysis Guide | → references/defect-classification.md |
