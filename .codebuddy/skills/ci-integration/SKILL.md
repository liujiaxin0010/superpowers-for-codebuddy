---
name: ci-integration
description: 把 Featureflow 流程门禁与质量门禁接入 GitLab CI/CD 流水线，将「协议驱动」的软门禁升级为「系统强制」的硬门禁。用于在业务项目里生成 .gitlab-ci.yml、MR 模板、commit message 校验脚本和 GitLab 项目设置清单。目标平台 GitLab Community Edition 14.8.2——CE 下 CI Pipeline 是唯一可靠的强门禁载体。用户提到"接 CI/配流水线/门禁上 CI/ci-setup"时触发。不负责 GitLab API 交互（那是 gitlab-bridge），不负责本地 git 操作。
---

# CI 门禁集成（CI Integration）

本技能回答的是：**怎样让 Featureflow 的门禁不再依赖 AI 自觉，而是由 GitLab CI 系统强制执行。**

## 核心心智：CE 环境下，Pipeline 是唯一强门禁载体

Featureflow 原有门禁（process-gatekeeper、质量门禁）都是「协议驱动」——靠 AI 在命令流程里自觉调用，没有外部系统拦截。AI 可以跳过，没人拦得住。

GitLab **Community Edition** 缺失 EE 的 Push Rules、Approval Rules、Security widget。CE 唯一能「阻断合并」的机制是 **MR 设置「Pipelines must succeed」**。

因此核心策略：**所有想强制的门禁，统统做成 `.gitlab-ci.yml` 里的 job。** 流水线红 → 不满足「Pipelines must succeed」→ MR 合不了。一个 pipeline 收口全部强门禁。

## 资源加载规则

执行 `/ci-setup`、需要生成产物时，按需读取 `templates/` 下对应文件：

- `templates/gitlab-ci.yml.template` —— 三阶段门禁流水线
- `templates/gitlab-setup-checklist.md.template` —— GitLab 项目设置清单（人工执行）
- `templates/merge_request_template.md` —— MR 模板（含门禁 checklist）
- `templates/commit-msg-lint.ps1` / `.sh` —— commit message 规范校验脚本

校验生成的 `.gitlab-ci.yml` 语法时，经 `gitlab-bridge` 的 `ci.lint` 动作。

## 何时使用

1. 业务项目首次接入 Featureflow 门禁到 GitLab CI（`/ci-setup`）
2. 调整门禁流水线阶段或规则
3. 排查「门禁没有真正阻断 MR」的问题

## 何时不用

1. 需要直接调 GitLab API（拉 issue、查流水线）——用 `gitlab-bridge`
2. 引擎仓库自身——引擎托管在 GitHub，只提供模板与能力，不放成品 `.gitlab-ci.yml`
3. 目标平台不是 GitLab——本技能产物专为 GitLab CI

## 门禁流水线设计

五个 stage：

| stage / job | 跑什么 | 对应门禁 |
|---|---|---|
| `gate:process` | `check-gates.sh` | 流程门禁：门禁资产与命令接线完整 |
| `build:compile` | 项目构建命令 | 编译检查：真实执行构建，编译失败即阻断 |
| `test:unit` | 项目测试命令 | 单元测试：真实运行测试，产出 `test-summary.json` |
| `quality:check` | `check-quality.sh` | 质量门禁：消费 `test-summary.json` 判通过率/覆盖率/文档同步 |
| `verify:commit-msg` | `commit-msg-lint.sh` | commit 规范（替代 CE 缺失的 Push Rules）|

`build` / `test` 阶段真实编译并运行单测——这是「质量门禁」的证据来源。若 CI 只消费一个外部生成的 `test-summary.json`，门禁就建立在可能过时或造假的文件上。`build:compile` / `test:unit` 的命令由 `/ci-setup` 按项目技术栈填入。

流水线仅在 MR event 触发。任一 job 失败 → 流水线红 → MR 阻断。

## CE 14.8.2 取舍

| EE 功能 | CE 替代方案 |
|---|---|
| Push Rules（commit 规范强制）| `verify:commit-msg` job |
| Approval Rules（强制 N 人审批）| Protected Branches 限「Allowed to merge: Maintainers」+ MR 模板 checklist |
| Security / Code Quality widget | 后续可在 CI 自带开源工具，当前不做 |

## /ci-setup 产物

在业务项目运行 `/ci-setup` 后产出：

1. `.gitlab-ci.yml` —— 由模板实例化，替换全部占位符（内网 registry 镜像、`BUILD_COMMAND`、`TEST_COMMAND`）
2. `.gitlab/merge_request_templates/featureflow.md` —— MR 模板
3. `scripts/commit-msg-lint.sh`（及 `.ps1`，Windows runner 用）
4. `docs/gitlab-setup-checklist.md` —— 由模板实例化，交 Maintainer 人工执行

## 渐进接入

`test:unit` 须产出 `docs/quality/test-summary.json` 供 `quality:check` 消费。若项目测试框架不直接产出该格式、转换步骤尚未配好，`quality:check` 会因缺文件阻断——此时可临时给 `quality:check` 设 `allow_failure: true` 渐进接入，待 `test:unit` 稳定产出 JSON 后改回强制。`gate:process`、`build:compile`、`test:unit`、`verify:commit-msg` 应一开始就强制。

## 禁止事项

1. 不要只生成 `.gitlab-ci.yml` 而不交付设置清单——没有「Pipelines must succeed」，流水线红了也合得了，门禁形同虚设
2. 不要把任何 `<PLACEHOLDER:...>` 留在产物里——占位符未替换，CI 会拉不到镜像或执行空命令
3. 不要在引擎仓库根目录放成品 `.gitlab-ci.yml`——引擎在 GitHub，且应保持平台无关，只提供模板
4. 不要默认让全部 job `allow_failure`——那等于没有门禁；渐进接入只针对 `quality:check` 且需明示
5. 不要假设 Runner 是 Windows——默认 Linux + bash；Windows runner 需显式切到 `.ps1`
