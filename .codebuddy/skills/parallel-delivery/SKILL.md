---
name: parallel-delivery
description: 多 lane 并行交付技能。用于将长任务拆分成低耦合子任务，为每个 lane 明确文件边界、验证命令和最终合流 owner，并配合 worktree 或独立会话执行。
---

# 并行交付（Parallel Delivery）

把长任务拆成多个低耦合 lane，并在合流前保持边界清晰、证据充分。

## 何时使用

- 一个任务可拆成 2 个以上低耦合子项
- 并行推进能明显节省时间
- 有明确 owner 负责最终集成和质量门禁

## 必备输入

1. 已批准的 `plan`
2. 子任务拆分
3. 每个子任务允许修改的目录
4. 每个子任务验证命令
5. 最终收口 owner

## 执行流程

1. 先检查子任务能否并行：
   - 不共享核心文件
   - 不互相依赖输出
   - 测试可独立运行
2. 使用 `task-contracts` 生成 `parallel-delivery` 合同
3. 为每个 lane 写清：目标、边界、验证命令、依赖关系
4. Git 项目优先使用 `using-git-worktrees`
5. 非 Git 项目使用独立 session，并严格限制文件边界
6. 所有 lane 结束后，由 owner 统一执行：
   - 冲突检查
   - 集成验证
   - `/code-review`
   - 质量门禁

## 阻断条件

- 多个 lane 同改同一核心文件
- 没有统一 owner
- 子任务拆分不清，仍然强耦合
- 只交代码，不交验证证据

## 参考

- lane 清单：`references/lane-checklist.md`
