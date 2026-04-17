# 性能基线存储

本目录保存每个性能 scope 的权威基线。

## 命名

- 每个 scope 一份 JSON：`<scope>.json`
- 示例：`auth-api.json`、`order-batch-import.json`、`db-write-path.json`

## 文件格式

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

## 刷新原则

1. 基线只在以下情况刷新：
   - 架构级重构（经 Boss 确认）
   - 依赖升级（记录升级项）
   - 机型 / 运行时版本变化
2. 每次刷新必须写 `updatedAt` 与 `notes`（变更原因 + 前后值对比）
3. 禁止为了"通过 perf-check"而刷新基线

## 使用

- 新建 / 刷新：`/perf-check scope=<name>`
- 对比判定：`/perf-check scope=<name>` 自动读取本文件
