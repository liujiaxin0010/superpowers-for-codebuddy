# 工具流分阶段优化 Backlog

> 来源：2026-06-09 对整套工具流的 SDLC 各阶段评审。供排期用。
> 杠杆 = 收益/成本；★★★ 最高。`/metrics`（见 `specs/2026-06-09-delivery-metrics-design.md`）是 OPT-00，多数项的"是否有效"判定都依赖它。

## 优先级 Top（建议先做）

| 编号 | 杠杆 | 一句话 |
|---|---|---|
| OPT-00 | ★★★ | 建反馈闭环 `/metrics`（已出 spec）——解锁其余所有项的效果判定 |
| OPT-R1 | ★★★ | ✅ 已落地：`.codebuddy/skills/code-review-standards/scripts/diff-risk.js` 基于实际 diff 分类风险，自动定审查深度 + 强制 security/perf/data 门禁，文件感知排除文档误判；接入 `/code-review` 步骤 3.5 |
| OPT-P1 | ★★☆ | ✅ 已落地：write-plan 步骤 7.5 每任务标注 complexity S/M/L + complexityProfile 汇总；execute-plan 5.5 复杂度升级须记录（scope-creep 度量） |

## 需求阶段

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-Q1 | 需求↔验收用例强映射拖到测试前 `requirement-coverage` 才查，太晚 | 在 spec-lite 阶段就硬链接"每条需求 ≥1 可执行验收用例"，缺失即 BLOCK | ★★☆ | — |
| OPT-Q2 | 需求变更无影响分析，下游 spec/plan/test 哪些失效靠人记 | 给需求项加指纹，变更时输出受影响下游产物清单 | ★★☆ | OPT-Q1 |
| OPT-Q3 ✅ | requirement-review 四角色模拟结论未结构化回填 | **已落地** requirement-review 7.5：必补项/P0P1 回填 spec「风险与对策」，标注来源与日期 | ★☆☆ | — |

## 设计 / 计划阶段

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-P1 ✅ | 零工作量估算，无法容量规划/量化 scope creep | **已落地** write-plan 7.5：任务级 complexity S/M/L + complexityProfile 元信息；执行中复杂度升级须记录原因 | ★★☆ | — |
| OPT-P2 ✅ | 架构决策只在 walkthrough 口头对齐，不沉淀 | **已落地** walkthrough/templates/adr-template.md + walkthrough 7.5（架构级结论落 docs/adr/，不滥开）+ write-plan 3.6（读 ADR、冲突须显式 supersede 禁静默偏离） | ★★☆ | — |
| OPT-P3 | 两层 walkthrough 对 L/M 过重（与流程瘦身 P1-5 同源） | L/M 合并为单层；H 保留两层 | ★★☆ | — |

## 编码阶段

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-C1 ✅ | execute-plan 批次崩了回退整批 | **已落地** execute-plan 5.5：批次过即 checkpoint commit（带批次号），失败回退上一 checkpoint 不整计划重来 | ★★☆ | — |
| OPT-C2 | 并行交付文件边界靠人工声明，无冲突检测 | parallel-delivery 自动检测多任务是否改同一文件并预警 | ★★☆ | — |
| OPT-C3 ✅ | 写完即检缺 hook，问题堆到测试/评审阶段才发现 | **已落地** `instant-check` 技能：PostToolUse hook 在 Edit/Write 后毫秒级单文件语法检查（JS/JSON/Shell/Python），失败 exit 2 + stderr 当场回馈 AI；缺工具/异常一律放行不挡路；引擎仓库已 dogfood（`.claude/settings.json`）；10 用例回归 + 入 CI | ★★★ | — |

## 测试阶段

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-T1 | 覆盖率是数字门禁非质量门禁，可用废测试刷 | 引入变异测试抽样或断言密度检查，识别无效测试 | ★★☆ | — |
| OPT-T2 | 无 flaky 识别，重试 3 次把 flaky 当真 bug 修，烧 token | 多次运行结果不稳定即标 flaky 并隔离，不进自动修 | ★★☆ | OPT-00 |
| OPT-T3 | feature 路径不强制回归基线（仅 fix-bug 强制失败回归测试） | 关键 feature 合并前建回归基线 | ★☆☆ | — |

