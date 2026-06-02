---
name: gitlab-bridge
description: Featureflow 与 GitLab 之间的唯一对接层。用于经 MCP server（@zereight/mcp-gitlab）访问内网 GitLab 的 Issues、Merge Request、Pipeline、Wiki、Milestone——拉取需求、创建/评论 MR、查询流水线状态、读写知识库、采集度量。其他 skill 或命令需要任何 GitLab 操作时，统一调用本技能定义的抽象动作，不直接调 MCP 工具。用户提到"接 GitLab/拉 issue/查流水线/MR 状态/对接 MCP"时触发。不负责本地 git 分支操作（那是 version-control-branching）。
---

# GitLab 对接层（GitLab Bridge）

本技能回答的是：**Featureflow 怎样以一种「可移植、可降级、不绑死平台」的方式访问 GitLab。**

## 核心心智：唯一对接层 + 探测优先 + 优雅降级

GitLab 对接的复杂度（MCP 工具名、CE/EE 差异、版本兼容、内网部署）全部封装在本技能内。

- **唯一对接层**：所有 GitLab 交互只经本技能的抽象动作。其他 skill/命令调 `intake.list`、`mr.comment` 这类抽象动作，不知道底层是 MCP、是哪个 MCP server、GitLab 是什么版本。换平台时只改本技能一个文件——因为对接逻辑集中一处，核心工作流零改动。
- **探测优先**：任何抽象动作执行前，必须先 `bridge.probe`。不探测就调用 = 拿不确定的工具集赌运行时——MCP server 实际暴露哪些工具，取决于它的版本和功能开关，必须实测而非假设。
- **优雅降级**：MCP 不可用时回退本地 `docs/` 文件模式。降级是设计的一部分，不是故障——保证无 GitLab 环境下工作流仍能跑。

## 资源加载规则

首次部署 / 配置 MCP server、或排查连接问题时，再读取：

- `references/mcp-setup.md`（内网部署 @zereight/mcp-gitlab 指南）

执行 `bridge.probe` 或调用任一抽象动作前，再读取：

- `references/capability-map.md`（抽象动作 ↔ MCP 工具映射 + CE 14.8.2 兼容表）

需要判断「某能力 CE 14.8.2 能不能做、缺在哪个版本/tier、用什么替代」时，再读取：

- `references/gitlab-version-support.md`（GitLab 版本能力支持矩阵 + 「未满足实现」清单 + 升级影响）

不要在未确定要执行哪个动作时就把 references 全部读入。

## 何时使用

需要与 GitLab 发生任何交互时：

1. 拉取 / 查询 GitLab Issues（需求 intake）
2. 创建 MR、给 MR 贴评论、查询 MR 与流水线状态
3. 校验 `.gitlab-ci.yml` 语法
4. 读写 GitLab Wiki（团队知识库）
5. 采集流水线历史做度量

## 何时不用

1. 本地 git 操作（branch / commit / merge / worktree）——用 `version-control-branching`、`using-git-worktrees`
2. 纯本地文件读写——直接用文件工具，不必经本技能
3. 目标平台不是 GitLab——本技能仅对接 GitLab；其它平台需另写对接层

## bridge.probe 探测协议（强制前置）

任何 GitLab 抽象动作执行前，**必须先完成 `bridge.probe`**：

1. 确认 MCP server 可达（连接配置见 `references/mcp-setup.md`）
2. 列出该 MCP server 当前实际暴露的工具清单
3. 对照 `references/capability-map.md`，给每个抽象动作打标：
   - `available` —— 依赖的 MCP 工具存在且 CE 14.8.2 支持
   - `degraded` —— MCP 工具存在但 CE 14.8.2 行为受限（如审批类）
   - `unavailable` —— MCP 工具缺失或 CE 14.8.2 不支持（如 Work Items）
4. 探测结果在单次会话内可缓存复用，不必每个动作重复探测
5. 若 MCP server 完全不可达 → 全部动作进入「本地降级模式」

**探测结果与 `capability-map.md` 的预期映射不一致时**：以探测的实测结果为准，并提示 Boss 更新 `capability-map.md`。

