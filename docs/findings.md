# Findings

## 2026-03-02

- [流程治理] 增加质量门禁脚本（通过率、覆盖率、文档同步）并接入执行收尾。
- [流程治理] `/extend` 与 `/write-plan` 强化为先判档再选流程，缺 `spec/tier` 直接阻断。
- [试运行] 新增 3 个需求场景的质量门禁试运行输入与记录。

## 2026-03-04

- [指南兼容] 新增 `spec/Me2AI + spec/AI2AI` 兼容目录，保持 `docs/*` 为主事实源。
- [命令扩展] 新增 `/research`、`/testcase`、`/code-self-check` 别名命令与对应技能。
- [门禁扩展] `gate-matrix` 与 `check-gates` 纳入新增命令接线校验。
- [质量门禁] `check-quality.ps1/.sh` 新增可选参数 `RequireAi2AiDocs`（默认 `false`）。

## 2026-03-09

- [流程合同化] 新增 `.codebuddy/templates/task-contracts/`，引入 `new-feature / bugfix / refactor / test / research / review-pr / issue-draft-pr / parallel-delivery` 八类任务合同模板。
- [门禁升级] `spec-lite`、`write-plan`、`execute-plan`、`fix-bug`、`test-gen`、`unified-test`、`code-review`、`status` 接入 TaskContract 视角。
- [文档整合] 新增 `docs/workflows/*` 与 `docs/playbooks/workflow-playbook.md`，吸收 `website` 仓库中的 Prompt Contract 与 workflow 模式。
- [项目更名] 将项目对外名称统一为 `Featureflow`，保留对上游 `Superpowers` 的来源说明。
- [命令落地] 新增 `/issue-draft-pr` 与 `/parallel-delivery` 斜杠命令，并接入主文档、门禁矩阵与命令清单。
- [技能体系] 新增 `task-contracts`、`issue-draft-pr`、`parallel-delivery` 三个 SKILL 目录，让新工作流在技能层可复用、可组合、可维护。
- [单入口封装] 新增 `devflow-router` 技能、`Featureflow` 总控代理与 `/Featureflow` 单命令入口，支持其他项目按“一入口”导入使用。
- [路由增强] `/Featureflow` 将模糊需求细分为 `must-brainstorm / should-brainstorm` 两档，避免在边界未收敛时直接进入规格或实现。

## 2026-03-13

- [GitNexus 适配] 将 GitNexus 自动安装的 `Exploring / Debugging / Impact Analysis / Refactoring` 四类 skill 映射到 CodeBuddy 既有命令与规则，不引入第二套技能事实源。
- [索引边界] 明确 `.claude/skills/`、`AGENT.md`、`CLAUDE.md` 仅为 GitNexus 提示产物，建议通过 `.gitnexusignore` 排除，避免污染项目代码图谱。
