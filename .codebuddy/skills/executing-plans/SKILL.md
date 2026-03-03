---
description: 在硬门禁检查下按批次执行已批准计划。
---

# 执行计划（Executing Plans）

在门禁通过前，不允许进入执行阶段。

## 硬门禁前置条件

执行前先运行 `.codebuddy/skills/process-gatekeeper/SKILL.md`。

若被阻断：

- 输出阻断结果
- 不执行任何任务

## 批次执行规则

1. 加载 spec + plan 上下文
2. 按依赖顺序执行任务
3. 严格遵循 TDD：RED -> GREEN -> REFACTOR
4. 每项任务完成后提供证据
5. 持续更新 `docs/progress.md` 与 `docs/findings.md`
6. 完成前运行质量门禁脚本（check-quality），未通过不得收尾
7. 涉及日志改动时必须：
   - 复用项目日志结构（或落实新项目已选框架）
   - 保持日志英文
   - 不使用控制台输出（除非用户明确要求）

## 分级策略

- L：标准执行并补齐测试
- M：完成前强制执行 `/code-review`
- H：必须具备头脑风暴证据，并设置风险/回滚检查点
