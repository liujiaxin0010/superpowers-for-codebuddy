# 项目文件结构地图

> 手工维护；目录大改后请同步本文件（`scripts/lint-doc-paths.sh` 会校验文中引擎路径有效性）。
> 统计基线：2026-06-09，约 500 个纳管文件。

## 顶层

```text
superpowers-for-codebuddy/
├── CODEBUDDY.md          # 会话最小手册：铁律 / 启动必做 / 路由 / 链路 / 命令速查
├── README.md             # 项目总说明
├── CHANGELOG.md          # 引擎与模板变更记录（/upgrade-check 的对照源）
├── .gitignore            # 个人配置、运行产物、业务运行态目录
├── .gitnexusignore       # GitNexus 代码智能忽略规则
├── .github/workflows/    # engine-lint.yml 引擎自检 CI
├── scripts/              # lint-doc-paths.sh / test-commit-msg-lint.sh（CI 与本地共用）
├── .codebuddy/           # 引擎本体（见下）
├── docs/                 # 引擎自身文档与记录（见下）
└── spec/                 # 约定槽位工作样例：AI2AI/（过程文档槽）、Me2AI/（需求输入槽）
                          #   ⚠️ 这些路径被 10+ 技能作为契约引用，不要移动/重命名
```

## .codebuddy/ —— 引擎本体

```text
.codebuddy/
├── commands/   (43)   # 【入口层】斜杠命令 = 执行编排提示词
│     主链:  Featureflow brainstorm spec-lite walkthrough write-plan execute-plan
│            requirement-coverage test-gen unified-test code-review security-review
│            perf-check system-test data-safety-check release rollback status resume extend
│     GitLab/自动化: ci-setup schedule-setup event-setup runner-deploy pipeline-watch
│            defect-loop issue-draft-pr upgrade-check
│     辅助:  fix-bug research testcase spec-check spec-sync doc-init doc-sync
│            code-self-check cpp-code-review openapi parallel-delivery pending pua
│            requirement-review score-interaction simplify
├── skills/     (54)   # 【能力层】SKILL.md + references/ + templates/ 三段式
│     工作流主链 / 审查质量 / 测试 / 缺陷 / GitLab-CI / 并行协作 / 流程治理 / 外围工具
│     体积大户: docx(61) xlsx(60) ← 第三方搬运脚本库；code-review-standards(26)
│     模板所在: event-triggers/templates/(接收器+权限样例) scheduled-automation/templates/
│            ci-integration/templates/(commit-msg-lint 等)
├── agents/     (10)   # 【子代理】Featureflow 总控 + 实现/审查/调试/测试等专职代理
├── rules/      (11)   # 【行为规则】常驻 4 条 + 按需 7 条（详见 CODEBUDDY.md §2）
├── templates/  task-contracts/ 8 类任务契约
└── state/      仅骨架（README + session-handoff.json.example）；运行态文件运行期才生成
```

## docs/ —— 引擎文档

```text
docs/
├── architecture/   featureflow 架构 + PlantUML + 本结构图
├── playbooks/      best-practices-tutorial（接入全流程）/ workflow-playbook /
│                   unattended-permission-checklist（无人值守免确认上线/排错）
├── workflows/      workflow 目录、prompt 契约、bugfix/refactor/test 工作流
├── specs/          设计 spec（含 3 个 2026-03 试跑样例）
├── quality/        质量门禁契约说明 + *.sample；trials/ 为试跑证据存档
│                   （运行产物 last-quality-gate.json 等已 .gitignore，不入库）
├── pr-summaries/   已合并 PR 的上库总结
├── plans/          计划产物目录契约（.gitkeep）
├── progress.md / findings.md      全局进度与发现台账（历史台账，路径 lint 豁免）
├── process-governance-whitepaper.md
├── ai-feature-flow-mapping.md
└── skill-judge-evaluation-report.md
```

## 关键约定

1. **三层职责**：commands（入口编排）→ skills（能力与资源）→ agents（执行角色）；规则在 rules/，跨技能模板在技能自己的 templates/ 下。
2. **引擎 vs 业务项目**：引擎只提供 runbook 与模板；`/ci-setup` `/schedule-setup` `/event-setup` 在业务项目实例化；运行产物（`.codebuddy-runtime/`、`docs/quality/*.json` 非 sample、`.webhook-receiver-state/`）一律不入引擎库。
3. **模板分发与升级**：复制式分发会腐烂——模板带版本标注，变更记 `CHANGELOG.md`，业务项目用 `/upgrade-check` 对照。
4. **契约路径不可动**：`spec/AI2AI/`（research/testcase 等的默认读写槽）、`spec/Me2AI/需求描述.md`、`技术约束.md`（需求输入槽）、`docs/quality/*.json`（门禁输入输出）被多技能引用，重命名 = 破坏存量业务项目。
