请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/system-test/SKILL.md`（系统测试）
3. `.codebuddy/skills/system-test/templates/system-test-scenarios.md`
4. `.codebuddy/skills/system-test/templates/system-test-report.md`

**务必遵守四条铁律（见 CODEBUDDY.md §1）。**

**你的任务是：**
在 `/unified-test` 之后、`/release` 之前执行系统测试，输出通过态报告。

执行步骤：

1. 解析参数：`/system-test scope=<name> [spec=<path>] [plan=<path>] [env=staging|uat]`
2. 调用 `process-gatekeeper`（`command=system-test`）
3. 若阻断：输出阻断报告并停止
4. 验证前置：`/requirement-coverage` 通过态 + `/unified-test` 通过态；任一缺失 → BLOCKED
5. 生成 / 更新系统测试剧本：`docs/quality/system-test-scenarios.md`
   - 每个需求 ID 至少一个场景
   - 场景包含前置 / 步骤 / 预期 / 实际 / 状态 / 证据
6. 执行数据准备脚本（只能作用于 staging / uat）
7. 按剧本执行每个场景，收集证据（日志 / 截图 / 录屏）
8. 发现的缺陷按 `defect-classification.json` 分级，写入 `docs/quality/system-test-defects.md`
9. 执行数据清理脚本
10. 生成 `docs/quality/system-test-report.md`，含通过率、覆盖对齐、缺陷摘要、发布建议
11. 判定：
    - 🔴 严重 / 🟠 高缺陷存在 → BLOCKED，禁止进入 `/release`
    - 未覆盖的需求 ID 存在 → BLOCKED，回退到 `/requirement-coverage` 或补剧本
    - 通过 → 回填 spec 的 `systemTestReportPath`
12. 实现者本人不得自审自测，必须由独立角色执行
13. 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
