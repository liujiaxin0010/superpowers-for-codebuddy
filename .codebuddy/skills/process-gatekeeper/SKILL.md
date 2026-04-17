---
name: process-gatekeeper
description: 命令执行前置项的硬性流程门禁。用于在 `/write-plan`、`/execute-plan`、`/research`、`/testcase`、`/code-review`、`/fix-bug`、`/Featureflow` 等命令进入主体前检查 spec、plan、TaskContract、tier、owner、验证命令和头脑风暴证据是否齐备；若不满足则返回 `BLOCKED` 并给出下一条命令。
---

# 流程门禁（Process Gatekeeper）

本技能回答的是：**当前命令能不能放行、缺的是什么、下一条命令该回退到哪里。**

## 资源加载规则

已知 `command` 后，优先只读取 `references/gate-matrix.md` 里对应那一行；只有需要比较多个候选命令时，才扩大到多行。

当矩阵单行还不足以解释某个命令的详细门禁语义时，再读取：

- `references/command-gate-rules.md`

阻断时优先使用：

- `templates/blocked-report.md`

通过时优先使用：

- `templates/pass-report.md`

不要在未确定 `command` 时就把整张矩阵和全部细则一次性读进上下文。

## 输入期望

至少明确：

1. `command`
2. `tier`
3. 相关 `spec/plan/TaskContract/target`

## 核心协议

1. 门禁是阻断机制，不是建议机制
2. 任一必需项缺失即返回 `BLOCKED`
3. `BLOCKED` 必须提供可执行的 `nextCommand`
4. 一旦阻断，命令主体必须停止
5. 详细命令级约束以矩阵和命令细则为准，不要在主文件里重复抄一遍

## 软建议（非阻断）

以下情况不阻断但应提示：

- L 级任务缺少代码审查：建议补充，但不阻断
- 计划中缺少文档同步任务：建议追加，但不阻断
- spec 文档已通过但距今超过 5 天且需求较复杂：建议重新确认，但不阻断
- owner 信息模糊但任务风险较低：建议明确，但不阻断

## 脚本边界

### `scripts/check-gates.*`

只在字段需要做确定性检查时使用，用于：

1. 校验 spec / plan / contract 关键字段
2. 统一输出 pass / blocked 结果

### `scripts/check-quality.*`

只在接近收尾、发布前或质量闸口阶段使用；不要在普通前置门禁中提前运行。

## 质量闸口说明

`check-quality.*` 默认校验：

1. 测试通过率阈值
2. 覆盖率阈值
3. 文档同步状态
4. 可选校验 `spec/AI2AI` 关键文档

## 禁止事项

1. 不要把门禁当作“提醒”，一旦阻断就必须停止主体执行
2. 不要返回 `BLOCKED` 却不给下一条可执行命令
3. 不要在缺少 `command` 语义的情况下乱套门禁
4. 不要把质量闸口和普通前置门禁混为一谈
5. 不要在主文件里重复堆所有命令的细则
