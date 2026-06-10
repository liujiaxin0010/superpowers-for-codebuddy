请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/event-triggers/SKILL.md`（事件驱动触发体系）
2. `.codebuddy/skills/gitlab-bridge/SKILL.md`（GitLab 对接层）
3. `.codebuddy/skills/scheduled-automation/SKILL.md`（轮询兜底关系）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在当前业务项目里接入**事件驱动触发**：用 GitLab Webhook 把 MR/评论/label/pipeline 事件实时映射成 Featureflow 命令，取代 `scheduled-automation` 的高频轮询；并让协作者在 MR 评论 `/code-review` 等或打 `ai:review` 标签即可召唤 AI。

执行步骤：

1. **环境确认**：
   - 项目根目录已含 `.codebuddy/`，且已跑过 `/ci-setup`（MR 门禁就绪）
   - 不在引擎仓库（superpowers-for-codebuddy）自身运行——只提供技能与模板
   - 有可常驻的内网接收器主机（与 CodeBuddy CLI 同机最简单）
   - 缺失 → 输出 `BLOCKED` 并说明

2. **bridge 探测 + 写权限确认**：
   - 经 `gitlab-bridge` 执行 `bridge.probe`
   - 确认 `webhook.*` 是否有对应 MCP 工具；无则后续第 5 步改走 REST/UI 注册（不阻断）
   - 写动作类触发（合并/改 Issue/行内评论）需 `GITLAB_READ_ONLY_MODE=false`；仍只读 → 提示 Boss 放开，未放开则只登记只读类触发（如 `/code-review` 仅产报告）

3. **选择部署形态 + 采集参数**（询问 Boss，一次问清）：
   - 接收器运行方式：systemd / pm2 / 容器（推荐常驻 + 自启；Windows 主机用 NSSM 或 pm2-windows）
   - 业务项目绝对路径 `<PROJECT_DIR>`、CodeBuddy CLI 调用方式 `<CODEBUDDY_CLI>`
   - 监听端口、反向代理/内网地址（GitLab 能 POST 到的 URL）
   - `X-Gitlab-Token` 密钥（生成强随机串，走环境变量 `GITLAB_WEBHOOK_SECRET`）
   - 触发 allowlist 取舍（评论命令 / 标签 / 是否开 MR 自动审查 / 是否开 pipeline 失败自修）
   - 可选 `allowedActors`（限制谁能触发写动作）

4. **实例化产物**（从 `event-triggers/templates/` 落到业务项目）：
   - `event-triggers.config.json` ← `event-triggers.config.sample.json`，替换 `<PROJECT_DIR>` / `<CODEBUDDY_CLI>`，按取舍裁剪 `triggers`
   - `webhook-receiver.js` ← 模板（如需改 CLI 调用形态，改 `dispatch()`）
   - 接收器进程管理文件（systemd unit / pm2 ecosystem），注入 `GITLAB_WEBHOOK_SECRET`

5. **注册 Webhook**：
   - `webhook.register` 可用 → 经 `gitlab-bridge` 注册：URL=接收器地址、Secret Token=同一密钥、勾选 **Comments / Merge request / Pipeline events**（按 allowlist），按需勾 Issues
   - 不可用 → 输出人工清单：GitLab 项目 `Settings → Webhooks` 手动添加（或 `curl POST /api/v4/projects/:id/hooks`），并 **Test** 一次

6. **输出后续人工步骤清单**：
   - 启动接收器服务（设密钥、设自启），确认内网可达、`X-Gitlab-Token` 已配
   - 放开 MCP 写权限（写动作触发才需要）的操作与 Boss 确认
   - **验证**：在测试 MR 评论 `/code-review`，确认事件到达、命令触发、结果经 `mr.discussion` 回贴
   - 在 `scheduled-automation` 把对应高频轮询（如 Task #17）调成**低频兜底**，避免与事件触发重复动作

补充约束：
- 接收器**先 200 应答再异步处理**；必配 `X-Gitlab-Token` 验签；只执行 allowlist 内触发
- 幂等键统一用 MR iid + 最新 commit sha（或 event id），与 `scheduled-automation` 共用，事件与轮询互不重复
- 所有改动仍走 MR + CI 门禁，**不直推 main**
- 全部 `<PLACEHOLDER>` / `<...>` 必须替换；密钥不落配置文件，只走环境变量
- 生成文档默认中文（代码、命令、路径可保留英文）

$ARGUMENTS
