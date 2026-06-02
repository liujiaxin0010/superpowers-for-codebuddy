# 事件 → 命令 映射表

接收器（`templates/webhook-receiver.js`）按本表把 GitLab webhook 事件映射成 Featureflow 命令。映射是**白名单**：不在表里的事件/触发词一律忽略。配置在 `event-triggers.config.json` 的 `triggers` 段，可按项目裁剪。

## 1. MR 评论触发（`object_kind=note`，noteable=MergeRequest）

取评论正文**首行**，匹配 `^/<命令>[ 参数]`：

| 评论首行 | 映射命令 | 说明 |
|---|---|---|
| `/featureflow <需求>` | `/Featureflow <需求>` | 单入口路由 |
| `/code-review` | `/code-review`（行内回贴）| 审查当前 MR，意见经 `mr.discussion` 落到 diff 行 |
| `/fix-bug <描述>` | `/fix-bug <描述>` | 针对该 MR/分支修缺陷 |
| `/status` | `/status` | 回贴当前门禁/进度 |
| `/pending` | `/pending list` | 回贴待决策项 |

- 命令大小写不敏感；只取首行，其余正文作为补充上下文。
- `actor` = 评论者；受 `allowedActors` 约束（默认不限，建议限 ≥ Developer）。
- 幂等键：`note:<note_id>`（同一条评论只触发一次）。

## 2. MR 标签触发（`object_kind=merge_request`，labels 含目标标签）

| 标签 | 映射命令 | 说明 |
|---|---|---|
| `ai:review` | `/code-review` | 复刻"打标签即审查" |
| `ai:fix` | `/defect-loop source=gitlab max=1` | 自动修复并回 MR |

- 标签用**单冒号普通 label**（CE 14.8.2 无 scoped label，见 `gitlab-bridge/references/gitlab-version-support.md`）。
- 幂等键：`mr-label:<iid>:<label>:<last_commit_sha>`（同一标签+同一 commit 只触发一次；新 push 后可再触发）。

## 3. MR 动作触发（可选，默认开启自动审查）

| `object_attributes.action` | 映射命令 | 说明 |
|---|---|---|
| `open` | `/code-review` | MR 一开就自动审查（类比 GitHub auto review）|
| `reopen` | `/code-review` | 重开时重审 |
| `update`（含 push）| —（默认不触发，避免每次 push 都审）| 可在配置开启 |

- 幂等键：`mr:<iid>:<action>:<last_commit_sha>`。
- 不需要自动审查的项目，把 `triggers.mrAction` 置空即可。

## 4. 流水线触发（可选，默认开启失败自修）

| `object_kind=pipeline` 条件 | 映射命令 | 说明 |
|---|---|---|
| `status=failed` 且关联 MR | `/defect-loop source=gitlab max=1` | 即时触发自动修复，替代轮询等待 |

- 幂等键：`pipe:<pipeline_id>`。
- 注意防循环：自动修复 push 会再触发流水线——靠幂等键 + `scheduled-automation` 的"最多 3 次"修复上限收口（见 task-playbooks 公共机制）。

## 5. Issue 触发（可选）

| 条件 | 映射命令 | 说明 |
|---|---|---|
| `object_kind=issue` 新建且含 `ai:triage` 标签 | `/Featureflow`（分类）| 让单入口判类型再路由 |

## 参数与上下文传递

接收器把 MR 上下文（`mr=<iid>`、必要时 `sha`、`project`）追加到命令，供下游 `gitlab-bridge` 定位对象。具体 CLI 调用形态见 `templates/webhook-receiver.js` 的 `dispatch()`，按你的 CodeBuddy CLI 调用方式调整。

## 扩展原则

1. 新增触发必须同时：① 进 allowlist ② 定义幂等键 ③ 明确是否需要写权限
2. 写动作类（合并/改 Issue/行内评论）触发，必须在写权限放开（`GITLAB_READ_ONLY_MODE=false`）后才生效
3. 任何用户可控输入（评论正文）只用于"选命令 + 透传为上下文"，不直接拼进 shell
