# Progress Log

> 历史归档：2026-03 ~ 2026-05 会话见 `docs/archive/progress-2026Q1Q2.md`（file-based-memory 归档机制，>400 行轮转）。

## 会话：2026-06-09（无人值守免确认 + 工程化审计落地，PR #18）

- 根因修复：CI 事件/定时任务拉起的 AI 会话卡在权限确认（实测挂 3h）——CLI 实测形态 `-p`（headless）单独不免确认，免确认 = `permissions.allow` 白名单（受控）或 `-y`（全量）；模板/技能/手册全链对齐，新增 `automation-settings.sample.json` 与 `docs/playbooks/unattended-permission-checklist.md`
- 工程化审计逐项落地：
  - 引擎自检 CI（engine-lint.yml：JS/JSON/Shell 语法、路径引用 lint、commit-msg 单测与自检）
  - 仓库卫生：settings.local.json 与 docs/quality 运行产物出库（+.gitignore）、9 处路径腐烂修复、`缺陷.md`→`defect-classification.md`
  - webhook-receiver v1.1.0：看门狗杀进程树（POSIX/Windows）、maxConcurrent 队列、持久幂等、jobs.jsonl 台账（冒烟全过）
  - 铁律 2 增无人值守分支（headless 禁止同步等人，落盘+回贴+BLOCKED 退出）
  - 模板版本化 + CHANGELOG.md + `/upgrade-check`；Windows schtasks/NSSM 支持；docs/architecture/project-structure.md
- 审计中改判：spec/AI2AI、spec/Me2AI 为 10+ 技能引用的契约槽位样例，保留不迁（已写入结构图"契约路径不可动"）
- 未做（需 Boss 决策）：H 级链路瘦身（P1-5）、master 分支保护需仓库管理员在 GitHub 设置开启

## 会话：2026-06-10（度量闭环收口 + 评审风险加权 + 写完即检）

- /metrics Tier 1：自动修复接受率（git revert，零埋点）、阶段周期（stage-event 埋点，已接入 spec-lite/write-plan/execute-plan/test-gen/unified-test/code-review/release 七命令步骤 0）、缺陷逃逸率（defect-tracking 约定 foundPhase）
- OPT-R1：code-review-standards/scripts/diff-risk.js——审查深度与 security/perf/data 门禁由实际 diff 代码信号触发；文件感知修复（文档里的 crypto/rm-rf 不再误触发，本 PR 自验证 DEEP→STANDARD 收敛）
- OPT-C3：instant-check 技能——PostToolUse 写完即检 hook，引擎已 dogfood；10 用例
- 修复分发缺陷：metrics/stage-event/diff-risk 从引擎根 scripts/ 归位技能 scripts/（业务项目 404 类）
- CI 增三组单测；全套本地复刻通过

## 会话：2026-06-10（剩余 backlog 收口，合入前最后一批）

- OPT-P1 复杂度估算（write-plan 7.5 / execute-plan 5.5 scope-creep 记录）
- OPT-P2 ADR：adr-template + walkthrough 7.5 沉淀 + write-plan 3.6 读取与 supersede 约束 + CODEBUDDY §5 登记
- OPT-X1 归档轮转机制入 file-based-memory；progress.md dogfood 轮转至 docs/archive/progress-2026Q1Q2.md
- 低成本三连：Q3 评审风险回填 / C1 批次 checkpoint / D3 changelog 追溯链；O1 核销（/metrics 已覆盖）
- backlog 9 项 ✅，暂缓项注明原因（产品决策/外部设施/待数据）
