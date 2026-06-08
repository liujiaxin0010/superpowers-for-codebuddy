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

- `templates/gitlab-ci.yml.template` —— 五阶段门禁流水线
- `templates/gitlab-setup-checklist.md.template` —— GitLab 项目设置清单（人工执行）
- `templates/merge_request_template.md` —— MR 模板（含门禁 checklist）
- `templates/commit-msg-lint.ps1` / `.sh` —— commit message 规范校验脚本

**生成或增强任何 `.gitlab-ci.yml` 前，必须先读** `references/ce-14.8.2-cicd-support.md`（CE 14.8.2 CI/CD 配置适配基线）——所有产物的 YAML 关键字必须落在该安全子集内，禁用 14.8 之后引入的特性（`id_tokens` / `spec:inputs` / CI/CD components 等）。

把基础 5 阶段门禁增强为完整质量流水线（lint / e2e / 覆盖率分层 / `-race` / deploy 阶段）时，读 `references/ci-quality-principles.md`（CI 质量 7 原则 + 三级测试体系 + CE 14.8.2 可用片段）。

判断「GitLab 服务器/Runner 要配什么、需不需要 Docker、docker vs shell executor」时，读 `references/gitlab-server-setup.md`（CI 能跑起来的服务器侧前置）。

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
| `verify:commit-msg` | `commit-msg-lint.sh` | commit 规范（替代 CE 缺失的 Push Rules）：AI 标签 `[AI-0\|AI-H\|AI-100]` 恰好一个 + `AC<数字>:`/Conventional 格式 |

`verify:commit-msg` 与团队服务端 AI 标签 hook 对齐——本地/CI 提前拦截，避免推送被服务端 `GL-HOOK-ERR` 拒绝。AI 标签必须作为 subject 前缀、有且仅有一个（缺失或多个均阻断）。

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

## 可选：AI 审查作为 pipeline job（P1-5）

默认 AI 代码审查**不是** pipeline job（CE 无审查 widget，且审查需 agent 运行时而非普通 runner），而是走 `scheduled-automation` Task #4 产 Critical Issue、经 `/defect-loop` 闭环。

若你愿意维护一个能拉起 CodeBuddy/Claude CLI 的专用 runner，可用 `templates/ai-review-job.yml.template` 把审查升级成**合并阻断 job**：

1. 该 runner 打 tag `ai-review`，镜像含 CLI + node；CLI 鉴权走 masked+protected CI 变量
2. 把模板的 `review` stage 合并进主 `stages:`（置于 quality 之后），拷入 `review:ai` job
3. `<PLACEHOLDER:AI_REVIEW_COMMAND>` 填 CLI 调用（如 `codebuddy -p --settings <AUTOMATION_SETTINGS> "/code-review mr=$CI_MERGE_REQUEST_IID"`）；runner 上无人值守须免逐工具确认：`-p` 非交互 + `permissions.allow` 白名单（`--settings` 指向专用设置，含 deny 红线，见 `event-triggers/templates/automation-settings.sample.json`），或最简用 `-p -y`（`-y` 自动批准所有，无护栏）；否则会话会卡在确认弹窗导致 job 超时；审查存在 🔴 严重问题 → 退出码非 0 → job 红
4. 默认 `allow_failure: true` 先观察；稳定后改 `false` → 严重问题即阻断 MR
5. 审查意见仍经 `gitlab-bridge` 的 `mr.discussion` 行内回贴、`commit.status` 贴状态（见 `/code-review` 步骤 11）

> 没有这种 runner 时，**不要**硬把审查塞进普通 runner 的 job——普通 runner 跑不起 agent。维持"定时任务产 Issue"路径即可。

## 流水线自愈（/pipeline-watch）

经 `gitlab-bridge` 监听某 MR 流水线，失败则取日志、定位根因、最小修复、重推、重试**直到通过**（有界，默认最多 3 次，到顶/不可修则升级人工）。协议（循环骨架、失败类型→修复策略、停止条件、安全幂等）见 `references/pipeline-self-heal.md`。

- 按需单 MR：`/pipeline-watch mr=<iid>`；批量无人值守：`scheduled-automation` Task #17；事件实时：`event-triggers` 的 `pipelineFailed`。三者共用同一自愈循环。
- 关键安全：只 push 源分支、有界重试、基础设施/flaky 不当代码改、自愈 push 用能触发流水线的身份（CI_JOB_TOKEN 防循环）。

## 禁止事项

1. 不要只生成 `.gitlab-ci.yml` 而不交付设置清单——没有「Pipelines must succeed」，流水线红了也合得了，门禁形同虚设
2. 不要把任何 `<PLACEHOLDER:...>` 留在产物里——占位符未替换，CI 会拉不到镜像或执行空命令
3. 不要在引擎仓库根目录放成品 `.gitlab-ci.yml`——引擎在 GitHub，且应保持平台无关，只提供模板
4. 不要默认让全部 job `allow_failure`——那等于没有门禁；渐进接入只针对 `quality:check` 且需明示
5. 不要假设 Runner 是 Windows——默认 Linux + bash；Windows runner 需显式切到 `.ps1`
6. 不要让 AI 自动 push 用 `CI_JOB_TOKEN` / trigger token 触发流水线——GitLab 防循环会使其**不触发** MR pipeline，等于绕过门禁；AI 提交用 PAT / Project Access Token，接入前用测试 MR 确认能拉起 5 阶段流水线（P1-8）
