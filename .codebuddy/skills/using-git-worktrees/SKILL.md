---
name: using-git-worktrees
description: Git worktree 隔离开发技能。用于在 Git 项目中为并行任务、子代理分发或脏工作目录创建独立工作树，避免分支切换互相干扰。用户提到“worktree/隔离开发/多个分支并行/独立工作目录”时触发。
---

# Git Worktree 隔离开发

在 Git 项目中，用独立工作树代替频繁切分支，降低上下文污染和本地改动冲突。

## 何时使用

以下情况优先使用 worktree：

1. 当前主工作目录已有未提交改动
2. 需要同时推进两个及以上任务
3. 需要为并行代理提供互不干扰的工作目录
4. 需要把实验性任务与主任务隔离

## 何时不用

以下情况不建议使用本技能：

1. 不是 Git 项目
2. 只做一个短平快任务，且当前目录完全干净
3. 用户明确要求就在当前目录工作

## 前置条件

1. 仓库是 Git
2. 基础分支明确，通常为 `main`
3. 基线测试可运行
4. worktree 目录有明确放置位置

## 阻断条件

出现以下任一情况时，返回 `BLOCKED`：

1. 当前仓库不是 Git
2. 基础分支不明确
3. 已存在同名分支或同名 worktree，且无法确认是否复用
4. 基线验证失败

## 目录策略

优先复用已有 worktree 目录；若不存在，则默认使用 `.worktrees/`。

创建前必须确认：

1. `.gitignore` 已忽略 worktree 目录
2. 路径命名与任务语义一致

## 创建协议

### 1. 选定目录

```bash
if [ -d ".worktrees" ]; then
  WORKTREE_DIR=".worktrees"
elif [ -d "worktrees" ]; then
  WORKTREE_DIR="worktrees"
else
  WORKTREE_DIR=".worktrees"
fi
```

### 2. 确保忽略规则存在

```bash
grep -q "^\\.worktrees/" .gitignore 2>/dev/null || echo ".worktrees/" >> .gitignore
grep -q "^worktrees/" .gitignore 2>/dev/null || echo "worktrees/" >> .gitignore
```

### 3. 创建工作树

```bash
git worktree add .worktrees/feature-功能描述 -b feature/功能描述 main
```

## 使用规则

1. 进入 worktree 后，所有提交、推送、测试都在该目录内完成
2. 一个 worktree 只服务一个明确任务
3. 若多个任务共享核心文件，不要假装可以并行，先停下来重拆任务
4. 不要在 worktree 内再频繁切换到其他分支

## 清理规则

在合并或放弃任务后，才允许清理：

```bash
git worktree remove .worktrees/feature-功能描述
git branch -d feature/功能描述
```

若明确放弃任务且 Boss 已确认，可用强制清理：

```bash
git worktree remove .worktrees/feature-功能描述 --force
git branch -D feature/功能描述
```

## 与并行任务的关系

当 `parallel-delivery` 或并行代理需要隔离目录时：

1. 每个 lane 或每个子代理使用独立 worktree
2. lane 名称和分支名必须能追溯到任务
3. 最终由统一 owner 收口合流

## 禁止事项

1. 不要在 SVN 项目里尝试 worktree
2. 不要让多个任务共用同一个 worktree
3. 不要在 worktree 内随意 `git checkout` 到无关分支
4. 不要在未合并或未确认放弃时清理 worktree
5. 不要忽略同名分支或同名目录冲突
