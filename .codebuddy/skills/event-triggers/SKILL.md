---
name: event-triggers
description: 事件驱动触发体系技能。用 GitLab Webhook（MR、评论 note、label、pipeline、issue 事件）实时触发 Featureflow 命令，取代 scheduled-automation 的轮询；并支持协作者在 MR 评论 /code-review、/fix-bug 或打 ai:review 标签来召唤 AI（复刻 GitHub @claude 体验）。具体 GitLab 交互经 gitlab-bridge。用户提到“webhook/事件触发/评论触发/@claude 那样召唤/实时触发/别再轮询”时触发。
---

# 事件驱动触发体系（Event Triggers）

本技能回答的是：**怎样让 AI 由 GitLab 事件实时召唤，而不是靠 cron 每小时轮询。**

## 核心心智

1. **事件驱动优先，轮询兜底**：GitLab Webhook 把 MR/评论/label/pipeline 事件实时推给接收器 → 映射成 Featureflow 命令 → 调 CodeBuddy CLI。`scheduled-automation` 的轮询退化为"对账兜底"（防漏事件 / receiver 宕机时补扫），不再是主路径。
2. **复刻 `@claude` 体验**：协作者在 MR 里评论 `/code-review`、`/fix-bug`，或打 `ai:review` 标签，就能在 MR 上下文里召唤 AI——无需进 CodeBuddy 会话或等 cron。
3. **唯一对接层不变**：注册 webhook 与回贴结果仍经 `gitlab-bridge`；GitLab 平台细节不散落到本技能之外。
4. **白名单 + 验签 + 幂等**：只接受配置里 allowlist 的触发词/标签；用 `X-Gitlab-Token` 验签；同一事件去重，避免重复动作。

## 资源加载规则

- 判断"某事件该触发哪条命令"时，读 `references/trigger-map.md`
- 在业务项目落地接收器与配置时，读 `templates/webhook-receiver.js` 与 `templates/event-triggers.config.sample.json`
- 注册 / 列出 / 测试 webhook，或回贴 commit status / 行内评论时，经 `gitlab-bridge`（`webhook.*` / `commit.status` / `mr.discussion`）

## 何时使用

1. 业务项目首次接入事件驱动触发（`/event-setup`）
2. 想让协作者在 MR 评论 / 打标签召唤 AI
3. 想把 `scheduled-automation` 的高频轮询（Task #17 每小时）换成实时事件
4. pipeline 失败时希望即时触发自动修复，而非等下一次轮询

## 何时不用

1. 没有可对外暴露的接收器主机（内网无常驻服务）→ 退回 `scheduled-automation` 轮询
2. MCP/GitLab 写权限未放开（只读模式）→ 只能接收只读类触发（如产报告），合并/改 Issue 类阻断
3. 引擎仓库自身——只提供技能与模板，不放成品接收器配置

## 阻断条件

返回 `BLOCKED` 并说明：

1. 未配置 `X-Gitlab-Token` 密钥（无验签的公开端点 = 任意人可触发 AI 改库）
2. 触发映射不在 allowlist（拒绝执行未登记的命令，防注入）
3. 需要写动作（合并 / 改 Issue / 行内评论）但 `GITLAB_READ_ONLY_MODE=true`
4. 接收器无法定位 CodeBuddy CLI 或业务项目目录

## 触发链路

```text
GitLab 事件（MR / note / label / pipeline / issue）
   → Webhook POST 到接收器（templates/webhook-receiver.js）
   → ① 验签 X-Gitlab-Token   ② 解析 object_kind   ③ 按 trigger-map 映射命令
   → ④ allowlist + actor 权限校验   ⑤ 幂等去重（event/MR+sha 维度）
   → ⑥ 调 CodeBuddy CLI 执行映射到的 /命令（带 MR 上下文）
   → ⑦ 结果经 gitlab-bridge 回贴：mr.discussion 行内评论 / commit.status / mr.comment
```

接收器**先 200 应答再异步处理**，避免 GitLab webhook 超时重投。

## 支持的事件 → 命令（默认 allowlist，可在配置裁剪）

| 事件 | 条件 | 默认命令 |
|---|---|---|
| MR 评论 `note` | 正文首行 `/featureflow …` | `/Featureflow` |
| MR 评论 `note` | `/code-review` | `/code-review`（行内回贴）|
| MR 评论 `note` | `/fix-bug` | `/fix-bug` |
| MR `merge_request` | 加 `ai:review` 标签 | `/code-review` |
| MR `merge_request` | 加 `ai:fix` 标签 | `/defect-loop source=gitlab max=1` |
| MR `merge_request` | `action=open/reopen`（可选自动审查）| `/code-review` |
| `pipeline` | MR 流水线 `failed`（可选自动修复）| `/pipeline-watch`（流水线自愈）|

完整映射与扩展见 `references/trigger-map.md`。

## 与 scheduled-automation 的关系

| 维度 | event-triggers（本技能）| scheduled-automation（轮询）|
|---|---|---|
| 触发 | 实时 webhook 事件 | cron 定时扫描 |
| 延迟 | 秒级 | 分钟~小时级 |
| 角色 | **主路径** | **兜底/对账**：定时补扫漏掉的事件、receiver 宕机期间的积压 |
| 典型替换 | Task #17（MR 审查合并）实时化 | 保留低频版本做兜底 |

> 两者**共用同一套命令与幂等键**（MR iid + 最新 commit sha）。事件触发过的 MR，轮询发现已处理就跳过，绝不重复合并/重复修复。

## 安全约束

1. `X-Gitlab-Token` 密钥必配，接收器用 `crypto.timingSafeEqual` 等值比较
2. 只执行 allowlist 内的触发→命令映射；未登记的评论/标签一律忽略
3. 可选 `allowedActors`：限制谁能触发写动作（建议 ≥ Developer 成员；外部/访客评论不触发）
4. 接收器只在内网监听，置于反向代理/服务管理（systemd/pm2）之后；写动作仍受 `GITLAB_READ_ONLY_MODE` 与 Boss 确认约束
5. 接收器不内联密钥：PAT / token 仍走 `gitlab-bridge` 的 MCP env
6. 无人值守免确认：webhook 拉起的会话无 TTY，逐工具确认会让进程挂起；经 `automationSettings` / `--settings` 注入专用设置（`templates/automation-settings.sample.json`：allow 白名单 + deny 红线，deny 优先），把"免确认"限定在无人值守路径，交互式人工会话不受影响。注意这是 **CLI 工具层**确认，与 `GITLAB_READ_ONLY_MODE`（GitLab 写动作）是两层，别混淆。真正的护栏是 token 验签 + trigger/actor allowlist + MR/CI 门禁，而非逐工具弹窗

## 禁止事项

1. 不要暴露无验签的 webhook 端点——等于把"改库/合并 MR"的按钮交给任意人
2. 不要执行 allowlist 之外的触发——评论是用户可控输入，未登记即拒绝，防命令注入
3. 不要去掉幂等去重——webhook 会重投、轮询会并行，重复动作会重复合并/重复改库
4. 不要在事件链路里绕过 `gitlab-bridge` 直接调 MCP/REST——回贴与注册都走对接层，保持可移植
5. 不要在写权限未放开时谎报已合并/已改——只读模式下只能产报告并输出人工提示
6. 不要让事件触发直推 main——所有改动仍走 MR + CI 门禁（与 scheduled-automation 一致）
