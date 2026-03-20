# 技术发现与决策记录

## 2026-03-20 Skill Library Regrade

### 关键发现

- Skill 评分提升的最高杠杆点不是“加内容”，而是补齐高质量中文 `name/description`
- 对复杂 skill，最有效的结构是“主 `SKILL.md` 负责触发与路由，细节下沉到 `references/` 或 `templates/`”
- 多个低分 skill 的根因相同：正文教程化、缺少阻断条件、缺少反模式和资源加载时机

### 已落地决策

| 决策 | 理由 |
|---|---|
| 将 `brainstorming` 主文件瘦身，阶段细节下沉到 `references/stage-guide.md` | 提升 progressive disclosure，减少主文件噪音 |
| 为 `subagent-driven-development` 补齐真实存在的 implementer / spec-reviewer / code-reviewer 模板 | 修复“主文件口头引用模板，但磁盘不存在”的结构问题 |
| 将 `research/testcase/writing-plans/executing-plans/file-based-memory/process-gatekeeper` 改为协议式 skill | 让主链 skill 从“骨架”变为“可执行工作法” |
| 将 `version-control-branching/using-git-worktrees/finishing-branch/code-simplifier/custom-testing` 从教程式改为决策式 | 消除尾部技能的主要扣分来源 |

### 最终复评结论

- 全库均分提升到 `92.3 / 120`
- 等级分布变为 `A=1, B=11, C=17, D=4, F=0`
- 当前最值得继续优化的尾部 skill：`writing-skills`、`postgres-best-practices`、`pua`、`dispatching-parallel-agents`

## 2026-03-20 Tail Skills Cleanup

### 新发现

- `writing-skills` 的主要问题不是“内容少”，而是沿用了旧 skill frontmatter 口径，并把理论解释写得太重
- `postgres-best-practices` 的主要问题是主文件过于教程化，缺少“先判断问题类型，再决定优化策略”的决策入口
- `pua` 的主要问题是正文过重，长篇话术和方法论混在一起，导致触发后 token 成本过高
- `dispatching-parallel-agents` 缺少与 `parallel-delivery`、`subagent-driven-development` 的清晰边界，容易重复触发或角色重叠

### 本轮决策

| 决策 | 理由 |
|---|---|
| 将 `writing-skills` 重写为当前项目可用的元技能，并显式声明只使用 `name/description` frontmatter | 修正过时规范，提升触发与可执行性 |
| 为 `postgres-best-practices` 新增 `references/query-patterns.md`，主文件仅保留决策规则与高风险反模式 | 降低教程化冗余，提高 progressive disclosure |
| 为 `pua` 新增 `references/flavor-pack.md`，把大厂风味话术从主文件下沉 | 大幅降低主文件负担，保留按需话术资源 |
| 将 `dispatching-parallel-agents` 重写为“并行分组协议”并补齐与其他并行技能的边界 | 减少重复功能与误触发 |

### 当前状态

- 上一版 `skill-library-final-regrade.md` 已经完成，但尚未包含本轮 4 个尾部 skill 的新分数
- 若需要对当前最新 worktree 形成最终定稿，需要再做一次全库复评分

## 2026-03-20 Final Tail Regrade

### 复评结论

- 将 `writing-skills`、`postgres-best-practices`、`pua`、`dispatching-parallel-agents` 纳入最新复评分后，全库均分进一步提升到 `93.9 / 120`
- 当前等级分布为 `A=1, B=11, C=21, D=0, F=0`
- 技能库尾部已基本被抬升到 `C` 档以上

### 新决策

| 决策 | 理由 |
|---|---|
| 将 `postgres-best-practices` 的大量 SQL 示例下沉到 `references/query-patterns.md` | 主文件更聚焦决策，避免教程化冗余 |
| 将 `pua` 的大厂风味话术下沉到 `references/flavor-pack.md` | 保留风味选择能力，同时控制主文件 token 成本 |
| 将 `dispatching-parallel-agents` 明确定位为“当前轮次内并行分发决策” | 减少与 `parallel-delivery`、`subagent-driven-development` 的角色重叠 |
| 将 `writing-skills` 显式切换到当前项目真正采用的 frontmatter 规范 | 修正过时格式，提升元技能可信度 |

## 2026-03-20 Mid C Tier Optimization

### 新发现

- `extending-project` 的主要问题是主文件过重且缺少清晰 frontmatter，导致更像“长流程说明”而不是“扩展决策 skill”
- `requesting-code-review` 与 `receiving-code-review` 的主要问题是缺少 `name`，同时“什么时候发起/怎么接收”与“怎么审查”之间边界不够清晰
- `ai-interaction-scoring` 已有模板和规则文件，但主文件此前没有显式说明何时加载它们
- `unified-test` 的主文件已经接近路由层，但 description 和资源加载协议还不够硬，且目录里存在无助于 agent 执行的 `README.md`

