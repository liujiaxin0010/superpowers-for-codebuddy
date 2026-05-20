# GitLab CI 强门禁 + gitlab-bridge 对接层设计

- 状态: Approved（设计经多轮确认，进入实施）
- 创建日期: 2026-05-20
- 作者: Boss + Claude
- 分支: `claude/gitlab-ci-gate`

## 1. 背景与目标

Featureflow 当前所有门禁（process-gatekeeper、质量门禁）均为「协议驱动」——靠 AI 自觉执行，无外部系统强制（白皮书 §13.1 已承认）。目标：把门禁从「协议」升级为「系统强制」，并为后续需求 intake / 知识库 / 度量打通 GitLab 对接基础。

约束（已确认）：

- 目标平台：内网自建 GitLab **Community Edition 14.8.2**
- AI 访问 GitLab：**仅通过 MCP server**，选定 `@zereight/mcp-gitlab@2.1.12`
- 架构方向：优先复用 GitLab 原生能力；GitLab 对接收敛到单一隔离层，保证可移植

## 2. 架构：gitlab-bridge 隔离层

```
核心工作流（44 skills，不变）
        │ 只依赖抽象动作，不知道 GitLab/MCP 存在
   gitlab-bridge skill   ← 唯一对接层，封装所有 MCP 调用
        │ bridge.probe 探测 MCP 工具可用性
   ┌────┴────┐
   MCP 可用   MCP 不可用 → 本地 docs/ 降级模式
```

三条原则：

1. 复用 GitLab 原生（CI/CD、Issues、Wiki、Milestones、Pipelines）
2. 所有 GitLab 交互收敛到 `gitlab-bridge` 一个 skill
3. 优雅降级：bridge 不可用时回退本地 `docs/` 文件模式；移植到非 GitLab 环境只改 bridge

## 3. CE 14.8.2 核心约束与取舍

CE 缺失 EE 功能，取舍如下：

| EE 功能 | CE 替代 |
|---|---|
| Push Rules（commit 规范强制）| CI job `verify:commit-msg`，失败则流水线红 |
| MR Approval Rules（强制 N 人审批）| Protected Branches 限「Allowed to merge: Maintainers」+ MR 模板 checklist |
| SAST / Code Quality widget | 后续可在 CI 自带开源工具，P0 不做 |

**核心结论**：CE 环境下 **CI Pipeline 是唯一可靠的强门禁载体**。所有强制项（门禁证据、commit 规范、质量检查）统统做成 `.gitlab-ci.yml` 的 job——流水线红 →「Pipelines must succeed」→ MR 合不了。

CE 14.8.2 可用：CI/CD Pipelines、Protected Branches、MR「Pipelines must succeed」「All threads must be resolved」、Issues/Boards/Wiki/Milestones、API v4。

## 4. MCP server 前置（P0 第 0 步）

`@zereight/mcp-gitlab@2.1.12`，156 工具，支持 self-hosted。内网落地要求：

- **自建 Docker 镜像**（`zereight050/gitlab-mcp`）推到内网 registry，或推 npm 包到内网 registry；版本锁 `2.1.12`，禁用 `latest`
- 配置：`GITLAB_API_URL=https://内网域名/api/v4`、`GITLAB_PERSONAL_ACCESS_TOKEN`（scope: api）、`USE_PIPELINE=true`、`USE_GITLAB_WIKI=true`、`USE_MILESTONE=true`
- 初期 `GITLAB_READ_ONLY_MODE=true`，探测与只读验证通过后再放开写
- CE 14.8.2 上 Work Items 类、GraphQL 新 type、MR Approval 强制类工具不可用——由 `bridge.probe` 探测标记，方案不依赖它们

## 5. 新增 / 修改文件清单

```
.codebuddy/
├── skills/
│   ├── gitlab-bridge/                       [新增]
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── mcp-setup.md                 内网部署 zereight/gitlab-mcp 指南
│   │       └── capability-map.md            抽象动作 ↔ MCP 工具映射 + CE 兼容表
│   └── ci-integration/                      [新增]
│       ├── SKILL.md
│       └── templates/
│           ├── gitlab-ci.yml.template
│           ├── gitlab-setup-checklist.md.template
│           ├── merge_request_template.md
│           ├── commit-msg-lint.ps1
│           └── commit-msg-lint.sh
├── commands/
│   └── ci-setup.md                          [新增]
└── skills/finishing-branch/SKILL.md         [修改] 接入 bridge 的 MR 回查
```

文档：README.md、CODEBUDDY.md 增补 `/ci-setup`。

## 6. gitlab-bridge skill 设计

**抽象动作**（其他 skill 只调这些）：

| 动作 | 用途 | MCP 工具 | 降级 |
|---|---|---|---|
| `bridge.probe` | 探测 MCP 工具清单，生成 capability map | （列出工具） | —— |
| `intake.list/get` | 拉 GitLab Issues | `list_issues`/`get_issue` | 读 `docs/backlog/` |
| `mr.create/comment/status` | MR 创建/评论/查状态 | `create_merge_request`/notes/`get_merge_request` | 输出人工提示 |
| `pipeline.status` | 查流水线状态 | `get_pipeline`/`list_pipeline_jobs` | 读 `docs/quality/last-quality-gate.json` |
| `ci.lint` | 校验 .gitlab-ci.yml 语法 | `validate_ci_lint` | 跳过 |
| `wiki.read/write` | 知识库读写 | `get_wiki_page`/`create_wiki_page` | 读写 `docs/knowledge/` |
| `metrics.pipelines` | 流水线历史 | `list_pipelines` | 读 `docs/metrics/` |

