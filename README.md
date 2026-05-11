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

---

## 项目结构

```
your-project/
├── CODEBUDDY.md              # 主引导文件（铁律 + 工作流）
└── .codebuddy/
    ├── commands/             # 21 个斜杠命令
    ├── skills/               # 33 个能力（按需调用）
    ├── agents/               # 9 个专职子代理
    └── rules/                # 7 条规则（核心常驻 + 按需加载）
```

> 想了解每个目录里有什么？看 [docs/](./docs/) 和 [CODEBUDDY.md](./CODEBUDDY.md)。

---

## 常用命令速查

| 命令 | 用途 |
|---|---|
| `/Featureflow` | **推荐入口**，自动识别任务类型并路由 |
| `/brainstorm` | 头脑风暴，需求澄清和方案发散 |
| `/spec-lite` | 写轻量规格（自动判定 L/M/H 难度） |
| `/write-plan` | 写实施计划 |
| `/execute-plan` | 按批次执行计划，每批暂停等你确认 |
| `/extend` | 在已有代码上安全加功能 |
| `/fix-bug` | 修 Bug 全流程 |
| `/test-gen` / `/unified-test` | 生成单元测试（自动按语言路由） |
| `/code-review` | 代码审查（输出 MD + Excel 报告） |
| `/doc-init` / `/doc-sync` | 三层代码自文档体系 |
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
- 📋 **代码审查升级**：11 种语言规范 + Web 前端专项 + Excel 报告
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
- 门禁矩阵：[.codebuddy/skills/process-gatekeeper/gate-matrix.md](./.codebuddy/skills/process-gatekeeper/)
- 路由规则：[.codebuddy/skills/devflow-router/SKILL.md](./.codebuddy/skills/devflow-router/SKILL.md)

---

## 许可证

MIT（继承自上游 [obra/superpowers](https://github.com/obra/superpowers)）。
