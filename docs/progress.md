# Progress

## 2026-03-02

- [x] `docs/specs/` 与 `spec-lite` 模板落地
- [x] `/write-plan` 前置门禁阻断
- [x] `/extend` 改为先判档再选流程
- [x] 新增质量门禁脚本 `check-quality.ps1/.sh`
- [x] 新增质量门禁结果文件 `docs/quality/last-quality-gate.json`
- [x] 准备 3 个需求试运行数据与记录

## 2026-03-04

- [x] 新增兼容目录 `spec/Me2AI` 与 `spec/AI2AI`
- [x] 新增命令：`/research`、`/testcase`、`/code-self-check`
- [x] 新增技能：`research`、`testcase`、`code-self-check`
- [x] 扩展 `spec-lite` 追踪链接字段（7 项兼容字段）
- [x] 扩展门禁矩阵与 `check-gates.ps1/.sh`
- [x] 扩展 `check-quality.ps1/.sh` 可选参数 `RequireAi2AiDocs`
- [x] 回填 3 份历史 spec 的澄清结论、方向确认与追踪链接

## 2026-03-09

- [x] 新增 TaskContract 模板目录 `.codebuddy/templates/task-contracts/`
- [x] 为 `spec-lite` 模板增加 `TaskContract` 区块与任务类型字段
- [x] 升级 `process-gatekeeper` 与门禁矩阵，纳入合同完整性检查
- [x] 升级 `/fix-bug`、`/test-gen`、`/unified-test`、`/code-review`、`/status` 的合同与证据输出要求
- [x] 新增本地 workflow 文档与 playbook
- [x] 将项目命名统一为 `Featureflow`
- [x] 新增 `/issue-draft-pr` 与 `/parallel-delivery` 命令入口
- [x] 新增 `task-contracts`、`issue-draft-pr`、`parallel-delivery` 技能目录并接入命令
- [x] 新增 `devflow-router` 技能、`Featureflow` 总控代理与 `/Featureflow` 单入口命令
- [x] 强化 `/Featureflow`：模糊需求细分为 `must-brainstorm / should-brainstorm`
