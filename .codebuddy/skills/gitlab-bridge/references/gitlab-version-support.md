# GitLab 版本能力支持说明（基线 CE 14.8.2）

本文件回答：**方法论 / Featureflow 想要的每项 GitLab 能力，CE 14.8.2 能不能做；做不了的，缺在哪个版本 / 哪个 tier，引擎用什么替代闭合。**

> 平台基线：内网自建 **GitLab Community Edition 14.8.2**（2022-02）。AI 经 MCP server `@zereight/mcp-gitlab@2.1.12` 访问。
>
> 适配原则：只用 CE 14.8.2 已稳定能力；凡需更高版本或 EE(Premium/Ultimate) 的，标「未满足」并给 CE 替代。状态以 `bridge.probe` 实测与本实例文档为准（本表为预期基线）。

图例：✅ 原生支持 ｜ ⚠️ 受限/降级 ｜ ❌ 不支持（需更高版本或 EE）

## 1. 合并门禁

| 能力 | 需要版本 / Tier | CE 14.8.2 | CE 替代 | 引擎落点 |
|---|---|---|---|---|
| Pipelines must succeed | CE/Free（长期）| ✅ | — | ci-integration（核心硬门禁载体）|
| All threads must be resolved | CE/Free | ✅ | — | gitlab-setup-checklist |
| Protected Branches（限 Maintainers 合并）| CE/Free | ✅ | — | gitlab-setup-checklist |
| Merge when pipeline succeeds（即 auto-merge）| CE/Free（8.x+）| ✅ | — | scheduled-automation Task#17、defect-loop |
| MR Approval Rules（强制 N 人审批）| **EE Premium** | ❌ | Protected Branches +「Maintainers only」+ MR 模板 checklist | ci-integration |
| Push Rules（commit 规范在 push 时强制）| **EE Premium** | ❌ | `verify:commit-msg` CI job（流水线红→合不了）| ci-integration |
| Merge Trains | **EE Premium** | ❌（不依赖）| 串行合并 + 合并前 rebase | parallel-delivery 合并策略 |

## 2. CI/CD YAML / 流水线

| 能力 | 引入版本 / Tier | CE 14.8.2 | 说明 / 替代 |
|---|---|---|---|
| `merge_request_event` MR 流水线 | CE/Free 11.x+ | ✅ | `workflow:rules` 触发 |
| Pipeline Schedules（定时流水线）| CE/Free | ✅ | `$CI_PIPELINE_SOURCE == "schedule"` |
| `services:`（真实中间件）| CE/Free | ✅ | L3 e2e |
| `needs:`（DAG）| CE/Free 12.2+ | ✅ | |
| `parallel:matrix:` | CE/Free 13.3+ | ✅ | |
| `artifacts:reports:junit` | CE/Free | ✅ | |
| `artifacts:reports:coverage_report`（cobertura）| CE/Free 14.0+ | ✅ | 取代旧 `reports:cobertura` |
| `coverage:` 关键字正则 | CE/Free | ✅ | 项目级 regex 设置 15.0 移除 → 用 job 级关键字 |
| `!reference` | CE/Free 13.0+ | ✅ | |
| `id_tokens`（OIDC ID 令牌）| **16.4+** | ❌ | 密钥走 CI Variables（masked + protected）|
| `spec:inputs` / `include:inputs`（CI inputs）| **17.x** | ❌ | 参数化用 `variables` + `rules` |
| CI/CD components / catalog（`include:component`）| **17.0+** | ❌ | 复用走 `include:local/remote` + `extends` |
| `run:` steps 关键字 | **17.x** | ❌ | 用 `script` |
| `manual_confirmation` | **17.x** | ❌ | 手动 job 用 `when: manual` |

## 3. Issues / 缺陷管理

| 能力 | 需要版本 / Tier | CE 14.8.2 | CE 替代 |
|---|---|---|---|
| Issues REST API v4（classic）| CE/Free | ✅ | gitlab-bridge `intake.*` / `issue.*` |
| Issue 创建/改标签/评论 | CE/Free（需非只读）| ✅ | defect-tracking |
| 普通 Label（单冒号 `bugfix:in-progress`）| CE/Free | ✅ | defect-tracking 标签状态机用普通 label |
| **Scoped Labels（双冒号 `bugfix::in-progress`，原生互斥）** | **EE Premium** | ❌ | 用普通单冒号 label，互斥性由 AI 流程纪律保证（见下注）|
| Work Items API（`/work_items`、类型转换）| **15.x+** | ❌ | 用 classic Issues API；缺陷管理不需要任务层级 |

