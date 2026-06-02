# Critical Issue 文件格式与疑似解决检查

> 原则：**Critical 发现项必须可追踪**。审查报告是瞬时快照，Issue 是持续状态追踪。Critical 项同时写 Issue 文件，形成「发现 → 追踪 → 验证 → 关闭」闭环。

## 1. Issue 文件格式

每个 Critical 发现项创建 `.clawbench/issues/ISS-{nnn}.md`：

```markdown
---
id: ISS-{nnn}
status: open            # open | suspected-resolved | resolved
severity: critical
dimension: {维度名称}    # 如 安全性 / 流程正确性 / 并发安全
created: {YYYY-MM-DD}
files: [{文件列表}]
gitlab_issue: {iid}     # 由 defect-tracking 同步后回填
---

## Description
{问题描述}

## Impact
{为什么这是 Critical}

## Suggestion
{修复建议}

## History
- {YYYY-MM-DD}: Created by review {review-date}
- {YYYY-MM-DD}: GitLab Issue #{iid} created
```

## 2. 编号规则

- 编号递增：扫描 `.clawbench/issues/` 下已有文件，取最大编号 +1。
- 编号一旦分配不复用，即使 Issue 关闭也保留文件（可追溯历史）。

## 3. 疑似解决检查（每次审查必做）

每次审查在生成新发现项后，回查已有 open Issue：

1. 读取所有 `status: open` 的 Issue 文件
2. 检查其 `files:` 列表中的文件是否在本次变更范围内
3. 涉及文件已变更 → 状态改为 `suspected-resolved`，History 追加一行
4. **不自动关闭**——疑似解决只是标记，最终关闭由 `defect-tracking` 验证后或人工确认

```markdown
## History
- 2026-06-02: Created by review 2026-06-02
- 2026-06-10: Suspected Resolved — auth.js 在 commit abc123 已变更，待验证
```

## 4. 与 GitLab Issue 双向同步

Critical 缺陷同时存在于两个系统，由 `defect-tracking` 维护同步：

| 系统 | 用途 | 标识 |
|---|---|---|
| 本地 `.clawbench/issues/` | 审查报告内部追踪 | `ISS-{nnn}` |
| GitLab Issues | 外部可观测缺陷管理 | IID 编号 |

同步规则：

1. 审查发现 Critical → 创建本地 ISS 文件 + 经 `gitlab-bridge` 的 `issue.create` 建 GitLab Issue（打 `bug` 标签）
2. 本地文件 frontmatter `gitlab_issue` 回填 GitLab IID；History 记录
3. GitLab Issue 描述中引用本地 ISS 编号
4. 后续审查检查本地 Issue 疑似解决状态，经 `issue.update` / `issue.note` 同步到 GitLab

> `gitlab-bridge` 不可用时降级：只维护本地 `.clawbench/issues/`，GitLab 同步留待 bridge 恢复后补做。
