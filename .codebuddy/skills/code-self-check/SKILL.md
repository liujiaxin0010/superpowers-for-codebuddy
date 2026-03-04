---
description: 代码自检技能，基于 Git/SVN diff 对新增修改代码执行结构化审查并输出报告。
---

# Code Self Check

用于在提交前执行统一代码自检，支持 Git 与 SVN。

## 输入参数

- `vcs=auto|git|svn`
- `diffPath=<path>`（可选，优先使用已有 diff/patch）
- `applyFix=true|false`（可选，默认 false）

## VCS 检测

1. `vcs=git`：固定使用 `git diff`
2. `vcs=svn`：固定使用 `svn diff`
3. `vcs=auto`：
   - 存在 `.git` 则走 Git
   - 否则存在 `.svn` 则走 SVN
   - 否则返回 `BLOCKED`

## 执行要求

1. 优先审查新增/修改行（diff 中 `+` 语句）
2. 报告按严重度分级（高/中/低）
3. 给出修复建议与示例
4. `applyFix=true` 时，按确认过的审查项进行修复并回归验证

## 输出

- `docs/quality/code-self-check-report.md`

