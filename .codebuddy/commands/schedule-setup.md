请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/scheduled-automation/SKILL.md`（定时自动化体系）
2. `.codebuddy/skills/gitlab-bridge/SKILL.md`（GitLab 对接层）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在当前业务项目里，把 7 类定时任务接入调度器，让交付阶段 24×7 无人值守运行。

执行步骤：

1. **环境确认**：
   - 确认项目根目录已含 `.codebuddy/`，且已跑过 `/ci-setup`（MR 门禁就绪）
   - 不在引擎仓库（superpowers-for-codebuddy）自身运行——引擎只提供 runbook 与模板
   - 若缺失，输出 `BLOCKED` 并说明

2. **bridge 探测 + 写权限确认**：
   - 经 `gitlab-bridge` 执行 `bridge.probe`，确认 `mr.merge` / `issue.*` 写动作可用
   - 仍是只读模式（`GITLAB_READ_ONLY_MODE=true`）→ 提示 Boss：定时自动化依赖写动作，需放开只读并经确认；未放开则只能登记「只读类」任务（如 Task #4 审查仅产出报告）

3. **选择调度方式**（询问 Boss）：
   - 方式 A：CodeBuddy 原生定时任务能力（推荐）
   - 方式 B：系统 cron 调 `codebuddy` CLI
   - 方式 C：GitLab CE 14.8.2 原生 Pipeline Schedules（`CI/CD → 计划`，`$CI_PIPELINE_SOURCE == "schedule"` 触发）——纯 CI 类任务可直接用；AI 驱动类需 runner 能拉起 CLI
   - 采集参数：业务项目绝对路径、CLI 调用方式（方式 B/C）、各任务启停与时间偏好

4. **实例化调度配置**：
   - 基于 `scheduled-automation/templates/schedule-config.sample` 生成项目内配置
   - 替换 `<PROJECT_DIR>` / `<CODEBUDDY_CLI>` 等占位符
   - 任务错峰串行，避免多实例争抢资源

5. **输出后续人工步骤清单**：
   - 放开 MCP server 写权限（`GITLAB_READ_ONLY_MODE=false`）的操作与确认
   - 方式 A：在 CodeBuddy 定时任务界面登记；方式 B：写入服务器 crontab
   - 先手动触发一次 Task #4（只读、最安全）验证 runbook 跑通

补充约束：
- 所有定时任务的 GitLab 交互只经 `gitlab-bridge` 抽象动作
- 全部 `<PLACEHOLDER:...>` 必须替换，不得留在产物中
- Task #3 夜间发布只打 tag 触发流水线，不直接部署生产
- 生成文档默认中文

$ARGUMENTS
