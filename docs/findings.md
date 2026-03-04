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
