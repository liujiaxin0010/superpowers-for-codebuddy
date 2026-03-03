请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`
2. `.codebuddy/skills/file-based-memory/SKILL.md`

你的任务是：
展示当前任务进度与门禁状态。

执行步骤：
1. 检查 `docs/findings.md` 与 `docs/progress.md`
2. 读取 `docs/specs/` 最新规格并加载 `GateContext`
3. 若存在 `docs/plans/` 最新计划，也一并读取
4. 若存在 `docs/quality/last-quality-gate.json`，读取最新质量门禁结果
5. 输出 `PASS/BLOCKED`、当前等级、缺失前置项、质量门禁与下一步命令

输出格式：

```
任务状态

阶段: {N}/{Total}
状态: {text}

门禁: {PASS|BLOCKED}
等级: {L|M|H}
缺失项: {list|none}
下一步: {command}
原因: {message}
质量门禁: {PASS|BLOCKED|UNKNOWN}
质量详情: 通过率 {x%|N/A} | 覆盖率 {x%|N/A} | 文档同步 {pass|blocked|unknown}

文件: findings {Y|N} | progress {Y|N} | spec {Y|N} | plan {Y|N}
错误记录数: {count}
```

若无活跃任务：

```
无活跃任务
运行 /spec-lite 或 /brainstorm 开始。
```

$ARGUMENTS
