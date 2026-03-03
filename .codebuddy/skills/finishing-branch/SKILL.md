---
description: 完成开发分支，合并前的检查和清理流程
---

# 完成开发分支

当所有计划中的任务完成后，安全地收尾开发分支。包含测试验证、代码清理、worktree 清理和合并选项。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

## 触发条件

当实施计划中的所有任务都已完成且通过审查时激活。

---

## 1. 最终验证

```bash
# 运行完整测试套件
npm test  # 或对应的测试命令

# 检查未提交的更改
git status 2>/dev/null || svn status

# 检查遗留的 TODO/FIXME/HACK
grep -rn "TODO\|FIXME\|HACK\|XXX\|console\.log\|System\.out\.print" src/ \
  --include="*.ts" --include="*.js" --include="*.py" \
  --include="*.java" --include="*.go" --include="*.vue" \
  2>/dev/null || true
```

**展示验证输出作为证据。**

## 2. 代码清理

- [ ] 移除所有调试代码（`console.log`、`print`、`System.out.println`）
- [ ] 移除注释掉的代码块
- [ ] 确保文件格式化正确
- [ ] 确认三层代码自文档全部更新

## 3. 全局代码审查

如果使用了子代理驱动开发，此时应进行**全局代码审查**：
- 审查所有任务的代码作为一个整体
- 检查模块之间的集成
- 确认总体架构一致性
- 向 Boss 提交全局审查报告

## 4. 向 Boss 展示选项

```
Boss，所有任务已完成，最终验证通过。请选择下一步操作：
```

| 选项 | 描述 |
|---|---|
| **A: 创建 PR/MR** | 推送分支并创建合并请求（适合团队审查） |
| **B: 合并到主干** | 直接合并回 trunk/main（适合个人项目） |
| **C: 保持分支** | 不合并，保留当前分支（适合还不确定的情况） |
| **D: 放弃分支** | 删除分支及所有更改（适合实验/原型失败） |

## 5. 执行操作

### Git 项目

```bash
# 选项 A: 创建 PR
git push -u origin feature/功能描述
# 如果安装了 gh CLI:
gh pr create --title "功能描述" --body "详细说明"

# 选项 B: 本地合并
git checkout main
git merge feature/功能描述
git push

# 选项 D: 放弃
git checkout main
git branch -D feature/功能描述
```

### Git Worktree 清理（如果使用了 worktree）

```bash
# 合并后清理 worktree
git worktree remove .worktrees/feature/功能描述 2>/dev/null
git branch -d feature/功能描述

# 放弃时强制清理
git worktree remove .worktrees/feature/功能描述 --force 2>/dev/null
git branch -D feature/功能描述

# 验证 worktree 已清理
git worktree list
```

### SVN 项目

```bash
SVN_ROOT=$(svn info --show-item repos-root-url)

# 选项 B: 合并到主干
svn switch "$SVN_ROOT/trunk"
svn merge "$SVN_ROOT/branches/feature-功能描述"
svn commit -m "merge: 合并功能分支 功能描述"

# 清理分支（可选）
svn delete "$SVN_ROOT/branches/feature-功能描述" -m "cleanup: 删除已合并分支"

# 选项 D: 放弃
svn switch "$SVN_ROOT/trunk"
svn delete "$SVN_ROOT/branches/feature-功能描述" -m "cleanup: 放弃功能分支"
```

## 6. 最终检查清单

- [ ] ✅ 所有测试通过（展示了证据）
- [ ] ✅ 没有未提交的更改
- [ ] ✅ 没有遗留的调试代码
- [ ] ✅ 三层代码自文档全部更新
- [ ] ✅ Worktree 已清理（如果使用了）
- [ ] ✅ Boss 已确认选择的操作
- [ ] ✅ 操作已执行并展示结果
