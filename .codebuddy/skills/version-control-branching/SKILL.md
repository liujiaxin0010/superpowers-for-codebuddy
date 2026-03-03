---
description: 版本控制分支管理策略和工作流
---

# 版本控制分支管理

在设计批准后创建隔离的开发分支，支持 Git 和 SVN 两种版本控制系统。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

## 触发条件

在头脑风暴完成、设计获得 Boss 批准后激活。

## 第一步：检测版本控制系统

```bash
if [ -d .git ]; then
    echo "VCS=git"
elif [ -d .svn ] || svn info &>/dev/null; then
    echo "VCS=svn"
else
    echo "VCS=未知，请询问 Boss"
fi
```

---

## Git 工作流

### 创建分支（推荐使用工作树实现隔离）

```bash
# 方式一：使用 Git Worktree（推荐，实现完全隔离）
git worktree add ../项目名-功能描述 -b feature/功能描述

# 切换到工作树目录
cd ../项目名-功能描述

# 方式二：普通分支（如果不需要并行开发）
git checkout -b feature/功能描述
```

### 设置工作环境
```bash
# 安装依赖
npm install  # 或 pip install -r requirements.txt 等

# 运行测试确认基线干净
npm test
```

### 常用命令
```bash
git status                    # 查看状态
git diff                      # 查看变更
git add . && git commit -m "msg"  # 提交
git log --oneline -10         # 查看最近提交
git worktree list             # 列出所有工作树
```

### 命名约定

| 类型 | 分支名 |
|---|---|
| 功能 | `feature/功能描述` |
| 修复 | `fix/bug描述` |
| 重构 | `refactor/描述` |

---

## SVN 工作流

### 创建分支

```bash
# 获取仓库根 URL
SVN_ROOT=$(svn info --show-item repos-root-url)

# 创建功能分支
svn copy "$SVN_ROOT/trunk" "$SVN_ROOT/branches/feature-功能描述" \
    -m "创建功能分支: 功能描述"

# 切换到功能分支
svn switch "$SVN_ROOT/branches/feature-功能描述"
```

### 设置工作环境
```bash
# 确认已切换到正确分支
svn info | grep "Relative URL"

# 安装依赖
npm install  # 或 pip install -r requirements.txt 等

# 运行测试确认基线干净
npm test
```

### 常用命令
```bash
svn status                    # 查看状态
svn diff                      # 查看变更
svn add --force . 2>/dev/null # 添加新文件
svn commit -m "msg"           # 提交
svn log -l 10                 # 查看最近提交
svn info                      # 查看当前分支信息
```

### 命名约定

| 类型 | 分支路径 |
|---|---|
| 功能 | `branches/feature-功能描述` |
| 修复 | `branches/fix-bug描述` |
| 重构 | `branches/refactor-描述` |

---

## 验证干净基线

无论使用哪种版本控制，创建分支后都必须确认：
- ✅ 所有现有测试通过
- ✅ 没有未提交的更改
- ✅ 依赖安装完整
- ✅ 开发服务器能正常启动（如适用）

基线验证失败时，立即向 Boss 报告，不要继续。
