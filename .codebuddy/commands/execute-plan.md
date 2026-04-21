请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/executing-plans/SKILL.md`（计划执行）

**务必遵守四条铁律（见 CODEBUDDY.md §1）：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码
4. 触达生产数据 / 共享存储 / 表结构的操作必须先有 `data-safety` 合同且 Boss 显式签字

**你的任务是：**
先过门禁，再执行计划。

执行步骤：
1. 解析参数：`planPath`，可选 `spec=<path>`、`tier=<L|M|H>`
2. 调用 `process-gatekeeper`（`command=execute-plan`）
3. 若阻断：输出阻断报告并停止
4. **数据安全前置检查**：扫描计划中是否存在命中 `data-safety/SKILL.md#触发条件` 的步骤
   （DDL / 批量 DML / `rm -rf` / `kubectl delete` / 对象存储批量 / MQ purge / 迁移脚本 / 脱敏回灌）
   - 命中但缺少已签字的 `docs/plans/*-data-safety.md` → BLOCKED，回退到 `/data-safety-check`
   - 命中且已签字 → 在执行日志中记录报告路径与签字时间戳
5. 若通过：加载计划中的合同摘要，按批次执行，并展示测试证据
6. 执行质量门禁脚本（按平台分流，**不得双执行**）：
   - 先读取会话上下文的 `isWindows` 标记（由 CODEBUDDY.md §2 第 4 步启动时写入）
   - `isWindows=true`：`powershell -ExecutionPolicy Bypass -File .codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1`
   - `isWindows=false`：`bash .codebuddy/skills/process-gatekeeper/scripts/check-quality.sh`
   - 脚本失败时按 `.codebuddy/rules/cross-platform-shell.md §失败自愈流程` 处理，禁止同一命令重试 ≥ 2 次
7. 执行过程中同步兼容产物：
   - `spec/AI2AI/IMPLEMENTATION_PROGRESS.md`
   - `spec/AI2AI/IMPLEMENTATION_SUMMARY.md`
   - `spec/AI2AI/Architecture_Info.md`
   - `spec/AI2AI/Protocol_and_Data.md`
8. 若提供 `spec=<path>`，回填追踪链接：
   - `implementationProgressPath`
   - `implementationSummaryPath`
9. 输出时必须包含：验证证据、剩余风险、owner / handoff 建议
10. 若质量门禁 `BLOCKED`：停止收尾并返回修复项；通过后才允许宣告完成
11. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
