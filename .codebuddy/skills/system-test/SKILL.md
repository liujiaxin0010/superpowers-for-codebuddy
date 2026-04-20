---
name: system-test
description: 系统测试技能。用于在 `/unified-test` 之后、`/release` 之前做端到端、跨模块的验证。回答"系统作为整体是否满足需求"。用户提到"系统测试 / E2E / 集成测试 / UAT / 验收 / 剧本"时触发。
---

# 系统测试

回答的核心问题：**把每个模块拼在一起，作为一个系统运行时，是否满足需求？**

`/unified-test` 回答"代码实现是否符合用例"，`/system-test` 回答"整个系统是否符合需求"。两者不能互相替代。

## 触发条件

1. H 级 / 复杂扩展任务
2. 涉及跨模块协作 / 跨服务调用
3. 新增 / 修改外部接口、用户可见行为
4. 发布前的最终验收

## 何时不用

1. 纯文档改动
2. 仅局部工具函数改动且无跨模块影响
3. L 级简单任务（走 `/unified-test` 即可）

## 前置要求

1. `/requirement-coverage` 报告 = 通过
2. `/unified-test` 报告 = 通过
3. 存在系统测试剧本
4. 存在数据准备 / 清理脚本

## 阻断条件（BLOCKED）

1. `/requirement-coverage` 未通过
2. `/unified-test` 未通过
3. 系统测试剧本缺失或未覆盖主路径
4. 数据准备脚本会污染生产
5. 🔴 严重 / 🟠 高缺陷存在（按 `defect-classification.json`）

## 输入参数

`/system-test scope=<name> [spec=<path>] [plan=<path>] [env=staging|uat]`

## 产出

### 1. 系统测试剧本

路径：`docs/quality/system-test-scenarios.md`

必含字段：

- 场景 ID
- 关联需求 ID（与 `/requirement-coverage` 矩阵对齐）
- 前置条件
- 操作步骤
- 预期结果
- 实际结果
- 状态：pass / fail / blocked
- 证据路径（日志、截图、录屏）

### 2. 数据准备 / 清理脚本

- 路径：`docs/quality/system-test-data-setup.md` + 脚本文件
- 要求：
  - 仅作用于 staging / uat 环境
  - 可重复执行
  - 清理脚本必须在每次场景后运行
  - 不得访问生产数据（若必须 → 先过 `/data-safety-check`）

### 3. 缺陷分类表

- 路径：`docs/quality/system-test-defects.md`
- 分级：🔴 严重 / 🟠 高 / 🟡 中 / 🟢 低（引用 `defect-classification.json`）
- 每条缺陷必含：场景 ID、触发步骤、实际与预期差异、根因初判、修复建议

### 4. 系统测试报告

- 路径：`docs/quality/system-test-report.md`
- 必含：
  - 剧本总数 / 通过 / 失败 / 阻塞
  - 与需求覆盖矩阵的对齐状态
  - 缺陷摘要（按分级）
  - 发布建议（✅ 可发布 / 🟠 有条件发布 / 🔴 禁止发布）

## 与其他命令的耦合

- `/release` 前置：必须有通过态系统测试报告
- `/rollback` 复盘：需要引用系统测试发现的问题
- 覆盖矩阵：每个需求 ID 都应能映射到至少一个系统测试场景

## 禁止事项

1. 禁止用 `/unified-test` 结果代替系统测试
2. 禁止在生产环境跑系统测试
3. 禁止缺陷未关闭就声明"系统测试通过"
4. 禁止实现者自审自测（独立审查视角）
