# Skill Library Final Regrade

**日期**: 2026-03-20  
**范围**: `.codebuddy/skills/` 全库 33 个 skills  
**口径**: 使用 `skill-judge` 的 8 维、120 分模型复评分  
**基线**: 以当前 worktree 状态为准，包含尚未提交的 `references/`、`templates/` 与删除的辅助文件  

## 总结

- 平均分：`95.9 / 120`
- 等级分布：`A=1, B=17, C=15, D=0, F=0`
- 相比首轮复评：`83.2 -> 95.9`
- 结论：技能库已经进入“主链稳定、重型技能完成结构下沉、`B` 档成为主体”的状态

这轮整体提分主要来自四类修复：

1. 为大量 skills 补齐高质量中文 `name/description`
2. 将重型主文件改为“主文件路由 + references/templates 下沉”
3. 将教程式正文改造成协议式 skill
4. 为高 `C` 档 skill 增加判断框架、样例 reference 与模板资产

## 新总表

| 分数 | 等级 | Skill |
|---|---|---|
| 108 | A | `bug-fix` |
| 107 | B | `process-gatekeeper` |
| 104 | B | `systematic-debugging` |
| 103 | B | `devflow-router` |
| 100 | B | `task-contracts` |
| 99 | B | `spec-lite` |
| 99 | B | `subagent-driven-development` |
| 98 | B | `brainstorming` |
| 97 | B | `file-based-memory` |
| 97 | B | `parallel-delivery` |
| 97 | B | `research` |
| 97 | B | `web-code-review` |
| 97 | B | `writing-plans` |
| 96 | B | `ai-interaction-scoring` |
| 96 | B | `code-review-standards` |
| 96 | B | `issue-draft-pr` |
| 96 | B | `testcase` |
| 96 | B | `unified-test` |
| 95 | C | `receiving-code-review` |
| 94 | C | `custom-testing` |
| 93 | C | `code-self-check` |
| 93 | C | `postgres-best-practices` |
| 93 | C | `pua` |
| 93 | C | `using-git-worktrees` |
| 93 | C | `xlsx` |
| 92 | C | `dispatching-parallel-agents` |
| 92 | C | `executing-plans` |
| 92 | C | `writing-skills` |
| 91 | C | `extending-project` |
| 91 | C | `finishing-branch` |
| 91 | C | `version-control-branching` |
| 90 | C | `code-simplifier` |
| 90 | C | `requesting-code-review` |

## 提升最大的 Skills

| Skill | 旧分 | 新分 | 变化 |
|---|---:|---:|---:|
| `testcase` | 57 | 96 | +39 |
| `research` | 62 | 97 | +35 |
| `version-control-branching` | 59 | 91 | +32 |
| `using-git-worktrees` | 62 | 93 | +31 |
| `custom-testing` | 68 | 94 | +26 |
| `executing-plans` | 68 | 92 | +24 |
| `finishing-branch` | 68 | 91 | +23 |
| `file-based-memory` | 76 | 97 | +21 |
| `writing-plans` | 81 | 97 | +16 |
| `writing-skills` | 76 | 92 | +16 |

## 关键结论

### 1. 主链 skills 已进入稳定区间

下列主链技能已经具备较完整的触发、阻断、协议与资源装载设计：

- `research`
- `spec-lite`
- `writing-plans`
- `executing-plans`
- `process-gatekeeper`
- `file-based-memory`
- `code-self-check`

### 2. 重型高杠杆 skills 已完成结构下沉

- `brainstorming`
  - 主 `SKILL.md` 已压成路由层
  - 阶段细节下沉到 `brainstorming/references/stage-guide.md`
- `subagent-driven-development`
  - 主 `SKILL.md` 已压成路由层
  - implementer / spec-reviewer / code-reviewer 模板已真实落盘到 `templates/`
- `postgres-best-practices`
  - 主文件改为决策层
  - SQL 示例下沉到 `references/query-patterns.md`
- `pua`
  - 主文件保留触发与方法论
  - 具体话术风味下沉到 `references/flavor-pack.md`

### 3. 中游 C 档已成片抬升，部分成功进入 B 档

以下 skills 已从“偏通用说明”转向“协议式技能”：

- `extending-project`
- `requesting-code-review`
- `receiving-code-review`
- `ai-interaction-scoring`
- `unified-test`
- `custom-testing`
- `code-simplifier`
- `finishing-branch`
- `version-control-branching`
- `code-self-check`
- `using-git-worktrees`

其中以下 3 个已成功冲入 `B`：

- `testcase`
- `ai-interaction-scoring`
- `unified-test`

### 4. 最后一轮接近 B 的 C 档提分有效

通过补强样例资源、证据模式和模板资产：

- `testcase`: `94 -> 96`
- `ai-interaction-scoring`: `93 -> 96`
- `receiving-code-review`: `93 -> 95`
- `custom-testing`: `90 -> 94`

说明接近 `B` 的 `C` 档，继续提分最有效的方法不是加长正文，而是：

1. 增加按需加载的样例资源
2. 增加明确的 `BLOCKED` 条件
3. 增加统一输出模板

## 仍然最值得继续优化的 4 个

1. `code-simplifier`
   - 已具备收益判断，但仍可继续补语言/场景差异化经验
2. `requesting-code-review`
   - 发起协议已清晰，但还可继续强化审查深度分流
3. `extending-project`
   - 扩展决策协议已成型，但仍可继续下沉阶段细节
4. `finishing-branch`
   - 收尾路径矩阵已补齐，但还可补与 PR 模板/团队收口的连接

## 评分说明

本次复评分以当前仓库中的实际文件为准，包含以下未提交但已存在的资源：

- `brainstorming/references/stage-guide.md`
- `subagent-driven-development/templates/implementer-prompt.md`
- `subagent-driven-development/templates/spec-reviewer-prompt.md`
- `subagent-driven-development/templates/code-reviewer-prompt.md`
- `postgres-best-practices/references/query-patterns.md`
- `pua/references/flavor-pack.md`
- `code-self-check/references/diff-scenarios.md`
- `using-git-worktrees/references/worktree-edge-cases.md`
- `custom-testing/templates/external-test-rules-template.md`
- `custom-testing/references/rule-resolution-examples.md`
- `requesting-code-review/references/review-depth-matrix.md`
- `requesting-code-review/templates/review-request-template.md`
- `testcase/references/testcase-patterns.md`
- `ai-interaction-scoring/references/evidence-patterns.md`
- `receiving-code-review/templates/review-response-template.md`

若继续优化剩余 `C` 档，建议继续使用同一口径复评，避免标准漂移。
