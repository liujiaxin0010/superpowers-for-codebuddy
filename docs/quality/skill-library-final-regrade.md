# Skill Library Final Regrade

**日期**: 2026-03-20  
**范围**: `.codebuddy/skills/` 全库 33 个 skills  
**口径**: 使用 `skill-judge` 的 8 维、120 分模型复评分  
**基线**: 以当前 worktree 状态为准，包含尚未提交的 `references/` 与 `templates/` 新资源  

## 总结

- 平均分：`95.4 / 120`
- 等级分布：`A=1, B=15, C=17, D=0, F=0`
- 相比首轮复评：`83.2 -> 95.4`
- 结论：技能库已进入“全库无 D/F，主链稳定，`B` 档占据核心骨架，中游持续抬升”的状态

本轮整体提升主要来自四类结构性修复：

1. 为大量 skills 补齐高质量中文 `name/description`，显著提升触发准确率
2. 将重型主文件改为“主文件路由 + references/templates 下沉”的结构
3. 将教程式正文改造为“何时用 / 何时阻断 / 如何决策 / 不要怎么做”的协议式 skill
4. 为接近 `B` 的 `C` 档 skill 补上更强的判断框架、质量检查和资源加载触发

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
| 96 | B | `code-review-standards` |
| 96 | B | `issue-draft-pr` |
| 96 | B | `unified-test` |
| 94 | C | `testcase` |
| 93 | C | `ai-interaction-scoring` |
| 93 | C | `postgres-best-practices` |
| 93 | C | `pua` |
| 93 | C | `receiving-code-review` |
| 93 | C | `xlsx` |
| 92 | C | `dispatching-parallel-agents` |
| 92 | C | `executing-plans` |
| 92 | C | `writing-skills` |
| 91 | C | `extending-project` |
| 91 | C | `finishing-branch` |
| 91 | C | `version-control-branching` |
| 90 | C | `code-simplifier` |
| 90 | C | `custom-testing` |
| 90 | C | `requesting-code-review` |
| 89 | C | `code-self-check` |
| 89 | C | `using-git-worktrees` |

## 提升最大的 Skills

| Skill | 旧分 | 新分 | 变化 |
|---|---:|---:|---:|
| `testcase` | 57 | 94 | +37 |
| `research` | 62 | 97 | +35 |
| `version-control-branching` | 59 | 91 | +32 |
| `using-git-worktrees` | 62 | 89 | +27 |
| `executing-plans` | 68 | 92 | +24 |
| `finishing-branch` | 68 | 91 | +23 |
| `custom-testing` | 68 | 90 | +22 |
| `file-based-memory` | 76 | 97 | +21 |
| `writing-plans` | 81 | 97 | +16 |
| `writing-skills` | 76 | 92 | +16 |

## 关键结论

### 1. 主链 skills 已经成型

下列主链技能现在已经具备比较完整的触发、阻断、协议与资源装载设计：

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

### 3. 中游 C 档已成片抬升

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

其中 `unified-test` 已进入 `B` 档。

### 4. 最后一轮 B 冲刺有效

通过补强判断框架、质量检查和资源触发：

- `research`：`95 -> 97`
- `writing-plans`：`95 -> 97`
- `file-based-memory`：`94 -> 97`

这 3 个 skill 已进入 `B` 档，说明“不是越长越高分”，而是“越像专家协议、越会按需加载、越会结束判断”越容易提分。

## 仍然最值得继续优化的 4 个

1. `code-self-check`
   - 结构已经稳，但还可继续补更多 diff 场景与自动修复边界
2. `using-git-worktrees`
   - 已形成协议，但仍可补更多冲突复用与清理失败场景
3. `custom-testing`
   - 现在更像“规则执行器”，后续可继续沉淀项目级真实配置样本
4. `requesting-code-review`
   - 审查发起协议已清晰，但仍可继续强化对不同审查深度的分流细则

## 评分说明

本次复评分以当前仓库中的实际文件为准，包含以下未提交但已存在的资源：

- `brainstorming/references/stage-guide.md`
- `subagent-driven-development/templates/implementer-prompt.md`
- `subagent-driven-development/templates/spec-reviewer-prompt.md`
- `subagent-driven-development/templates/code-reviewer-prompt.md`
- `postgres-best-practices/references/query-patterns.md`
- `pua/references/flavor-pack.md`

若后续继续优化中游 `C` 档或开始做提交整理，建议继续使用同一口径复评，避免标准漂移。