**强制协议**：skill 被调用时第一步永远执行 `bridge.probe`——探测当前 MCP server 实际可用工具，每个动作按结果标记 available / degraded / unavailable。后续动作只走 available 集。

## 7. ci-integration skill + 产物设计

**① `gitlab-ci.yml.template`** —— 三 stage：

```yaml
stages: [gate, quality, verify]
gate:process    → 跑 check-gates（校验 spec/plan/gateStatus 证据齐备）
quality:check   → 跑 check-quality（通过率/覆盖率/文档同步），产出 artifact
verify:commit-msg → 跑 commit-msg-lint（替代 Push Rules）
```

job 仅在 MR event 触发（`rules: if $CI_PIPELINE_SOURCE == "merge_request_event"`）；`image` 留占位，`/ci-setup` 时询问内网 registry 地址填入。

**② `gitlab-setup-checklist.md.template`** —— AI 生成、管理员去 GitLab 点：
- Protected Branches：master「Allowed to merge: Maintainers」「Allowed to push: No one」
- Settings→Merge requests：勾「Pipelines must succeed」「All threads must be resolved」

**③ `merge_request_template.md`** —— MR 模板，含门禁 checklist（弥补 CE 无强制审批）。

**④ `commit-msg-lint.ps1` / `.sh`** —— 校验 commit message：`<type>: <subject>` conventional 格式，type ∈ feat/fix/docs/refactor/test/chore/perf/build/ci；脚本注释说明如何加工单号正则。零外网依赖。

## 8. /ci-setup 命令

在使用方业务项目里运行，把 ci-integration 的 templates 实例化到该项目：

1. 经 gitlab-bridge 的 `bridge.probe` 确认 MCP 可用性
2. 询问内网 Docker registry 地址，填入 `.gitlab-ci.yml`
3. 生成 `.gitlab-ci.yml`、`.gitlab/merge_request_templates/featureflow.md`、`scripts/commit-msg-lint.*`、`docs/gitlab-setup-checklist.md`
4. 若 `ci.lint` 可用，调用校验生成的 `.gitlab-ci.yml` 语法
5. 输出后续人工步骤（部署 MCP server、执行 setup-checklist）

## 9. finishing-branch 接入

`finishing-branch` skill 收尾流程增加一步（软性、非阻断）：若 `gitlab-bridge` 可用，调用 `mr.status` / `pipeline.status` 查当前 MR 流水线状态，并经 `mr.comment` 把门禁结果摘要回贴到 MR。bridge 不可用时跳过，不阻断收尾。

## 10. 范围外（本次不做）

- 需求 intake（P0-2）、知识库接 Wiki（P1）、度量看板（P1）——本次只把 bridge 的对应动作定义好，命令留待后续
- SAST / 安全扫描接入 CI
- 不替 AI 去改 GitLab 项目设置（出 checklist，人执行）
- 不在引擎仓库自身放 `.gitlab-ci.yml`（引擎托管在 GitHub；引擎只提供模板与能力）
- 架构图 `docs/architecture/*` 全量刷新另行处理

## 11. 验证策略

无自动化测试，人工自检：

- [ ] `commit-msg-lint.ps1` / `.sh` 对合法/非法 commit message 各跑一次，退出码正确
- [ ] `gitlab-ci.yml.template` 经 YAML 解析无语法错误
- [ ] `bridge.probe` 协议在 SKILL.md 中定义完整，capability-map 覆盖全部抽象动作
- [ ] `/ci-setup` 命令步骤自洽，引用路径存在
- [ ] `grep` 确认 ci-integration / gitlab-bridge 无 `.lingma` 等错误路径引用
- [ ] finishing-branch 修改为软性接入，bridge 不可用不阻断
- [ ] README / CODEBUDDY 命令速查含 `/ci-setup`

## 12. 实施顺序

1. gitlab-bridge skill（SKILL.md + references/mcp-setup.md + references/capability-map.md）
2. commit-msg-lint.ps1 / .sh
3. ci-integration skill（SKILL.md + 4 个 template）
4. /ci-setup 命令
5. finishing-branch 接入 bridge MR 回查
6. README / CODEBUDDY 文档更新
7. 跑验证清单

## 13. 风险

| 风险 | 缓解 |
|---|---|
| 第三方 MCP（156 工具）有写权限风险 | 初期 `READ_ONLY_MODE=true`；写操作单独评估放开 |
| 内网拉不到公网 npm/镜像 | 自建内网镜像，版本锁 2.1.12 |
| CE 14.8.2 部分 MCP 工具不可用 | `bridge.probe` 探测确定可用子集，方案只依赖 REST v4 老牌端点 |
| MCP server 实际工具名与本设计假设有出入 | capability-map 标注为「预期映射」，首次 `bridge.probe` 后据实修正 |
