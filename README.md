# Featureflow

> 给 CodeBuddy / 终端 AI 代理用的「开发工作流引擎」。一句话：**让 AI 按规矩干活，少返工、少摆烂、少越界。**

源自 [obra/superpowers](https://github.com/obra/superpowers)，全部规则中文化，并加入了硬门禁、任务合同、防摆烂引擎等增强。

---

## 这个项目能帮你做什么？

| 你想做的事 | 一条命令搞定 |
|---|---|
| 从零开发一个新功能 | `/Featureflow <需求>` |
| 在已有项目上加功能 | `/extend <功能描述>` |
| 修一个 Bug | `/fix-bug <问题描述/链接>` |
| 写单元测试 | `/test-gen <文件路径>` |
| 让 AI 审查代码 | `/code-review <路径>` |
| 看不懂的项目想快速理解 | `/doc-init` |

不想记命令？**只用 `/Featureflow`**，它会自动判断任务类型并路由到对应流程。

---

## 三条铁律（AI 必须遵守）

1. **称呼 Boss** —— 每次回复第一句话必须叫你 `Boss`
2. **拿不准就问** —— 设计上有疑问先问你，不擅自决定
3. **不写兼容代码** —— 除非你主动要求

> 还有一条**数据铁律**：任何动生产数据的操作（迁移、批量改/删/清表、`rm -rf` 等）必须先有备份、dry-run、回滚脚本，并经你签字。

---

## 30 秒安装

只需要复制 2 样东西到你的项目根目录：

```bash
cp CODEBUDDY.md  /path/to/your-project/
cp -r .codebuddy /path/to/your-project/
```

然后重启 CodeBuddy / 新开会话即可。规则会自动加载。

> `docs/` 和 `spec/` 是运行时产物，不需要预先复制。

---

## 5 分钟上手

### 场景 1：新功能开发

```
你：/Featureflow 给订单模块加一个 Excel 导出功能
AI：Boss，我先澄清几个问题……
   （问完后自动走：规格 → 计划 → 编码 → 测试 → 审查 → 收尾）
```

### 场景 2：修 Bug

```
你：/fix-bug 用户详情页点保存没反应  src/user/UserDetail.vue
AI：Boss，先复现并定位根因……
```

### 场景 3：接手陌生项目

```
你：/doc-init
AI：Boss，扫描项目并生成三层文档（项目地图 → 模块说明 → 文件头部注释）……
```

之后再让 AI 改代码，它能秒懂任意模块。

> 📘 想看「新建项目」和「老项目扩展」从头到尾的完整走查（每步命令 + 会撞到的门禁 + 踩坑点）？读 [最佳实践教程](./docs/playbooks/best-practices-tutorial.md)。

---

## 接入 GitLab CI 强门禁（可选）

项目托管在 GitLab 时，可用 `/ci-setup` 把流程/质量门禁接入 CI 流水线，让门禁从「AI 自觉」升级为「MR 合并阻断」。

### 最终效果：AI 生成的流水线长什么样

`/ci-setup` 让 AI **探测项目技术栈**（`pom.xml` / `go.mod` / `package.json` …），从模板**生成 `.gitlab-ci.yml`**（5 阶段），并填入构建/测试命令。开发者推 MR → 流水线跑 → 任一红灯 → MR 合不了：

| 阶段 | 跑什么 | 是不是「review / 单测」 |
|---|---|---|
| `gate:process` | 门禁资产 / 证据齐备 | 流程门禁 |
| `build:compile` | 真实编译 | — |
| **`test:unit`** | **真实跑单元测试**，产出 `test-summary.json` | ✅ 单元测试在这 |
| `quality:check` | 消费 `test-summary.json` 判通过率 / 覆盖率 / 文档同步 | 质量门禁 |
| `verify:commit-msg` | commit 规范校验 | 替代 CE 缺失的 Push Rules |

> **关于「代码 review」**：AI 代码审查（审查立方 / 找 bug）**默认不是流水线里的阻断 job**，而是 `/schedule-setup` 的**定时 AI 任务**——Task#4（每日审查 → 产出 Critical Issue）、Task#17（每小时审 open MR → 合并）。原因：GitLab CE 无代码审查 widget，且 AI 审查需要 agent 运行时（CodeBuddy CLI）而非普通 CI runner。审查结果走缺陷闭环（`/defect-loop`）变成 Issue，而非让流水线变红。若想让 AI 审查**也成为 MR 阻断 job**，需让 runner 能拉起 CodeBuddy CLI（可做，按需定制）。

### 前置：GitLab 服务器要配什么（Runner + 是否需要 Docker）

- **GitLab CE 14.8.2 自带 CI/CD，服务器侧通常无需额外开启。**
- **必须有 GitLab Runner**：没 Runner 流水线一直 pending、门禁形同虚设——装 + 注册一个 Runner 到内网 GitLab。
- **需要 Docker 吗？取决于 Runner executor**：
  - **docker executor（推荐，模板默认）**：✅ 需要 Docker（Runner 主机装 Docker）+ 内网 Docker registry 提供 `image:` 基础镜像；e2e 真实中间件（`services:`）也只在此模式可用。
  - **shell executor**：❌ 不需要 Docker，但要在 Runner 主机预装构建/测试工具链，并从 `.gitlab-ci.yml` 删掉 `image:` / `services:`。
- MCP server（AI 访问 GitLab，与 Runner 无关）推荐也用 Docker 跑（或 npx + 内网 npm）。
- 服务器/Runner/Docker 完整说明见 [.codebuddy/skills/ci-integration/references/gitlab-server-setup.md](./.codebuddy/skills/ci-integration/references/gitlab-server-setup.md)。

### 1. 部署 GitLab MCP server

AI 经 [`@zereight/mcp-gitlab`](https://github.com/zereight/gitlab-mcp) 访问 GitLab，版本锁定 `2.1.12`。能直连 npm 时直接用 `npx`（mcp.json 配置见「2. 配置 MCP server」与 mcp-setup.md）；纯内网无公网时先把它搬进内网（二选一）：

```bash
# 方式 A：自建 Docker 镜像（推荐）
docker pull zereight050/gitlab-mcp:<2.1.12 对应 tag>
docker tag  zereight050/gitlab-mcp:<tag> <内网registry>/gitlab-mcp:2.1.12
docker push <内网registry>/gitlab-mcp:2.1.12

# 方式 B：把 @zereight/mcp-gitlab@2.1.12 发布到内网 npm registry
```

> 版本锁定 `2.1.12`，不要用 `latest`——版本漂移会导致工具集变化。

### 2. 配置 MCP server

在 CodeBuddy 的 MCP 配置中接入，关键环境变量：

```bash
GITLAB_API_URL=https://<内网GitLab域名>/api/v4   # 填到 /api/v4 为止
GITLAB_PERSONAL_ACCESS_TOKEN=<PAT，scope 勾 api>
USE_PIPELINE=true            # CI 门禁强依赖
USE_GITLAB_WIKI=true         # 知识库能力需要
GITLAB_READ_ONLY_MODE=true   # 初期只读，验证无误后再放开写
```

> PAT 获取：GitLab 头像 → Preferences → Access Tokens，scope 勾 `api`。

### 3. 跑 /ci-setup

```
你：/ci-setup
AI：Boss，探测到项目技术栈为 Maven……
   （生成 .gitlab-ci.yml、MR 模板、commit 校验脚本、GitLab 设置清单）
```

完整部署、功能开关与排障见 [.codebuddy/skills/gitlab-bridge/references/mcp-setup.md](./.codebuddy/skills/gitlab-bridge/references/mcp-setup.md)。

---

## 项目结构

```
your-project/
├── CODEBUDDY.md              # 主引导文件（铁律 + 工作流）
└── .codebuddy/
    ├── commands/             # 斜杠命令（单入口路由 + 各阶段专用入口）
    ├── skills/               # 能力（按需调用）
    ├── agents/               # 专职子代理
    └── rules/                # 规则（核心常驻 + 按需加载）
```

> 想了解每个目录里有什么？看 [docs/](./docs/) 和 [CODEBUDDY.md](./CODEBUDDY.md)。

---

## 常用命令速查

| 命令 | 用途 |
|---|---|
| `/Featureflow` | **推荐入口**，自动识别任务类型并路由 |
| `/brainstorm` | 头脑风暴，需求澄清和方案发散（接口设计涉及平台 OpenAPI 时联动 openapi-creator 规范） |
| `/openapi` | 宇视平台 OpenAPI 接口设计（五阶段：需求澄清 → 生成 → 校验 → 审查 → YAML 导出） |
| `/spec-lite` | 写轻量规格（自动判定 L/M/H 难度） |
| `/walkthrough` | 串讲（编码前设计对齐）：概要对齐架构/模块边界，详细锁定接口契约/数据流 |
| `/spec-check` | 校验 `spec/` 三级目录结构合规（必须文件/命名/层级） |
| `/write-plan` | 写实施计划 |
| `/execute-plan` | 按批次执行计划，每批暂停等你确认 |
| `/extend` | 在已有代码上安全加功能 |
| `/fix-bug` | 修 Bug 全流程（单次手动） |
| `/defect-loop` | 缺陷闭环（批量自动）：扫描→分类→Worktree 隔离修复→验证→MR→关闭，维护 `bugfix:*` 标签状态机 |
| `/test-gen` / `/unified-test` | 生成单元测试（自动按语言路由） |
| `/code-review` | 代码审查（通用五维 + Web 前端专项 + Qt 专项；大范围/定时走增量模式：Baseline Commit + 审查立方 + `.clawbench` Issue 闭环） |
| `/cpp-code-review` | EZStation/EZTools 项目 C++/Qt 专项审查（XLSX 报告输出到 `D:/Review/`） |
| `/doc-init` / `/doc-sync` | 三层代码自文档体系（CONTEXT.md） |
| `/spec-sync` | 设计文档（`spec/`）自动规格回填：即时/每日/每周三层 + Merge-Back |
| `/ci-setup` | 把流程/质量门禁接入 GitLab CI 流水线（GitLab CE 14.8.2，软门禁升级为合并阻断）|
| `/schedule-setup` | 接入 7 类定时任务，让交付阶段 24×7 无人值守（CodeBuddy 定时 / cron / GitLab Pipeline Schedules）|
| `/event-setup` | 事件驱动触发：GitLab Webhook 把 MR/评论/label/pipeline 实时映射成命令（取代轮询）；支持 MR 评论 `/code-review`、打 `ai:review` 标签召唤 AI（对标 GitHub `@claude`）|
| `/status` | 查看当前任务进度 |
| `/pua` | 防摆烂引擎，AI 卡住时手动激活 |
| `/requirement-review` | 需求评审模拟器（四角色模拟评审 PRD，上会前自检） |

完整命令列表见 [CODEBUDDY.md](./CODEBUDDY.md#8-常用命令速查)。

---

## 三个核心理念

### 1) 单入口路由
不用记一堆命令，`/Featureflow` 自动判断你要做什么。

### 2) 硬门禁治理
关键节点（写计划/执行/发布）必须满足前置条件，缺证据就 `BLOCKED`，不允许硬推进。

### 3) 文件即记忆
长任务用 `docs/progress.md` + `docs/findings.md` + `docs/pending-decisions.md` 持久化记录，
防止 AI 跑偏、忘记，或把一次抛多个待决策项的回合丢在对话里。
brainstorm / spec-lite 阶段尤其依赖 `pending-decisions.md`（≥ 2 个待决策项即强制落盘，详见 `/pending`）。

---

## 同时支持 Git 和 SVN

会话开始时自动检测，所有分支/提交/回滚操作两套都有对应方案。

---

## 常见问题

**Q：规则太多，AI 上下文会爆吗？**
不会。只有 4 条核心规则常驻（验证、记忆、日志、Karpathy 四准则），其他按需加载。

**Q：可以只用一部分功能吗？**
可以。删掉不需要的 `.codebuddy/skills/<xxx>/` 即可。最小核心：`CODEBUDDY.md` + `verification-before-completion` + `file-based-memory`。

**Q：三条铁律能改吗？**
能。编辑 `CODEBUDDY.md` 第 1 节即可。

**Q：和 GitNexus / Claude Code 的 `.claude/` 冲突吗？**
不冲突。`.codebuddy/*` 是事实源，`.claude/*` 仅作为参考提示层。建议把 `.claude/skills/`、`AGENT.md`、`CLAUDE.md` 加进 `.gitnexusignore`。

更多问答见旧版 README 备份或 [docs/](./docs/)。

---

## 相比上游 Superpowers 的增强

- 🔀 **双 VCS 支持**：Git + SVN 自动检测
- 🧩 **`/extend` 命令**：已有项目安全扩展
- 📖 **三层代码自文档**：项目地图 → 模块 CONTEXT → 文件头注释
- 🧪 **统一前后端测试**：`.vue/.go` 自动生成 + 执行 + 修复 + 覆盖率
- 📋 **代码审查升级**：11 种语言规范 + Web 前端专项 + C++/Qt 专项（EZStation/EZTools 智能路由，按项目变体自动切换日志规范）+ Excel 报告
- 🔌 **OpenAPI 接口设计**：宇视《平台类 OpenAPI 接口定义规范》五阶段工作流，自动规范校验 + 公司标准字段库核对 + OpenAPI YAML 导出；头脑风暴接口设计阶段自动联动
- 🚦 **CI 强门禁**：经 `gitlab-bridge` 对接层接入内网 GitLab，把流程/质量门禁做成 CI 流水线 job，软门禁升级为 MR 合并阻断（GitLab CE 适配）
- 🗣️ **串讲（设计对齐）**：编码前两层串讲（概要对齐架构/边界，详细锁接口契约），堵住「方向偏了再返工」的最大窗口
- 🔁 **缺陷闭环**：`bugfix:*` 标签状态机 + `.clawbench`↔GitLab Issue 双向同步 + Worktree 隔离修复，缺陷从发现到关闭自驱动
- 🔍 **增量代码审查**：Baseline Commit 锚点 + Block 化 + 审查立方 3×3×4 + Critical→可追踪 Issue 闭环
- ⏰ **定时自动化交付**：7 类定时任务（文档/发布/审查/缺陷/MR 合并）让交付阶段 24×7 无人值守
- 🗂️ **双层 Spec + 规格活文档**：`spec/` 三级目录（高层面向人 / 低层面向 AI）+ 三层自动规格回填（即时/每日/每周）+ Merge-Back
- 📐 **GitLab CE 14.8.2 版本适配**：CI/CD 配置安全子集 + 版本能力支持矩阵 + 「未满足实现」清单与替代
- 🐛 **`/fix-bug` 全流程**：问题单 → 上下文 → 定位 → 修复 → 验证
- 🔥 **PUA 防摆烂引擎**：AI 卡住或敷衍时自动激活
- 📊 **AI 交互质量评分**：4 维度 30 分制评估对话质量
- 🧠 **文件即记忆**：用文件代替上下文窗口做长任务记忆
- 🔒 **三条铁律 + 数据铁律**：贯穿所有规则和子代理

---

## 深入了解

- 会话最小手册：[CODEBUDDY.md](./CODEBUDDY.md)
- 工作流详解：[docs/workflows/](./docs/workflows/)
- 流程实操手册：[docs/playbooks/workflow-playbook.md](./docs/playbooks/workflow-playbook.md)
- 最佳实践教程（新建项目 & 老项目扩展）：[docs/playbooks/best-practices-tutorial.md](./docs/playbooks/best-practices-tutorial.md)
- 门禁矩阵：[.codebuddy/skills/process-gatekeeper/gate-matrix.md](./.codebuddy/skills/process-gatekeeper/)
- 路由规则：[.codebuddy/skills/devflow-router/SKILL.md](./.codebuddy/skills/devflow-router/SKILL.md)

---

## 许可证

MIT（继承自上游 [obra/superpowers](https://github.com/obra/superpowers)）。