## 评审阶段

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-R1 ✅ | 审查全量、安全/性能靠读 spec 关键词触发（可能漏触发） | **已落地** `diff-risk.js`：按 diff 风险加权深度（deep/standard/light）；碰鉴权/加密/DDL/查询等**代码信号**自动强制 security/perf/data 门禁；文件感知排除文档/.sample 误判；接入 `/code-review` 3.5；7 用例回归 + 入 CI | ★★★ | — |
| OPT-R2 | 审查意见无沉淀，同类问题反复指出 | review→项目专属 lint 规则的回流机制 | ★★☆ | OPT-00 |
| OPT-R3 | 修复闭环靠人确认后再跑命令 | 低风险建议自动修 + 高风险留人的分级 | ★★☆ | OPT-R1 |

## 发布 / 回滚阶段

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-D1 | 无渐进式发布编排 | 加金丝雀/蓝绿/分批的发布策略模板 | ★★☆ | — |
| OPT-D2 | release 声明"预期观测指标"却无发布后自动盯 SLO→建议回滚 | 回滚自动触发：发布后监测错误率/SLO 超阈即建议回滚 | ★★☆ | 生产监控集成 |
| OPT-D3 ✅ | changelog 与需求/PR 无可追溯链接 | **已落地** release 4.5：条目标注 REQ-ID/spec + MR 链接，feature 级不可 untracked | ★☆☆ | — |

## 运维 / 自动化阶段

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-O1 ✅ | 7 类定时任务 24×7 烧 token，无 ROI 核算 | **已被 /metrics 覆盖**：§3 自动化 ROI（次数/成功率/超时率/p50p95）+ §5 接受率（被 revert）；周报=scheduled-automation 低频跑 /metrics | ★★☆ | OPT-00 ✅ |
| OPT-O2 | pipeline 自愈到顶升级人工后，人工修复不回流成 AI 经验 | 人工修复结论结构化沉淀，供同类故障复用 | ★★☆ | — |
| OPT-O3 | 事件链只做 GitLab，缺飞书/企微通知 | 接收器加可插拔通知通道 | ★☆☆ | — |

## 横切（记忆 / 路由 / 决策）

| 编号 | 问题 | 优化 | 杠杆 | 依赖 |
|---|---|---|---|---|
| OPT-X1 ✅ | file-based-memory 膨胀无检索（findings.md 已 234 行还在涨） | **已落地** 归档轮转机制（>400 行原文搬运至 docs/archive/<file>-<period>.md + 指针，禁总结压缩）；引擎 progress.md 已 dogfood（518→23 行） | ★★☆ | — |
| OPT-X2 | pending-decisions 无 SLA 提醒 | 挂起超 N 天自动提醒/升级 | ★☆☆ | OPT-00 |
| OPT-X3 | devflow-router 分流准确率无校准 | 统计判 L 实为 H 的返工率，反哺路由规则 | ★★☆ | OPT-00 |

## 暂缓项及原因

- OPT-P3（walkthrough 两层合并）：方法论裁剪，属产品决策，需 Boss 定 L/M 的合并形态
- OPT-Q1/Q2（spec 阶段验收硬链接/需求指纹）：收紧门禁语义影响所有存量业务项目，建议先用 /metrics 观测 requirement-coverage 阻断率再定
- OPT-T1/T2（变异测试/flaky）：需运行时数据与测试设施，待业务项目接入后迭代
- OPT-R2/R3（审查沉淀回流/分级自动修）：R3 触碰"审查只读"教义，需 Boss 决策；R2 依赖审查数据积累
- OPT-D1/D2（金丝雀/SLO 自动回滚）、OPT-O2/O3（人工修复回流/IM 通知）：依赖部署编排、生产监控、IM webhook 等外部设施
- OPT-X2/X3（决策 SLA/路由校准）：依赖 /metrics 采集周期跑出数据后校准

## 说明

- 标 `依赖 OPT-00` 的项，没有 `/metrics` 也能做，但**无法验证是否真有效**——故 OPT-00 优先。
- 与既往工程化审计的关系：那批（CI/测试/模板版本化）治"引擎自身工程化"，已落地 PR #18；本 backlog 治"工具流对用户项目各阶段的覆盖质量"，是方法论侧增量。
