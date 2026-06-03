# PR #15 上库总结 —— Claude/gitlab ci gate

## 基本信息

| 项 | 值 |
|---|---|
| PR 编号 | **#15** |
| 标题 | Claude/gitlab ci gate |
| 源分支 → 目标分支 | `claude/gitlab-ci-gate` → `master` |
| 状态 | **MERGED**（2026-06-02） |
| 提交数 | **10 个 commit** |
| 文件改动 | **81 个文件，+5658 / −16 行** |
| 文件构成 | 新增 68（A） · 修改 13（M） · 删除 0 |
| 新增命令 | 9 个 |
| 新增 skill | 8 个（另扩展 bug-fix / code-review-standards / testcase 等） |

> PR 名义是「GitLab CI 强门禁」，实际是一条积累了 10 次提交的大型分支，围绕**内网 GitLab CE 14.8.2** 一次性落地了 **CI 门禁、AI 原生流程对齐（Phase A–D）、事件驱动集成、远程运维自愈** 四大块能力。

---

## 提交清单（按时间顺序）

| # | Commit | 类型 | 标题 |
|---|--------|------|------|
| 1 | `a016304` | docs | 新增 GitLab CI 强门禁 + gitlab-bridge 对接层设计 spec |
| 2 | `ecf5c66` | feat | 新增 GitLab CI 强门禁能力（gitlab-bridge + ci-integration + /ci-setup） |
| 3 | `f96a462` | feat | bug 修复上库 commit 规范 + CI 增加真实编译/单测阶段 |
| 4 | `6ad0de4` | docs | README 补充 GitLab MCP server 安装步骤 |
| 5 | `dc0950f` | feat | 对齐 AI 原生开发流程（Phase A–D）+ GitLab CE 14.8.2 CI/CD 适配 |
| 6 | `a0e2e91` | feat | 事件驱动 GitLab 集成（P0/P1，对标 Claude Code GitHub）+ 新建/扩展最佳实践教程 |
| 7 | `7375551` | docs | 新增 GitLab Runner 分步部署指导（Windows shell + Linux Docker runner） |
| 8 | `d32ad1c` | feat | /runner-deploy 经 SSH MCP 远程部署 GitLab Runner（只给服务器地址） |
| 9 | `eb8c718` | feat | /pipeline-watch 流水线自愈（监听→失败修复→重试直到通过） |
| 10 | `405bc2c` | docs | README 同步说明介绍（事件驱动/自愈/远程部署能力 + 文档链接） |

---

## 按主题分组的内容

### ① GitLab CI 强门禁 + 唯一对接层（PR 立项核心）
`a016304` · `ecf5c66` · `f96a462`

- **`gitlab-bridge` skill** —— GitLab 唯一对接层，封装 `@zereight/mcp-gitlab` MCP 调用，`bridge.probe` 探测可用性 + 优雅降级；含内网部署指南、能力映射表、CE 14.8.2 版本矩阵。
- **`ci-integration` skill + `/ci-setup`** —— 把流程/质量门禁做成 GitLab CI 流水线。CE 无 Push / Approval Rules，所有强门禁收口到 Pipeline——红了即阻断 MR 合并。
- 流水线由 3 阶段扩为 **5 阶段**：`gate → build(真实编译) → test(真实单测) → quality(消费 json) → verify`。
- **bug 修复上库规范**：`AC<工单号>: <说明>` 模板（Bug Id / Root Cause / Solution / Verification / Risk）；`commit-msg-lint` 支持「工单号 / Conventional」双格式（bash + PowerShell）。

### ② AI 原生开发流程对齐 Phase A–D + CE 14.8.2 适配
`dc0950f`

- **Phase A 交付自动化**：code-review 增量化（Baseline Commit / 审查立方 / Critical→Issue 闭环）；新增 `defect-tracking` + `/defect-loop`（标签状态机 + 双向同步）；`scheduled-automation` + `/schedule-setup`（7 类定时任务）。
- **Phase B 设计阶段**：`walkthrough`（串讲）+ `/walkthrough`；`spec-organization` + `/spec-check` + 7 个设计文档模板（README 三级 / 技术选型 / 核心流程 / DB / 配置）。
- **Phase C 规格活文档**：`spec-backfill` + `/spec-sync`（三层回填 + Merge-Back）。
- **Phase D 精细化**：`requirement-spec`；`testcase` 加 8 维度 + 五维评分；CI 7 原则。
- **CE 14.8.2 适配**：YAML 安全子集 + 版本能力矩阵 + 「未满足实现」清单 + Runner/Docker 前置。

### ③ 事件驱动 GitLab 集成（对标 Claude Code 的 GitHub `@claude`）
`a0e2e91`

- **`event-triggers` + `/event-setup`** —— GitLab Webhook 事件驱动取代轮询：MR 评论 `/code-review`、打 `ai:review` 标签即可召唤 AI。
- 行内审查（`mr.discussion`）、commit status 贴 MR、可选 AI 审查 pipeline job、幂等（MR iid+sha）+ 并发控制 + `CI_JOB_TOKEN` 防循环。
- 新增 **最佳实践教程**（新建项目 A / 老项目扩展 B / 结合 GitLab C）。

### ④ 远程运维自动化（自愈 + 远程部署）
`7375551` · `d32ad1c` · `eb8c718`

- **`/runner-deploy`** —— 只给服务器地址，经 SSH MCP 探测 OS → 选 executor → 取注册令牌 → 装/注册/验证 Runner（含远程特权预演确认、令牌不落盘）。
- **`/pipeline-watch`** —— 流水线自愈：监听失败 → 取日志分类（代码 vs flaky）→ 最小修复 → 重推重触发，**有界**（默认 ≤3 次，触达数据/安全门禁即升级人工，拒绝删测试凑绿）。

### ⑤ 文档同步收尾
`6ad0de4` · `405bc2c`

- README 补充 GitLab MCP server 安装步骤；最后一次提交把事件驱动 / 自愈 / 远程部署能力写进 README 增强清单与文档索引。

---

## 沉淀的设计文档

| 文档 | 内容 |
|---|---|
| `docs/specs/2026-05-20-gitlab-ci-gate-design.md` | CI 强门禁设计 |
| `docs/specs/2026-06-02-ai-flow-alignment-roadmap-design.md` | Phase A–D 对齐路线 |
| `docs/specs/2026-06-02-event-driven-integration-design.md` | 事件驱动集成 |
| `docs/playbooks/best-practices-tutorial.md` | 最佳实践教程（654 行） |

---

## 一句话总结

> 这个 PR 把项目从「协议驱动的软门禁」升级为「GitLab CI 系统强制门禁」，并围绕内网 GitLab CE 14.8.2 一次性补齐了 AI 原生开发全流程（需求 → 设计 → 编码 → 审查 → 缺陷 → 交付）的 **9 个新命令 / 8 个新 skill**，外加事件驱动触发、流水线自愈、远程 Runner 部署三项对标 GitHub 的运维自动化能力。

---

*本文档由对 PR #15（`a016304..405bc2c`）的提交分析自动整理。*
