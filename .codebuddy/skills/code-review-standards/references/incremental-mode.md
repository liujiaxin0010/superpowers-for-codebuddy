# 增量审查模式（Baseline Commit + Block 化）

本文件定义大范围 / 定时自动审查的执行模式。逐文件五维审查仍以各语言 `standards/*.md` + `references/*-review-checklist.md` 为准；本文件解决的是「审查哪些文件、按什么顺序、产物落到哪里」。

> 核心原则：**增量优先，全量兜底**。增量保节奏，全量保底线。

## 1. 审查模式判定

| 模式 | 触发 | 范围计算 |
|---|---|---|
| 增量（默认）| 日常 / 定时工作日 | 基于上次 **Baseline Commit** 的 `git diff --name-only <baseline>..HEAD` 取变更文件 |
| 全量（兜底）| 首次运行 / 周日 / Baseline 丢失 | 枚举所有源文件（排除项见 §4）|
| MR 触发 | MR event | 基于 MR 的 `base SHA..head SHA` 计算 diff |

Baseline 丢失或首次运行时**自动退化为全量**——这是安全兜底，不是错误。

## 2. Baseline Commit 锚点

- 每次审查报告**末尾必须记录 `Baseline Commit: <HEAD commit id>`**，作为下次增量审查计算 diff 的基准。
- 没有 Baseline 就无从计算「增量」；Baseline 的记录与读取是定时审查持续运转的基础设施。
- 读取顺序：优先读上一次 `.codebuddy-runtime/reviews/{上次date}/report.md` 末尾的 Baseline；缺失则全量。

## 3. 流程追踪（增量模式核心）

增量不是「只看 diff 文件」，而是「看 diff 文件影响的数据流」：

1. 从每个变更文件出发，分析其 import 链与调用关系
2. 推导该文件属于哪些数据流（可跨前后端）
3. 将上下游相关文件纳入审查范围
4. 流程追踪由 AI 阅读代码跟踪 import/调用链完成，**不依赖预定义流程图**（GitNexus 可用时优先用模式 D 调用链追踪加速）

## 4. Block 化分批

| 规则 | 说明 |
|---|---|
| 分组 | 按数据流分组为 Block |
| 大小 | 每个 Block ≤ 500 行 |
| 排序 | Block 按优先级排序（P0 优先），同优先级内按流程分组 |
| 标注 | 每个 Block 标注维度焦点 + 优先级级别 |
| 截断 | 资源 / 时间不足时低优先级截断；**P0 绝不截断**，超时也要跑完 |

维度与优先级（P0-P3）见 `references/review-cube.md`。

### 审查排除项

以下目录 / 文件不审查：`.worktrees/`、`vendor/`、`node_modules/`、`*_test.go`、`__tests__/`、`public/`、自动生成代码（按 `code-documentation.md` 识别）。

## 5. 产物目录结构

```
.codebuddy/
├── reviews/{date}/
│   ├── plan.md          # 审查计划（Block 列表 + 模式 + 范围）
│   ├── block-01.md      # 每个 Block 的审查结果
│   ├── block-02.md
│   └── report.md        # 汇总报告（末尾记录 Baseline Commit）
└── issues/ISS-{nnn}.md  # Critical 发现项（格式见 codebuddy-issue-format.md）
```

`.codebuddy/` 是业务项目运行时产物，应加入 `.gitnexusignore`；`issues/` 建议保留可追踪，`reviews/` 可按需 gitignore。

## 6. 汇总报告格式

```markdown
# 代码审查报告

## 审查信息
- 审查模式：增量 / 全量
- Baseline Commit: `{commit-id}`（增量）/ N/A（全量）
- 审查范围：{分支}（base: {abc} → head: {def}）
- 审查时间：YYYY-MM-DD HH:mm
- 触发方式：手动 / MR / 定时 Task#4
- Block 执行：{n}/{total}，截断：{None | "P2 及以下在 Block {n} 后截断"}

## 审查摘要
| 维度 | Critical | Warning | Info |
|------|----------|---------|------|
| P0 - 流程正确性 | {n} | {n} | {n} |
| ...（其余维度见 review-cube.md）|

## 问题列表
| 级别 | 文件:行号 | 维度 | 问题描述 | 建议修改 |
|------|-----------|------|----------|----------|

## 按数据流分组
### {flow name}
- [CRIT-001] {description} → ISS-{nnn}
- [WARN-001] {description}

## 已有 Issue 状态
| Issue ID | 状态 | 维度 | 描述 |
|----------|------|------|------|
| ISS-001 | Suspected Resolved | 安全性 | 涉及文件已变更 |

## AI 回击记录（如有）
| 审查项 | 回击原因 | 技术依据 |

## 修复确认
- [ ] Critical 问题已全部修复
- [ ] Warning 已处理或有合理理由推迟
- [ ] Info 已记录到技术债看板

**Baseline Commit**: `{current HEAD commit id}` — 下次增量 review 基于此 commit 计算 diff
```

## 7. 与缺陷闭环的衔接

- Critical 发现项在审查时同时写 `.codebuddy-runtime/issues/ISS-{nnn}.md`（格式见 `codebuddy-issue-format.md`），并经 `defect-tracking` 同步到 GitLab Issue。
- 定时审查（Task #4）由 `scheduled-automation` 编排，只生成审查输出文件，**不修改源代码**；修复由 `defect-tracking`（Task #9）在独立 Worktree 中进行。