## 抽象动作清单

其他 skill/命令只调用下列动作。具体 MCP 工具名见 `references/capability-map.md`。

| 抽象动作 | 用途 | CE 14.8.2 | 降级行为 |
|---|---|---|---|
| `bridge.probe` | 探测 MCP 工具可用性 | available | —— |
| `intake.list` / `intake.get` | 拉取 / 查询 GitLab Issues | available | 读本地 `docs/backlog/` |
| `issue.create` | 创建 GitLab Issue（缺陷收录）| available（需非只读）| 写本地 `docs/backlog/` |
| `issue.update` | 改 Issue 标签 / 状态 | available（需非只读）| 更新本地缺陷卡 |
| `issue.note` | 给 Issue 贴评论 | available（需非只读）| 追加本地缺陷卡 |
| `mr.create` | 创建 Merge Request | available（需非只读）| 输出人工创建提示 |
| `mr.comment` | 给 MR 贴评论 / discussion | available（需非只读）| 输出人工提示 |
| `mr.status` | 查询 MR 状态 | available | 读本地门禁产物 |
| `mr.merge` | 合并 MR（CI 绿 + 无冲突后）| available（需非只读）| 输出人工合并提示 |
| `pipeline.status` | 查询流水线 / job 状态 | available | 读 `docs/quality/last-quality-gate.json` |
| `ci.lint` | 校验 `.gitlab-ci.yml` 语法 | available | 跳过，提示人工校验 |
| `wiki.read` / `wiki.write` | 知识库读写 | available | 读写本地 `docs/knowledge/` |
| `metrics.pipelines` | 拉流水线历史 | available | 读本地 `docs/metrics/` |
| `mr.discussion` | 行内 diff 评论（指定文件+行）| available（需非只读）| 退化为 `mr.comment` 普通评论 |
| `commit.status` | 把外部检查状态贴到 commit/MR | available（需非只读）| 写本地状态文件 + 人工提示 |
| `webhook.list` / `webhook.register` / `webhook.test` | 注册/列出/测试 GitLab webhook（事件驱动触发）| degraded（多经 REST/UI）| 经 curl REST `/hooks` 或 UI 注册；回退轮询 |

## CE 14.8.2 边界

本技能目标平台为内网 GitLab **Community Edition 14.8.2**。已知不可用、本技能不依赖：

- Work Items 类工具（GitLab 15+ API）
- MR Approval Rules 强制类（EE 功能）——CE 可 approve，但不构成合并门禁
- 较新的 GraphQL type

抽象动作只依赖 GitLab REST API v4 的老牌端点（issues / merge_requests / pipelines / repository_files / wiki），CE 14.8.2 完整支持。

## 安全约束

1. 初期接入阶段，MCP server 必须配 `GITLAB_READ_ONLY_MODE=true`，只跑探测与只读动作
2. 写操作（`mr.create` / `wiki.write` 等）放开前，必须经 Boss 确认
3. 令牌最小权限：优先 **Project Access Token / 专用 bot**（项目级、可吊销、设过期），而非个人 `api` PAT；CI 侧用 masked+protected 变量；定期轮换；不复用管理员 token。详见 `references/mcp-setup.md`「令牌最小权限与轮换」

## 禁止事项

1. 不要绕过本技能直接调 MCP 工具——绕过会让 GitLab 依赖散落各处，换平台时无法收敛
2. 不要跳过 `bridge.probe` 直接调用抽象动作——未探测就调用，会在 CE 不支持的工具上运行时失败
3. 不要把探测结果硬编码进其他 skill——MCP server 版本/开关一变，硬编码即失效
4. 不要在 MCP 不可用时直接报错终止——必须走本地降级模式，否则无 GitLab 环境工作流瘫痪
5. 不要在未确认时放开 MCP 写权限——第三方 MCP server 拥有 156 个工具，含改文件、推 commit、merge MR
6. 不要假设 EE 功能可用——目标是 CE 14.8.2，审批规则 / 安全扫描 widget 等一律按不可用处理
