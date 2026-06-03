## 缺陷自动修复报告

**日期**: YYYY-MM-DD HH:MM
**来源**: 代码审查 .codebuddy-runtime / GitLab Issue / 测试失败 / CI 失败
**扫描**: X 个开放 Issue
**分类**: X bug / X enhancement / X question / X 不确定

**本次修复**: #{iid} — {title}

**跳过**:
- #{iid}: {原因} → bugfix:needs-design

**修复状态**: 验证通过 / 无法验证 / 修复失败

**验证证据**:
- 构建: `{命令}` → 通过 / 失败（退出码 {n}）
- 测试: `{命令}` → {通过数}/{总数} 通过
- 回归测试: `{测试名}` 覆盖 bug 触发条件 → 通过
- UI 验证（如适用）: 浏览器自动化 通过 / 失败 / 不适用

**MR**: !{mr_iid} — CI 通过 / 失败 | Merged 是 / 否

**Issue 状态**: closed / bugfix:needs-verification / bugfix:failed

**Worktree**: 已清理（`git worktree remove .worktrees/bugfix-{iid}`）

**剩余风险 / owner**: {如有}
