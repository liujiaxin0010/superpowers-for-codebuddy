# .codebuddy-runtime/issues ↔ GitLab Issue 双向同步

代码审查发现的 Critical 缺陷同时存在于两个系统，本文件定义二者一致性的维护规则。

| 系统 | 用途 | 标识 | 格式 |
|---|---|---|---|
| 本地 `.codebuddy-runtime/issues/` | 审查报告内部追踪 | `ISS-{nnn}` | 见 `code-review-standards/references/codebuddy-issue-format.md` |
| GitLab Issues | 外部可观测缺陷管理 | IID 编号 | GitLab 原生 |

## 同步规则

1. 代码审查发现 Critical → 同时创建本地 ISS 文件 + 经 `issue.create` 建 GitLab Issue（打 `bug` 标签）
2. 本地 ISS 文件 frontmatter `gitlab_issue` 回填 GitLab IID；History 追加一行
3. GitLab Issue 描述中引用本地 ISS 编号
4. 后续审查检查本地 ISS 的疑似解决状态，经 `issue.update` / `issue.note` 同步到 GitLab

## 创建 GitLab Issue（issue.create）

抽象动作入参（具体 MCP 工具名见 `gitlab-bridge/references/capability-map.md`）：

- title：`[Review] {缺陷简要描述}` 或 `[Test] {失败场景}`
- description：本地 ISS 文件正文（Description / Impact / Suggestion）
- labels：`bug`

创建后回填：

```markdown
## History
- {date}: GitLab Issue #{iid} created
```

## 降级行为（gitlab-bridge 不可用）

- 只维护本地 `.codebuddy-runtime/issues/`，GitLab 同步留待 bridge 恢复后补做
- 或写 `docs/backlog/缺陷卡-{slug}.md` 占位，标识「待人工同步 GitLab」
- 降级不阻断审查与本地缺陷追踪

## 一致性自检

每轮缺陷处理后核对：

1. 每个 `status: open` 的本地 ISS 是否都有对应 `gitlab_issue` IID（降级模式除外）
2. GitLab 上已关闭的 Issue，本地 ISS 是否同步标 `resolved`
3. 本地标 `suspected-resolved` 的，GitLab Issue 是否已 `issue.note` 提示待验证
