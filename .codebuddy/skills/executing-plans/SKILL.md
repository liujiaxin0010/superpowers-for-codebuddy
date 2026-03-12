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
2. 加载 TaskContract / 合同摘要
3. 按依赖顺序执行任务
4. 严格遵循 TDD：RED -> GREEN -> REFACTOR
5. 每项任务完成后提供证据
6. 持续更新 `docs/progress.md` 与 `docs/findings.md`
7. 完成前运行质量门禁脚本（check-quality），未通过不得收尾
8. 输出收尾时必须声明：剩余风险、owner、handoff 建议
9. 涉及日志改动时必须：
   - 复用项目日志结构（或落实新项目已选框架）
   - 保持日志英文
   - 不使用控制台输出（除非用户明确要求）
10. 回滚执行安全约束：
   - 默认仅执行“回滚准备 + dry-run 演练”，不得自动执行真实回滚。
   - 真实回滚前必须获得 Boss 的显式确认。
   - 执行真实回滚前必须先产出并记录快照点（commit/tag/备份点）与恢复命令。

## 分级策略

- L：标准执行并补齐测试
- M：完成前强制执行 `/code-review`
- H：必须具备头脑风暴证据，并设置风险/回滚检查点（默认 dry-run）
