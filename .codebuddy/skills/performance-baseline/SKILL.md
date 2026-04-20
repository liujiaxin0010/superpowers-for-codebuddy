---
name: performance-baseline
description: 性能基线技能。用于在涉及热路径 / 批量处理 / 并发模型变更 / DB 查询改动 / 关键接口的变更前后建立基线并做回归判定。用户提到"性能 / perf / 基线 / benchmark / 压测 / 延迟 / QPS / 内存"时触发。
---

# 性能基线

回答的核心问题：**这次改动让关键路径变慢了吗？慢多少？是不是可接受？**

没有基线谈不上回归。本技能把"建立基线"与"基于基线判定"作为成对的硬要求。

## 触发条件

1. 热路径代码改动（鉴权、请求分发、序列化、编解码、索引查询）
2. 批量处理 / 离线任务（ETL、导入导出、定时任务）
3. 并发模型变更（线程池大小、锁策略、协程数、连接池、队列容量）
4. DB 查询改动（新增索引、SQL 重写、连接池、分页策略）
5. 关键接口改动（QPS / 延迟 SLO 有约束的接口）
6. 依赖升级可能影响性能（序列化库、HTTP 客户端、DB 驱动）

## 何时不用

1. 纯文档 / 注释改动
2. 不在热路径的实验性代码
3. 临时脚本

## 阻断条件（BLOCKED）

1. 命中触发条件但缺少本次 perf 报告
2. 缺少历史基线且未新建
3. 回归超过 `thresholdPct` 且无 Boss 显式接受

## 输入参数

`/perf-check scope=<name> [baseline=<path>] [threshold=5|10] [env=prod|staging|dev]`

## 基线存储

目录：`.codebuddy/state/perf-baseline/<scope>.json`

文件结构（JSON）：

```json
{
  "scope": "auth-api",
  "createdAt": "YYYY-MM-DD",
  "updatedAt": "YYYY-MM-DD",
  "env": "staging",
  "workload": "100 RPS, 60s, uniform",
  "machine": "linux-x86_64 / 4C8G",
  "metrics": {
    "p50_ms": 10.3,
    "p95_ms": 25.1,
    "p99_ms": 52.7,
    "qps": 98.4,
    "cpu_pct": 42.0,
    "mem_mb": 512.0
  },
  "notes": ""
}
```

新建基线必须：

1. 指定固定负载（请求模式、并发数、持续时间）
2. 固定环境（机型、OS、JVM / 运行时版本）
3. 至少 3 次运行取中位数
4. 同一 scope 只保留一份权威基线；更新时必须写明 `updatedAt` 与变更原因

## 回归判定

- `thresholdPct` 默认 ±5%
- 关键指标（延迟 p95/p99、QPS、错误率、CPU / 内存峰值）逐项对比
- 任一关键指标回归超阈值 → 🔴 BLOCKED
- 回归在阈值内但趋势不好 → 🟠 建议审查
- 无回归 → ✅ 通过

## 报告输出

- 路径：`docs/quality/perf-report-<scope>.md`
- 必含字段：
  - 基线摘要（引用 `.codebuddy/state/perf-baseline/<scope>.json`）
  - 本次结果（同样的 JSON 结构 + 原始日志路径）
  - 对比表（指标 / 基线 / 本次 / 差值 / 差值%）
  - 判定结论（✅ / 🟠 / 🔴）
  - 若 🔴：根因初判 + 修复建议 或 Boss 签字豁免

## 禁止事项

1. 禁止用不同机型 / 负载的数据直接对比
2. 禁止单次运行结果代替基线
3. 禁止"人工观察无明显变化"代替数字判定
4. 禁止在无基线的情况下声明"性能 OK"
