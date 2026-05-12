请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/pending-decisions/SKILL.md`（待决策项持久化）
2. `.codebuddy/skills/file-based-memory/SKILL.md`（文件记忆边界，避免越界）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
作为待决策项的快捷入口，按子命令分发：

```
/pending list [phase=brainstorm|spec-lite|...] [status=pending|partial|answered|deferred|dropped]
/pending add  question="..." options="A|B|..." phase=<phase> [linkedDocs=<path,path,...>]
/pending answer id=PD-YYYYMMDD-NNN answer="..." [syncTo=<path>]
/pending defer id=PD-YYYYMMDD-NNN reason="..."
/pending drop  id=PD-YYYYMMDD-NNN reason="..."
/pending sweep            # 阶段切换 / handoff 前扫描所有 pending+partial 项
/pending lint             # 跑结构契约校验
```

执行步骤：
1. 解析子命令；缺参数或不识别 → `BLOCKED` 并提示正确语法
2. 若 `docs/pending-decisions.md` 不存在：
   - `list/answer/defer/drop/sweep/lint` → 返回提示“暂无待决策项”，不报错
   - `add` → 按模板创建文件后继续
3. 对所有写操作（add/answer/defer/drop）：
   - 写完后运行 `.codebuddy/skills/pending-decisions/scripts/lint-pending.sh`
   - lint 失败必须 `BLOCKED` 并返回缺失段落清单
4. `answer` 子命令必须强制同步结论到 `linkedDocs` 中的主文档（spec/brainstorm/plan）：
   - 若 `syncTo` 显式给出，写入指定路径
   - 否则使用记录中的 `linkedDocs` 第一条
   - 同步失败 → 回滚 status 为 `pending`，返回 `BLOCKED`
5. `sweep` 子命令输出格式：
   ```
   Boss，本会话存在 N 条未收敛待决策项：
   - PD-... [phase=...] question 简要描述（status=pending/partial）
   ...
   建议先 /pending answer / defer / drop 后再切阶段。
   ```
6. 任何写操作后，在回复末尾追加：
   `已更新 docs/pending-decisions.md（影响 IDs: ...）。`

注意：
- 该命令不直接进入 brainstorm/spec-lite 流程，只负责待决策项的增删改查与扫描
- 不要在 `add` 子命令里替 Boss 决策——仅记录问题与选项，等 Boss 后续 `/pending answer`
- 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
