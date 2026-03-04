---
name: spec-lite
description: 轻量规格生成，自动给出 L/M/H 分级建议并输出门禁上下文。
---

# Spec-Lite（轻量规格）

## 目标

在实施前先生成可执行的轻量规格，并计算任务等级。

默认输出路径：

`docs/specs/YYYY-MM-DD-<name>-spec-lite.md`

## 输入参数

`/spec-lite <需求描述> [tierOverride=L|M|H] [overrideReason=...] [explore=true|false]`

## 通用需求澄清与方向确认（硬门禁）

在生成 spec 前，必须先确认以下信息：

1. 业务目标与成功标准（判定完成的标准）
2. 用户/调用方与使用场景
3. 触发入口与交互路径（API/CLI/定时/UI/任务）
4. 交付形态（接口/命令/任务/页面/配置）
5. 关键数据对象与范围边界（新增/修改/不改）
6. 外部契约与兼容性影响
7. 非功能约束（性能/安全/稳定性/合规）
8. 观测与运维要求（日志/监控/告警）
9. 日志策略（复用项目日志结构；日志英文；默认禁控制台）

AI 必须给出 2-3 个实现方向供用户确认，每个方向至少包含：

1. 核心思路
2. 主要收益
3. 主要代价/风险
4. 适用前提

若任一项缺失或含 `TBD/待定/未确认`：

1. 返回 `GateResult.status=blocked`
2. `missing[]` 列出未确认项
3. `nextCommand` 指向补充信息后重试 `/spec-lite`
4. 不得推荐进入 `/write-plan`

若用户明确“不接受当前方向”，还必须补充：

1. 可接受的替代方向
2. 不可触碰约束（必须/禁止）

否则同样 `BLOCKED`。

日志相关补充约束：

1. 旧项目：必须先说明“已识别并沿用”的原有日志结构（框架、字段、级别、traceId 传递方式）
2. 新项目：必须在澄清/brainstorm 中确定日志框架与结构化字段
3. 若日志策略未明确，禁止进入 `/write-plan`

## GateContext 字段

1. taskId
2. recommendedTier
3. finalTier
4. overrideReason
5. specPath
6. planPath
7. requiredChecks
8. completedChecks
9. gateStatus (`pass|blocked`)

## GateResult 字段

1. status (`pass|blocked`)
2. tier
3. missing[]
4. nextCommand
5. message

## 追踪链接扩展字段

在 spec 文档“追踪链接”中补充以下兼容字段：

1. `researchPath`
2. `designPath`
3. `testStrategyPath`
4. `testcasePath`
5. `testcaseAnalysisPath`
6. `implementationProgressPath`
7. `implementationSummaryPath`

## 评分规则

- 变更文件数：`<=2:+0, 3-6:+1, >=7:+2`
- 影响模块数：`1:+0, 2:+1, >=3:+2`
- 外部契约变更（API/DB/Event/Config）：`+3`
- 安全/权限域变更：`+3`
- 数据/状态迁移：`+2`
- 关键路径性能影响：`+1`
- 线上故障修复：`+1`

等级映射：

- 0-2 => L
- 3-6 => M
- >=7 => H

## 混合覆盖策略

1. 先计算 `recommendedTier`
2. 若提供 `tierOverride`，则 `overrideReason` 必填
3. 缺少覆盖理由时直接 `BLOCKED`
4. `finalTier = tierOverride 或 recommendedTier`

## 执行流程

1. 读取 `template.md`
2. 执行通用需求澄清，补齐所有必填项
3. 输出 2-3 个实现方向并获取用户确认
4. 若存在缺失项或方向未确认，直接阻断并返回补充问题清单
5. 填写目标、范围外、接口/数据影响、澄清结论、方向确认记录、风险、验收、回滚
6. 计算评分并得到 `recommendedTier`
7. 应用覆盖策略并得到 `finalTier`
8. 写入规格文档与 `GateContext`
9. 返回 `GateResult`：
   - `H` -> 下一步 `/brainstorm <需求描述>`
   - `L/M` -> 下一步 `/write-plan spec=<specPath> tier=<finalTier>`
