---
name: defect-tracking
description: 缺陷生命周期闭环技能。用于把代码审查、测试、CI、GitLab Issue 发现的缺陷，按「发现→分类→评估→Worktree 隔离修复→验证→MR→关闭」自驱动推进；维护 bugfix:* 标签状态机与 .codebuddy-runtime↔GitLab Issue 双向同步。用户提到"缺陷闭环/批量修 issue/自动修 bug/缺陷生命周期/扫 issue 修复/defect loop"时触发。单次手动定位修复用 bug-fix；本技能是批量自动闭环。
---

# 缺陷生命周期闭环（Defect Tracking）

本技能回答的是：**怎样让缺陷从发现到关闭由 AI 自驱动推进，人只在关键节点审核验收。**

## 核心心智

1. **AI 主动发现，而非被动等待**：代码审查、测试、CI 都是缺陷发现源，AI 既是修复者也是发现者。
2. **每次只修一个，Worktree 隔离**：多缺陷并行修复会交叉污染；隔离保证干净回滚。
3. **最小化修复**：只改必要代码，不趁机重构，不改文档——diff 应一目了然只和这个 bug 相关。
4. **验证是修复的一部分**：没有验证证据的修复不算完成；无法验证必须标记，不关 Issue。
5. **放弃也是一种决策**：跨层架构 / 核心流程重构 / 信息不足的缺陷，记录原因后交人工，比盲目修复安全。

## 与 bug-fix 的分工

| | `bug-fix` | `defect-tracking`（本技能）|
|---|---|---|
| 定位 | 单次手动修复方法论 | 批量自动闭环编排 |
| 范围 | 一个明确问题单 | 扫描多个缺陷源，择一推进 |
| 调用关系 | 被本技能在「修复」步骤调用 | 编排者：分类 → 隔离 → 调 bug-fix 修复 → 验证 → MR → 关闭 |

修复的具体定位与改动方法论复用 `bug-fix`；本技能负责其外层的生命周期管理。

## 资源加载规则

- 判断标签流转、分类评级时，读 `references/label-state-machine.md`
- 处理 `.codebuddy-runtime/issues/` 与 GitLab Issue 同步时，读 `references/dual-sync.md`
- 输出修复报告时，读 `templates/fix-report.md`

## 何时使用

1. 定时缺陷清理（Task #9：扫 `.codebuddy-runtime/issues/`；Task #10：扫 GitLab Issue）
2. 代码审查产出 Critical → 收录为可追踪缺陷并推进修复
3. 一批积压 Issue 需要分类 + 择一自动修复

## 何时不用

1. 用户给了单个明确问题单要立即修 → 直接用 `bug-fix`
2. 需求是新增功能 / 重构 → 走 spec/plan 工作流
3. 缺陷需架构设计 → 打 `bugfix:needs-design`，交人工

## 阻断条件

1. `gitlab-bridge` 写动作（`issue.*` / `mr.merge`）不可用且本地降级也无法满足（如无 `docs/backlog/`）——阻断并说明
2. 缺陷信息不足以复现或定位，且无补充——打 `bugfix:needs-design`，跳过
3. 修复涉及数据 schema / 核心接口签名变更且 Boss 未确认——阻断（数据铁律）

## 缺陷来源

| 来源 | 触发 | 收录方式 |
|---|---|---|
| 代码审查 | 定时 Task#4 / MR | Critical → `.codebuddy-runtime/issues/ISS-{nnn}.md` + `issue.create` |
| 测试验证 | CI / 手动 | 失败日志分析 → `issue.create` |
| CI 流水线 | 自动 | 解析失败原因 → 关联或 `issue.create` |
| GitLab Issue | 人工提交 | `intake.list` 扫描 → AI 分类打标签 |

## 自驱动全流程（7 步）

1. **发现与收录**：从缺陷源收集；代码审查 Critical 同时建本地 ISS 文件与 GitLab Issue
2. **分类与评级**：AI 读标题+正文判断 bug / enhancement / question / 不确定（见 `label-state-machine.md`）
3. **评估与选择**：bug 队列按创建时间先入先出；评估是否可自动修复；**每次只修 1 个**；命中放弃标准则打 `bugfix:needs-design`
4. **Worktree 隔离修复**：经 `using-git-worktrees` 创建 `.worktrees/bugfix-{iid}` + 分支 `fix/issue-{iid}`；打 `bugfix:in-progress`；调 `bug-fix` 方法论实施最小化修复 + 补回归测试
5. **修复验证**：后端→测试全绿；前端 UI→浏览器自动化；无法验证→`bugfix:needs-verification`；失败→`bugfix:failed` 并回滚
6. **MR 流程**：commit（缺陷格式见 `bug-fix/templates/bugfix-commit-message.md`）→ `mr.create`（关联 Issue，`Fixes #{iid}`）→ 轮询 CI（最多 40×30s）→ 失败自修复（最多 3 次）→ `mr.merge`
7. **清理与报告**：`git worktree remove`（无论成败必清理）→ 更新 Issue 状态 → 输出 `templates/fix-report.md`

## 放弃标准（典型信号）

- 需改动 >5 个文件
- 跨层架构调整（同时改后端 API + 前端 store + 多组件）
- 涉及核心流程重构
- 修复方案不确定，可能引入新问题
- 缺少必要信息无法复现/定位

放弃时：`issue.update` 打 `bugfix:needs-design` + `issue.note` 说明原因。

## 约束

1. 所有 GitLab 交互**只经 `gitlab-bridge` 抽象动作**（`intake.*` / `issue.*` / `mr.*` / `pipeline.status`），不直调 glab / MCP
2. 修复必须在独立 Worktree，完成后必须 `git worktree remove`
3. 修复必须附带回归测试，覆盖 bug 触发条件
4. 所有代码修改必须经 MR 流程，CI 通过合并后才算完成
5. 不重复处理已有 `bugfix:*` 标签的 Issue

## 禁止事项

1. 不要一次修多个缺陷——交叉影响会让回滚和定位都变难
2. 不要做无关重构或改文档——超范围变更增加 review 难度和引入新问题的风险
3. 不要在无验证证据时关闭 Issue——修而不验等于没修
4. 不要 `gitlab-bridge` 不可用就报错终止——走本地 `docs/backlog/` 降级
5. 不要为「让测试通过」而改测试断言 / schema——只改业务代码（L1 层原则）
