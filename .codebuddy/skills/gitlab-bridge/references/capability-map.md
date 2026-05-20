# 能力映射表（抽象动作 ↔ MCP 工具）

本文件定义 `gitlab-bridge` 抽象动作到 `@zereight/mcp-gitlab` v2.1.12 工具的**预期映射**，以及 CE 14.8.2 兼容性。

> ⚠️ 这是「预期映射」。首次 `bridge.probe` 后，以 MCP server 实测暴露的工具名为准；如有出入，更新本表。

## 抽象动作映射

| 抽象动作 | 预期 MCP 工具 | CE 14.8.2 | 说明 |
|---|---|---|---|
| `bridge.probe` | （列出工具清单的元能力） | available | 探测 MCP server 暴露的工具 |
| `intake.list` | `list_issues` | available | 拉取 Issue 列表 |
| `intake.get` | `get_issue` | available | 取单个 Issue 详情 |
| `mr.create` | `create_merge_request` | available | 创建 MR |
| `mr.comment` | `create_merge_request_note` / discussion 类工具 | available | 给 MR 贴评论 |
| `mr.status` | `get_merge_request` | available | 查 MR 状态、合并状态 |
| `pipeline.status` | `get_pipeline` / `list_pipeline_jobs` / `get_pipeline_job_output` | available（需 `USE_PIPELINE=true`）| 查流水线与 job |
| `ci.lint` | `validate_ci_lint` | available | 校验 `.gitlab-ci.yml` 语法 |
| `wiki.read` | `get_wiki_page` / `list_wiki_pages` | available（需 `USE_GITLAB_WIKI=true`）| 读 Wiki |
| `wiki.write` | `create_wiki_page` / `update_wiki_page` | available（需 `USE_GITLAB_WIKI=true`，且非只读模式）| 写 Wiki |
| `metrics.pipelines` | `list_pipelines` | available（需 `USE_PIPELINE=true`）| 流水线历史 |

## CE 14.8.2 不可用工具（方案不依赖）

`bridge.probe` 应将下列标记为 `unavailable` 或 `degraded`：

| MCP 工具类 | 状态 | 原因 |
|---|---|---|
| `get_work_item` / `create_work_item` / `convert_work_item_type` | unavailable | Work Items 是 GitLab 15+ 的 API，14.8.2 没有 |
| `approve_merge_request` / `unapprove_merge_request` / `get_merge_request_approval_state` | degraded | CE 可 approve，但无强制审批数量，approve 不构成合并门禁 |
| GraphQL 执行类（依赖新 schema type） | degraded | 14.8 GraphQL schema 较老，新 type 缺失 |
| SAST / Code Quality / Security 相关 | unavailable | EE/Ultimate 功能 |

## 功能开关依赖

| 抽象动作 | 依赖的环境变量 |
|---|---|
| `pipeline.status` / `metrics.pipelines` | `USE_PIPELINE=true` |
| `wiki.read` / `wiki.write` | `USE_GITLAB_WIKI=true` |
| `wiki.write` / `mr.create` / `mr.comment` | `GITLAB_READ_ONLY_MODE=false`（写操作） |

开关未开 → 对应工具不暴露 → `bridge.probe` 标记该抽象动作 `unavailable`。

## 降级映射（MCP 不可用时）

| 抽象动作 | 本地降级行为 |
|---|---|
| `intake.list` / `intake.get` | 读 `docs/backlog/` 下的需求卡文件 |
| `mr.create` / `mr.comment` | 输出人工操作提示，不阻断 |
| `mr.status` / `pipeline.status` | 读 `docs/quality/last-quality-gate.json` |
| `ci.lint` | 跳过，提示人工在 GitLab CI Lint 页面校验 |
| `wiki.read` / `wiki.write` | 读写本地 `docs/knowledge/` |
| `metrics.pipelines` | 读 `docs/metrics/` |

## probe 后修正流程

首次 `bridge.probe` 完成后：

1. 对比实测工具清单与本表「预期 MCP 工具」列
2. 工具名不一致 → 更新本表对应行
3. 出现本表未列的相关工具 → 评估是否纳入抽象动作
4. 预期 available 但实测缺失 → 检查功能开关，或标记 unavailable
