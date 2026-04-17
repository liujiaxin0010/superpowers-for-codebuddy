---
name: release-and-rollback
description: 发布与回滚技能。用于在功能进入生产发布时产出 changelog / release-notes / rollback-playbook，并在必要时执行真实回滚。用户提到"发布 / release / 上线 / 回滚 / rollback / hotfix / 灰度"时触发。
---

# 发布与回滚

回答的核心问题：**这次发布可控吗？出问题后能不能在可接受时间内回到上一个已知好状态？**

发布不是"把代码推上去"，回滚不是"把代码改回来"。本技能把发布与回滚作为成对的契约管理。

## 触发条件

1. 用户要求发布 / 上线 / 灰度 / 全量
2. 用户要求回滚（默认仅准备，不直接执行）
3. 发布工单、release tag、version bump
4. Hotfix 流程
5. 涉及数据迁移或 schema 变更的发布（必须联动 `/data-safety-check`）

## 何时不用

1. 本地开发部署、临时调试环境
2. CI 沙盒内不会影响任何外部用户的产物

## 阻断条件（BLOCKED）

1. 缺少 changelog / release-notes / rollback-playbook 任一
2. 发布涉及数据操作但未提供已签字的 `/data-safety-check` 报告
3. `/requirement-coverage` / `/security-review` / `/unified-test` 任一处于未通过态
4. 真实回滚未取得 Boss 显式签字

## 发布（/release）三件套

### 1. Changelog 条目

- 路径：`docs/changelog/<version>.md`
- 必含字段：版本号、日期、新增 / 变更 / 修复、影响面、关联 spec/plan、owner
- 模板：`.codebuddy/skills/release-and-rollback/templates/changelog-entry.md`

### 2. Release Notes

- 路径：`docs/release/<version>-release-notes.md`
- 必含字段：发布策略（灰度 / 全量）、观测指标、告警阈值、终止条件、通知链、值守人、回滚触发条件
- 模板：`.codebuddy/skills/release-and-rollback/templates/release-notes.md`

### 3. Rollback Playbook

- 路径：`docs/runbooks/<feature>-rollback.md`
- 必含字段：快照点（commit / tag / 备份标识）、恢复命令、RTO / RPO、前置条件、演练结果、Boss 签字要求
- 模板：`.codebuddy/skills/release-and-rollback/templates/rollback-playbook.md`

## 发布前 Checklist

- [ ] spec / plan 已通过 `/requirement-coverage`
- [ ] `/security-review` 无 🔴 严重问题
- [ ] 若含数据操作 → `/data-safety-check` 已签字
- [ ] `/unified-test` / `/system-test` 均已通过
- [ ] Changelog 条目已合入主干
- [ ] Release notes 已评审
- [ ] Rollback playbook 已演练（staging 一次）
- [ ] 灰度 / 全量策略已写入
- [ ] 观测指标 / 告警阈值已部署
- [ ] 值守人 / 通知链已就位

## 回滚（/rollback）流程

默认策略：**仅允许"回滚准备 + dry-run 演练"**。真实回滚必须经 Boss 显式签字。

1. 识别当前部署版本与上一个已知好版本
2. 读取 `rollback-playbook`
3. 确认快照点仍有效（tag / commit / 备份未过期）
4. dry-run：尝试在 staging 按脚本回滚一次
5. 通知链触发
6. Boss 签字原文 + 时间戳 → `docs/progress.md`
7. 真实回滚执行
8. 回滚后 24 小时内提交复盘（`docs/findings.md`）

## 输出

- 发布：`docs/changelog/<version>.md` + `docs/release/<version>-release-notes.md` + `docs/runbooks/<feature>-rollback.md`
- 回滚：`docs/runbooks/<feature>-rollback-<timestamp>.md`（实际执行记录）

## 禁止事项

1. 禁止在未演练的情况下声称 rollback-playbook 可用
2. 禁止把回滚当作常规运维动作直接执行，必须 Boss 签字
3. 禁止 release-notes 只写"常规更新"而不列影响面
4. 禁止把发布与数据迁移绑定在同一次变更但未做 `/data-safety-check`
