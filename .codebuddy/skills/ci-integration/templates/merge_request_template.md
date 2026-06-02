<!--
Featureflow MR 模板。由 /ci-setup 安装到 .gitlab/merge_request_templates/featureflow.md。
CE 14.8.2 无 Approval Rules，本模板的 checklist 是人工审查约束的主要载体。
-->

## 变更说明

<!-- 这个 MR 做了什么、为什么 -->

## 关联

- 需求 / Issue：
- Spec：`docs/specs/`
- Plan：`docs/plans/`

## 门禁 Checklist（合并前逐项确认）

### 流程证据
- [ ] spec 已确认，`gateStatus` 为 PASS
- [ ] 计划已执行完毕，`docs/progress.md` 已更新
- [ ] 一次抛出 ≥ 2 个待决策项的，已落 `docs/pending-decisions.md`

### 质量
- [ ] 测试通过，覆盖率达标（流水线 `quality:check` 绿）
- [ ] 无遗留调试代码（console / print / qDebug / TODO 无单号）
- [ ] commit message 符合规范（流水线 `verify:commit-msg` 绿）

### 审查
- [ ] 代码审查已完成，严重问题已处理
- [ ] 涉及外部输入 / 鉴权 / 敏感数据的，已过 `/security-review`
- [ ] 涉及生产数据 / 表结构变更的，已过 `/data-safety-check`

### 收尾
- [ ] 文档与代码同步
- [ ] 剩余风险与 owner 已在下方说明

## 剩余风险 / owner

<!-- 未覆盖的风险、需后续跟进项、handoff owner -->

/assign me
