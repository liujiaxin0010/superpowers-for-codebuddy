# 缺陷标签状态机

AI 通过 GitLab 标签管理缺陷状态，标签变更即状态流转。所有标签操作经 `gitlab-bridge` 的 `issue.update`。

> **CE 14.8.2 适配**：下表标签一律用**单冒号普通 label**（`bugfix:in-progress`），**不用**双冒号 scoped label（`bugfix::in-progress`）——后者的原生互斥是 EE Premium 功能。CE 上同一 Issue 理论上可并存多个 `bugfix:*`，因此**状态流转时必须显式移除旧标签再打新标签**来保证互斥（见各步骤「移除 X，打 Y」）。版本细节见 `gitlab-bridge/references/gitlab-version-support.md` §3。

## 标签体系

| 标签 | 含义 | 谁打 |
|---|---|---|
| `bug` | bug 类型问题 | AI 分类 / 人工 |
| `enhancement` | 新特性或功能请求 | AI 分类 / 人工 |
| `question` | 咨询 / 讨论 / 使用问题 | AI 分类 / 人工 |
| `bugfix:in-progress` | AI 已认领，正在修复 | AI |
| `bugfix:awaiting-review` | 已修复，待人工验收 | AI（验证通过后）|
| `bugfix:needs-design` | 需架构设计，跳过自动修复 | AI（评估后放弃）|
| `bugfix:failed` | 自动修复失败 | AI（修复过程出错）|
| `bugfix:needs-verification` | 已修复但 AI 无法验证 | AI（无验证条件）|

## 状态流转图

```
bug ──→ bugfix:in-progress ──→ bugfix:awaiting-review ──→ 关闭 Issue
  │            │                        │
  │            │                        └─→ bugfix:needs-verification（无法验证，不关 Issue）
  │            ├─→ bugfix:failed（修复失败，回滚）
  │            └─→ bugfix:needs-design（需架构设计）
  │
  └─→ enhancement / question（非 bug，跳过）
```

## 分类判断（Step 2）

| 类型 | 判断依据 | 操作 |
|---|---|---|
| bug | 功能异常、报错、行为不符合预期 | 打 `bug`，进入修复队列 |
| enhancement | 新功能、新特性、改进交互 | 打 `enhancement`，跳过 |
| question | 咨询、讨论、使用问题 | 打 `question`，跳过 |
| 不确定 | 信息不足或问题模糊 | 打 `bugfix:needs-design` + 评论，等人工 |

## 验证结果 → 标签（Step 5）

| 结果 | 标签操作 | 后续 |
|---|---|---|
| 验证通过 | 移除 `in-progress`，打 `awaiting-review` | 继续 MR；合并后 `Fixes` 关键字自动关闭 |
| 无法验证 | 移除 `in-progress`，打 `needs-verification` | 继续 MR，但不关 Issue，待人工确认 |
| 验证失败 | 移除 `in-progress`，打 `failed` | 回滚代码，清理 Worktree |

## 不重复处理原则

已带任意 `bugfix:*` 标签的 Issue 视为「已被处理过」，本轮跳过——避免重复评论 / 重复修复。