### 本轮决策

| 决策 | 理由 |
|---|---|
| 将 `extending-project` 重写为“理解项目 -> 影响评估 -> 扩展模式 -> 计划/执行”协议 | 提高知识密度，减少流程说明感 |
| 为 `requesting-code-review` 与 `receiving-code-review` 补齐 `name/description` 并强化边界 | 提升触发准确率，减少与审查执行 skill 的重叠 |
| 为 `ai-interaction-scoring` 补充模板/规则文件的资源加载规则 | 让现有资源真正被 skill 使用 |
| 为 `unified-test` 强化 adapter/orchestrator/reference 的按需加载协议，并删除 `README.md` | 提升 progressive disclosure，减少无关噪音 |

## 2026-03-20 Mid C Tier Regrade

### 复评结论

- 纳入 `extending-project`、`requesting-code-review`、`receiving-code-review`、`ai-interaction-scoring`、`unified-test` 的最新改动后，全库均分提升到 `94.7 / 120`
- 当前等级分布为 `A=1, B=12, C=20, D=0, F=0`
- `unified-test` 已进入 `B` 档；其余本轮优化 skill 均稳定落在 `C` 档中上段

### 新决策

| 决策 | 理由 |
|---|---|
| 将 `extending-project` 重写为扩展决策协议，而非长流程说明 | 降低通用叙述，提升知识密度 |
| 为 `requesting-code-review` 与 `receiving-code-review` 补齐前后边界 | 把“发起审查”和“处理反馈”从“执行审查”中分离 |
| 为 `ai-interaction-scoring` 明确模板与规则文件的加载时机 | 让技能内资源真正参与执行 |
| 为 `unified-test` 明确 adapter/orchestrator/reference 的按需加载，并删除无关 `README.md` | 提高 progressive disclosure，消除技能目录噪音 |

## 2026-03-20 Bottom C Tier Polish

### 新发现

- `custom-testing` 的难点不在配置模板，而在“没有显式规则时，如何从仓库现有测试反推硬规则和软规则”
- `code-simplifier` 的主要风险不再是“改太多”，而是“把时间花在低收益简化上”
- `finishing-branch` 与 `version-control-branching` 已具备主干协议，但仍需要更明确的路径选择矩阵来减少临场拍脑袋

### 本轮决策

| 决策 | 理由 |
|---|---|
| 为 `custom-testing` 增加规则类型划分、仓库推断协议和输出时说明依据 | 提高在真实项目中无显式规则时的可用性 |
| 为 `code-simplifier` 增加收益判断与简化后验收问题 | 让“值不值得动”更容易判断 |
| 为 `finishing-branch` 增加收尾路径选择矩阵与收尾前最后一问 | 提升收尾路径选择质量 |
| 为 `version-control-branching` 增加分流矩阵、基础分支判断和命名可追溯性要求 | 提升分支策略选择精度 |

## 2026-03-20 Bottom C Tier Regrade

### 复评结论

- 在纳入 `custom-testing`、`code-simplifier`、`finishing-branch`、`version-control-branching` 的最新补强后，全库均分提升到 `95.2 / 120`
- 当前等级分布仍为 `A=1, B=12, C=20, D=0, F=0`
- 这 4 个 skill 均已从 `C` 档底部抬升到中上段

### 新决策

| 决策 | 理由 |
|---|---|
| 将 `custom-testing` 视为“规则执行器 + 规则推断器”双角色 | 让它在真实项目规则不完整时也可落地 |
| 将 `code-simplifier` 的核心价值明确为“收益判断 + 低风险简化” | 防止把时间浪费在低收益清理上 |
| 将 `finishing-branch` 增补为“收尾路径决策器” | 避免只会收尾，不会选路径 |
| 将 `version-control-branching` 增补为“分支策略分流器” | 减少普通分支与 worktree 的误选 |

## 2026-03-20 Final B Push Candidates

### 新发现

- `research` 要冲 `B`，关键不是再加章节，而是让“事实 / 推断 / 未知项”与“何时结束研究”的判断更显性
- `writing-plans` 要冲 `B`，关键在于让计划质量检查更像一套验收矩阵，而不是只靠经验提醒
- `file-based-memory` 要冲 `B`，关键在于把模板和脚本的触发时机写得更硬，并补上 `Do Not Load` 风格的防误用规则

### 本轮决策

| 决策 | 理由 |
|---|---|
| 为 `research` 增加研究判断框架和研究结束条件 | 提升 mindset + usability 得分 |
| 为 `writing-plans` 增加拆解决策矩阵和计划质量检查 | 提升任务拆解的可操作性和自检能力 |
| 为 `file-based-memory` 增加模板/脚本的强制触发与禁止覆盖规则 | 提升 progressive disclosure 和 practical usability |

## 2026-03-20 Final B Push Regrade

### 复评结论