> **关键适配点**：`defect-tracking` 的 `bugfix:in-progress` / `bugfix:awaiting-review` 等是**单冒号普通 label**，CE 14.8.2 支持。**不要**用双冒号 scoped label（`bugfix::xxx`）——那是 EE Premium 功能；CE 上同一 Issue 理论上可同时贴多个 `bugfix:*`，需靠 AI 流程在状态流转时移除旧标签来保证互斥，而非依赖 scoped label 的原生互斥。

## 4. 安全扫描

| 能力 | 需要 Tier | CE 14.8.2 | CE 替代 |
|---|---|---|---|
| SAST（MR 安全 widget）| **Ultimate** | ❌ | `security-review` skill 本地做；可选 CI 内开源工具产 artifact（无 widget）|
| DAST | **Ultimate** | ❌ | 不做 |
| Dependency / Container Scanning | **Ultimate** | ❌ | 不做；依赖审计在 `security-review` 本地命令 |
| Secret Detection（MR widget）| **Ultimate** | ❌ | `security-review` 本地秘密扫描 |
| Code Quality（codeclimate widget）| CE/Free 13.2+ | ⚠️ | 可用但需 Docker-in-Docker runner；P0 不启用 |

## 5. 知识库 / 度量 / 接口

| 能力 | 需要版本 | CE 14.8.2 | 说明 |
|---|---|---|---|
| Wiki API | CE/Free | ✅ | 需 MCP `USE_GITLAB_WIKI=true` |
| Pipelines API（度量）| CE/Free | ✅ | 需 MCP `USE_PIPELINE=true` |
| GraphQL | CE 14.8 自带 | ⚠️ | schema 较老，新 type 缺失 → 抽象动作只走 REST v4 |
| Project Webhooks API（push/MR/note/pipeline 事件）| CE/Free | ✅ | `event-triggers` 事件驱动；MCP 多无 hook 工具 → REST `/projects/:id/hooks` 或 UI 注册（bridge `webhook.*` 降级）|
| MR diff discussions（行内 `position` 评论）| CE/Free | ✅ | 行内审查（P0-3）；REST `POST .../merge_requests/:iid/discussions` 带 `position`（bridge `mr.discussion`）|
| Commit Status API（外部检查状态）| CE/Free | ✅ | `commit.status` 贴 MR；REST `POST /projects/:id/statuses/:sha`；**非强制门禁**，强制仍靠 pipeline（CE 无 External Status Checks）|

## 6. 「未满足实现」清单（CE 14.8.2 无法原生满足，已用替代闭合）

| # | 未满足能力 | 缺在哪（版本/Tier）| 引擎替代 | 残留差异（需知悉）|
|---|---|---|---|---|
| 1 | 强制审批 | EE Premium（Approval Rules）| Protected Branches +「Maintainers only」+ MR 模板 checklist | 审批非系统强制，靠流程 + 人；恶意绕过靠权限收口 |
| 2 | commit 规范在 push 时拦截 | EE Premium（Push Rules）| `verify:commit-msg` CI job | 规则在 CI 阶段而非 push 时；本地坏 commit 能 push，但 MR 合不了 |
| 3 | 安全扫描 MR widget | Ultimate（SAST/DAST/Secret/Dep）| `security-review` 本地 + 可选 CI 开源工具 | 无 MR 内联安全 widget；扫描结果在报告/artifact |
| 4 | Work Items / 任务层级 | GitLab 15.x+ | classic Issues API | 无 epic/任务类型转换；缺陷闭环不需要 |
| 5 | OIDC 密钥 / CI 配置复用 | 16.4（id_tokens）/ 17.x（inputs/components）| CI Variables + `include`/`extends` | 无 OIDC；配置复用度略低 |
| 6 | scoped label 原生互斥 | EE Premium | 单冒号普通 label + AI 流程保证互斥 | 同一 Issue 理论可并存多个 `bugfix:*`，靠流转时移除旧标签 |

## 7. 升级影响（前瞻说明，不要求升级）

| 升级到 | 解锁 | 可简化 |
|---|---|---|
| 16.4+ | `id_tokens`（OIDC）| 密钥管理更安全 |
| 17.0+ | CI/CD components / inputs | 多项目 CI 配置大幅复用 |
| EE Premium | Push Rules + Approval Rules + Scoped Labels | 可去掉 `verify:commit-msg` 与 checklist 替代；标签互斥转原生 |
| Ultimate | SAST/DAST/Secret/Dep 扫描 widget | 安全门禁进 MR widget |

## 8. 自检

- 任何 GitLab 交互前先 `bridge.probe` 实测，不假设 EE 功能可用
- 生成 / 改 `.gitlab-ci.yml` 后核对 `ci-integration/references/ce-14.8.2-cicd-support.md` 自检清单
- 缺陷标签只用单冒号普通 label，状态流转时显式移除旧标签
- 本表与实测不符 → 以本实例 GitLab CI Lint / 文档为准，并更新本表（同 capability-map「预期映射」策略）
