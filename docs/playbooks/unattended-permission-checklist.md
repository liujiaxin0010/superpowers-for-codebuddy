# 无人值守免确认上线 Checklist

> 适用：CI 事件（webhook）/ 定时任务触发的 AI 请求要 **24×7 无人值守、不需人工确认**。
> 配套技能：`event-triggers`、`scheduled-automation`；权限样例：`.codebuddy/skills/event-triggers/templates/automation-settings.sample.json`。

## 0. 一句话认知（先记住，否则会反复踩）

**`-p` 管「不弹交互窗口」，`-y` 或 `permissions.allow` 才管「不要人确认」——两个都得有。**

- `-p`（headless / print）：非交互方式跑。**单独用 `-p` 并不免确认**，遇到要权限的工具照样停下来等 → 进程挂起。
- 免确认靠：① `permissions.allow` 白名单（受控，配 `deny` 红线）或 ② `-y`（全量自动批准）。

> 还有一层别混淆：本页讲的是 **CLI 工具确认层**（会不会卡弹窗）；`GITLAB_READ_ONLY_MODE` 是 **GitLab 写动作层**（能不能合 MR / 改 Issue），两回事。

## 1. 选方案（A / B 二选一）

| | 方案 A：全量放开 | 方案 B：受控放开（推荐） |
|---|---|---|
| 命令 | `codebuddy -p -y "<prompt>"` | `codebuddy -p "<prompt>"` + `permissions.allow` |
| 免确认范围 | 批准**一切** | 仅白名单内工具 |
| 工具层红线（`deny`） | ❌ 被 `-y` 绕过 | ✅ 保留（`rm -rf` / `--force` 等） |
| 作用域 | 仅带 `-y` 的那次调用（交互式会话不受影响） | 看设置放哪：`--settings` 仅该次；项目设置则全项目 |
| 适合 | 隔离/沙箱 runner，认门禁兜底 | 生产无人值守，要纵深防御 |

> 两者都靠真正的护栏兜底：**token 验签 + trigger/actor 白名单 + 全走 MR/CI 门禁 + 不直推 main**。

## 2. 落地步骤

### 方案 B（受控，推荐）
- [ ] 接收器/runner 主机放 `automation-settings.json`（复制 `automation-settings.sample.json`，**勿入库**）
- [ ] `permissions.allow` 至少含 `Bash`、`DeferExecuteTool`（截图点名的两个），按命令补 `Edit`/`Write`/`Read`/`Glob`/`Grep`/`mcp__gitlab__*`
- [ ] `permissions.deny` 留红线；`defaultMode` 用 `acceptEdits`，**切勿设 `plan`**
- [ ] 注入：`event-triggers.config.json` 填 `automationSettings`（或 `--settings <file>`）；`codebuddyFlags: ["-p"]`
- [ ] 若 CLI 不支持 `--settings`：把 `permissions.allow/deny` 合并进项目的 CodeBuddy 设置（CodeBuddy 自动读取）

### 方案 A（全量）
- [ ] 调用形态 `codebuddy -p -y "<prompt>"`：receiver 设 `codebuddyFlags: ["-p","-y"]` 或环境变量 `CODEBUDDY_FLAGS="-p -y"`；cron/CI 直接写 `-p -y`
- [ ] 确认 runner 隔离（非 root、内网、专用服务账号 PAT）——`-y` 无工具层红线，靠环境隔离 + 门禁兜底

### 通用（两方案都要）
- [ ] 无人值守只映射**自主型/产报告型**命令（`/code-review`、`/defect-loop`、`/spec-sync`）
- [ ] **别**映射 `/write-plan`、`/walkthrough`、`/brainstorm`、生产 `/release` 等"天生要人确认"的命令
- [ ] 接收器 `stdin` 用 `ignore`、`cwd` 用 spawn 选项（防 stdin 读阻塞 / 不依赖 `--cwd`）

## 3. 卡住时：杀进程重跑

已经挂起的会话不会自愈（改配置救不了正在等的那次）：
- [ ] 找到卡住的 CLI/receiver 进程并结束（如 `webhook-receiver.js` 拉起的 `codebuddy` 子进程）
- [ ] 应用上面的方案 A 或 B
- [ ] 重启 receiver / 重新触发一次事件

## 4. 最小验证（上线前必跑）

```bash
# ① 免确认是否生效：在业务项目目录手动跑一次，全程不应停下来要权限
cd <PROJECT_DIR> && codebuddy -p -y "/code-review mr=<某个测试 MR iid>"
#   方案 B 改成： codebuddy -p --settings <AUTOMATION_SETTINGS> "/code-review mr=<iid>"
#   预期：直接跑完产出审查，不出现"请授权 / 请告知如何继续"

# ② 提问降级是否安全（防方案/提问层挂起）：故意触发一个"拿不准"的场景
#   预期：进程【干净退出并留报告/回贴】，而不是无限期挂起等输入
```

- [ ] ① 通过：无任何"请授权 / 添加到 permissions.allow / 请告知如何继续"的停顿
- [ ] ② 通过：遇不确定时进程**退出**（异步落盘 `docs/pending-decisions.md` + 回贴 MR），不挂起

## 5. 排错速查

| 现象 | 原因 | 处置 |
|---|---|---|
| 带 `-p` 仍挂起、日志要"添加到 permissions.allow" | 只有 `-p`，没免确认 | 加 `-y`（A）或把该工具加进 `allow`（B） |
| 日志出现"请告知如何继续" | 命令撞到"询问 Boss"行为层 | 换自主型命令；遇不确定改异步退出（见 §2 通用） |
| 跑出计划后停住等批准 | 进了 plan 模式 | `defaultMode` 别设 `plan`，确认没传 plan 相关 flag |
| 能跑但合不了 MR / 改不了 Issue | 这是写动作层 | 放开 `GITLAB_READ_ONLY_MODE=false`（经确认），与本页无关 |
| `rm -rf` 之类被放行 | 用了 `-y`（绕过 `deny`） | 改方案 B，靠 `permissions.deny` 兜红线 |

> flag/字段名以 `codebuddy --help` 为准（本页 `-p` / `-y` 依据 CLI 在缺权限时给出的 `codebuddy -p -y "..."` 提示）。
