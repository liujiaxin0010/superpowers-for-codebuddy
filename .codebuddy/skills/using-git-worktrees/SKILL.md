---
description: Git Worktree 隔离开发，避免分支切换干扰
---

# Git Worktree 隔离开发

为每个功能创建隔离的 Git worktree，避免分支切换的上下文开销和未提交更改的风险。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

## 何时使用

- 需要在已有项目上开发新功能，且不想影响当前工作目录
- 需要同时维护多个功能分支
- 并行代理分发时，每个代理需要独立的工作目录
- **仅适用于 Git 项目**（SVN 项目不支持 worktree）

## 初始化流程

### 1. 检测 worktree 目录

```bash
# 检查是否已有 worktree 目录
if [ -d ".worktrees" ]; then
    WORKTREE_DIR=".worktrees"
elif [ -d "worktrees" ]; then
    WORKTREE_DIR="worktrees"
else
    WORKTREE_DIR=".worktrees"
    mkdir -p "$WORKTREE_DIR"
fi
```

### 2. 确保 worktree 目录被忽略

```bash
# 确认 .gitignore 中包含 worktree 目录
grep -q "^\.worktrees/" .gitignore 2>/dev/null || echo ".worktrees/" >> .gitignore
grep -q "^worktrees/" .gitignore 2>/dev/null || echo "worktrees/" >> .gitignore
```

### 3. 创建功能 worktree

```bash
FEATURE_NAME="feature/告警联动"
WORKTREE_PATH="$WORKTREE_DIR/$FEATURE_NAME"

# 创建 worktree + 新分支
git worktree add "$WORKTREE_PATH" -b "$FEATURE_NAME" main

# 进入 worktree
cd "$WORKTREE_PATH"

# 安装依赖（如果项目需要）
npm install 2>/dev/null || mvn dependency:resolve 2>/dev/null || pip install -r requirements.txt 2>/dev/null || true

# 运行基准测试，确保基线干净
# 记录测试结果作为后续回归对比的基线
```

## 开发流程

```
在 worktree 中正常开发
  ↓
所有更改都隔离在 worktree 目录中
  ↓
主工作目录完全不受影响
  ↓
开发完成后合并回主分支
  ↓
清理 worktree
```

### 在 worktree 中工作

```bash
cd .worktrees/feature/告警联动

# 正常开发...
# 所有 git 操作（commit/push）都在这个 worktree 中独立进行

git add .
git commit -m "feat: 实现告警联动规则引擎"
```

### 合并与清理

```bash
# 回到主工作目录
cd /path/to/main/repo

# 合并功能分支
git merge feature/告警联动

# 清理 worktree
git worktree remove .worktrees/feature/告警联动

# 删除功能分支（可选）
git branch -d feature/告警联动
```

## 与并行代理的配合

当使用 `dispatching-parallel-agents` 并行分发任务时：

```bash
# 为每个并行任务创建独立 worktree
git worktree add .worktrees/task-1 -b task/linkage-rule-engine main
git worktree add .worktrees/task-2 -b task/linkage-action-executor main
git worktree add .worktrees/task-3 -b task/linkage-log-service main

# 每个子代理在各自的 worktree 中独立工作
# 完全不会互相干扰
```

## 注意事项

- 同一分支不能同时被两个 worktree 检出
- worktree 中不要使用 `git checkout` 切换分支
- 清理 worktree 之前确保所有更改已提交或已合并
- SVN 项目不支持 worktree，使用标准分支管理