- 将 `research`、`writing-plans`、`file-based-memory` 的最新补强纳入复评分后，全库均分提升到 `95.4 / 120`
- 当前等级分布为 `A=1, B=15, C=17, D=0, F=0`
- `research`、`writing-plans`、`file-based-memory` 已全部进入 `B` 档

### 新决策

| 决策 | 理由 |
|---|---|
| 将 `research` 的重点转向“判断框架 + 结束条件” | 让研究从报告模板升级为研究协议 |
| 将 `writing-plans` 的重点转向“拆解决策矩阵 + 质量检查” | 提高计划可执行性与自检能力 |
| 将 `file-based-memory` 的重点转向“模板/脚本强制触发 + Do Not Load 风格规则” | 提升导航型 skill 的精度 |

## 2026-03-20 Remaining C Tier Upgrade

### 新发现

- `code-self-check` 的核心问题不在主骨架，而在缺少更细的 diff 场景矩阵与 `applyFix` 风险分级
- `using-git-worktrees` 已有主流程，但还缺“复用、残留、清理失败”这类真实边界场景
- `requesting-code-review` 需要把“审查深度选择”与“发起前材料准备”拆成显式资源
- `custom-testing` 需要一个真实可落地的外部规则模板，才能从“规则说明”升级到“规则资产”

### 本轮决策

| 决策 | 理由 |
|---|---|
| 为 `code-self-check` 新增 `references/diff-scenarios.md` | 提高 diff 场景判断与 `applyFix` 边界清晰度 |
| 为 `using-git-worktrees` 新增 `references/worktree-edge-cases.md` | 补齐复用/残留/清理失败等高频边界案例 |
| 为 `requesting-code-review` 新增审查深度矩阵与审查请求模板 | 让发起审查时的分流和材料准备更标准化 |
| 为 `custom-testing` 新增 `templates/external-test-rules-template.md` | 提供可直接落地的项目测试规则资产 |

## 2026-03-20 Remaining C Tier Regrade

### 复评结论

- 在纳入 `code-self-check`、`using-git-worktrees`、`custom-testing`、`requesting-code-review` 的最新补强后，全库均分提升到 `95.8 / 120`
- 当前等级分布为 `A=1, B=15, C=17, D=0, F=0`
- 这 4 个 skill 均提升到 `93` 左右，已从 `C` 档底部抬升到中上段

### 新决策

| 决策 | 理由 |
|---|---|
| 为 `code-self-check` 增补 diff 场景矩阵 | 让自检从通用 checklist 升级为场景化审查协议 |
| 为 `using-git-worktrees` 增补边界案例 | 让主技能覆盖真实使用中的复用与清理问题 |
| 为 `custom-testing` 增补外部规则模板资产 | 让规则说明变成可落地模板 |
| 为 `requesting-code-review` 增补深度矩阵与请求模板 | 让“发起审查”动作更标准化 |
## 2026-03-20 Near-B C Tier Upgrade

### 新发现

- `testcase` 距离 `B` 最近，但还缺高风险样例与追踪矩阵样例，导致实操层略弱
- `ai-interaction-scoring` 已有模板与规则文件，但还缺证据抽取顺序和 `BLOCKED` 条件
- `receiving-code-review` 的流程已清晰，但缺统一回复模板，实操一致性不足
- `custom-testing` 需要补规则冲突解析样例，避免“有规则但不会裁决”

### 本轮决策

| 决策 | 理由 |
|---|---|
| 为 `testcase` 新增 `references/testcase-patterns.md` | 提供高风险链路和追踪矩阵样例 |
| 为 `ai-interaction-scoring` 新增 `references/evidence-patterns.md` | 提高证据归类与保守评分的一致性 |
| 为 `receiving-code-review` 新增 `templates/review-response-template.md` | 提高逐条处理 review 的输出一致性 |
| 为 `custom-testing` 新增 `references/rule-resolution-examples.md` | 提高规则冲突场景下的裁决能力 |

## 2026-03-20 Near-B C Tier Regrade

### 复评结论

- 在纳入 `testcase`、`ai-interaction-scoring`、`receiving-code-review`、`custom-testing` 的最新补强后，全库均分提升到 `95.9 / 120`
- 当前等级分布为 `A=1, B=17, C=15, D=0, F=0`
- `testcase` 与 `ai-interaction-scoring` 已进入 `B` 档；`receiving-code-review` 与 `custom-testing` 升至高 `C`

### 新决策

| 决策 | 理由 |
|---|---|
| 为 `testcase` 补高风险样例与追踪矩阵资源 | 让测试设计从原则走向可落地样式 |
| 为 `ai-interaction-scoring` 补证据模式与阻断规则 | 让评分动作更稳定、可解释 |
| 为 `receiving-code-review` 补回复模板 | 让 review 反馈处理更标准化 |
| 为 `custom-testing` 补规则冲突样例 | 让规则解释从“知道”升级为“会裁决” |
