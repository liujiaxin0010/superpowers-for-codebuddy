# 能力映射表（抽象动作 ↔ MCP 工具）

本文件定义 `gitlab-bridge` 抽象动作到 `@zereight/mcp-gitlab` v2.1.12 工具的**预期映射**，以及 CE 14.8.2 兼容性。

> ⚠️ 这是「预期映射」。首次 `bridge.probe` 后，以 MCP server 实测暴露的工具名为准；如有出入，更新本表。

## 抽象动作映射

| 抽象动作 | 预期 MCP 工具 | CE 14.8.2 | 说明 |
|---|---|---|---|
| `bridge.probe` | （列出工具清单的元能力） | available | 探测 MCP server 暴露的工具 |
| `intake.list` | `list_issues` | available | 拉取 Issue 列表 |
| `intake.get` | `get_issue` | available | 取单个 Issue 详情 |
| `issue.create` | `create_issue` | available（需非只读）| 创建 Issue（缺陷收录）|
| `issue.update` | `update_issue` | available（需非只读）| 改标签 / 状态（`bugfix:*` 状态机）|
| `issue.note` | `create_issue_note` | available（需非只读）| Issue 评论 |
| `mr.create` | `create_merge_request` | available（需非只读）| 创建 MR |
| `mr.comment` | `create_merge_request_note` / discussion 类工具 | available（需非只读）| 给 MR 贴评论 |
| `mr.status` | `get_merge_request` | available | 查 MR 状态、合并状态 |
| `mr.merge` | `merge_merge_request` | available（需非只读）| 合并 MR（squash / remove-source-branch）|
| `pipeline.status` | `get_pipeline` / `list_pipeline_jobs` / `get_pipeline_job_output` | available（需 `USE_PIPELINE=true`）| 查流水线与 job |
| `ci.lint` | `validate_ci_lint` | available | 校验 `.gitlab-ci.yml` 语法 |
| `wiki.read` | `get_wiki_page` / `list_wiki_pages` | available（需 `USE_GITLAB_WIKI=true`）| 读 Wiki |
| `wiki.write` | `create_wiki_page` / `update_wiki_page` | available（需 `USE_GITLAB_WIKI=true`，且非只读模式）| 写 Wiki |
| `metrics.pipelines` | `list_pipelines` | available（需 `USE_PIPELINE=true`）| 流水线历史 |
| `mr.discussion` | `create_merge_request_thread` / discussion 类工具（带 `position`）| available（需非只读）| 行内 diff 评论（指定 `new_path`+`new_line`），落 MR 讨论线程；P0-3 行内审查 |
| `commit.status` | `set_commit_status` / `create_commit_status` 类工具 | available（需非只读）| 外部检查状态贴到 commit/MR（`pending/running/success/failed`）；P1-6 |
| `webhook.list` / `webhook.register` / `webhook.test` | （MCP 多无 hook 管理工具）| degraded | 多数 MCP 未暴露 hook 工具 → 经 REST v4 `POST /projects/:id/hooks` 或 UI 注册；事件由 `event-triggers` 的 receiver 接收 |

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
| `wiki.write` / `mr.create` / `mr.comment` / `mr.merge` | `GITLAB_READ_ONLY_MODE=false`（写操作） |
| `issue.create` / `issue.update` / `issue.note` | `GITLAB_READ_ONLY_MODE=false`（写操作） |
| `mr.discussion` / `commit.status` | `GITLAB_READ_ONLY_MODE=false`（写操作） |

> 缺陷闭环（`defect-tracking`）与定时自动化（`scheduled-automation`）依赖 `issue.*` / `mr.merge` 等写动作——上线前必须把 `GITLAB_READ_ONLY_MODE` 改为 `false`，且经 Boss 确认（见 mcp-setup.md「写操作阶段」）。

开关未开 → 对应工具不暴露 → `bridge.probe` 标记该抽象动作 `unavailable`。

## 降级映射（MCP 不可用时）

| 抽象动作 | 本地降级行为 |
|---|---|
| `intake.list` / `intake.get` | 读 `docs/backlog/` 下的需求卡文件 |
| `issue.create` | 写 `docs/backlog/缺陷卡-{slug}.md`，标识待人工同步 GitLab |
| `issue.update` / `issue.note` | 更新本地缺陷卡的标签/状态/评论段，不阻断 |
| `mr.create` / `mr.comment` | 输出人工操作提示，不阻断 |
| `mr.merge` | 输出人工合并提示（含 squash / remove-source-branch 建议），不自动合并 |
| `mr.status` / `pipeline.status` | 读 `docs/quality/last-quality-gate.json` |
| `ci.lint` | 跳过，提示人工在 GitLab CI Lint 页面校验 |
| `wiki.read` / `wiki.write` | 读写本地 `docs/knowledge/` |
| `metrics.pipelines` | 读 `docs/metrics/` |
| `mr.discussion` | 退化为 `mr.comment` 普通评论；再不行把审查意见写本地报告 + 人工提示 |
| `commit.status` | 写 `docs/quality/` 状态文件，输出人工提示，不阻断 |
| `webhook.*` | 经 curl REST `/projects/:id/hooks` 或 UI 注册；接收侧由 `event-triggers` 的 `webhook-receiver` 兜底，事件驱动不可用时回退 `scheduled-automation` 轮询 |

## probe 后修正流程

首次 `bridge.probe` 完成后：

1. 对比实测工具清单与本表「预期 MCP 工具」列
2. 工具名不一致 → 更新本表对应行
3. 出现本表未列的相关工具 → 评估是否纳入抽象动作
4. 预期 available 但实测缺失 → 检查功能开关，或标记 unavailable
