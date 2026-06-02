请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/ci-integration/references/runner-deployment-guide.md`（Runner 分步部署 + §E SSH MCP 自动化）
2. `.codebuddy/skills/ci-integration/references/gitlab-server-setup.md`（Runner / Docker 决策）
3. `.codebuddy/skills/gitlab-bridge/SKILL.md`（取注册令牌 + 验证 runner online）
4. `.codebuddy/skills/data-safety/SKILL.md`（远程特权执行的安全约束）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
给定一个服务器地址，经 **SSH MCP** 远程把它部署成 GitLab Runner（探测 → 选 executor → 取令牌 → 装 / 注册 / 配 → 验证），**Boss 只需提供地址**。命令本体见 `runner-deployment-guide` §A/§B，远程执行与安全见 §E。

执行步骤：

1. 解析参数：`<服务器地址>`（必填，缺 → `BLOCKED`）；可选 `executor=auto|shell|docker`、`tags=`、`description=`、`token=`（不填则经 `gitlab-bridge` 取）。
2. **`ssh.probe` 连通**：不可用 → 降级：输出对应 OS 的手动命令清单（§A/§B）并停止，不阻断交付。
3. **探测**（`ssh.exec`）：OS（`uname -s` / `ver`）、arch、是否有 `sudo`、是否已装 `docker` / `gitlab-runner` / 已注册 runner；写 `docs/progress.md`。
4. **选 executor**：`auto` → Linux=docker、Windows=shell（按 §0.3）；尊重 `executor=` 覆盖。
5. **取 URL + registration token**：优先 `gitlab-bridge`（项目 `runners_token`）；取不到 → 一次性向 Boss 索取（不落盘）。注意 CE 14.8.2 用 registration token，不是 16+ 的 authentication token。
6. **生成命令计划**：按 §A（Windows shell）或 §B（Linux docker），每步带**幂等守卫**（已装 / 已注册则跳过）。
7. **预演确认（硬门禁）**：输出完整命令清单（含 `sudo` / 安装 / 注册 / 改 `config.toml`），等 Boss 明确确认；未确认 → **不执行任何写动作**。
8. **执行**：`ssh.exec` / `ssh.upload` 逐步执行；回显输出与退出码；首个错误即停并报告。
9. **验证**：远程 `gitlab-runner verify` + 经 `gitlab-bridge` 确认 runner online；可选触发一次测试 MR。
10. **报告 + 衔接**：执行清单、runner 状态、下一步（回 `/ci-setup` 按所选 executor 适配 `.gitlab-ci.yml`；docker executor 保留 `image:`/`services:`，shell 删之并切 `.ps1`）；更新 `docs/progress.md`。

补充约束：
- **幂等可重跑**：不重复安装 / 注册；重跑只补未完成项。
- **凭据不落盘**：registration token 与 SSH 凭据不写进远程文件、日志、仓库。
- **破坏性操作二次确认**：卸载 / 删容器 / 改系统服务等需 Boss 显式再确认（数据铁律）。
- **内网离线**：二进制 / 镜像从内网镜像站 / registry 取（同 §A/§B）。
- **全程可降级**：SSH MCP 不可用即退化为手动命令清单，不阻断（只是不自动）。
- AI 审查专用 runner（P1-5）：如需，`tags=ai-review` 且镜像含 CLI + node。
- 生成 / 更新文档默认中文（代码、命令、路径可保留英文）。

$ARGUMENTS
