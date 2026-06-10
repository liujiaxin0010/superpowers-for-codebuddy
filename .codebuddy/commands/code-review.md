请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/code-review-standards/SKILL.md`（通用审查）
3. `.codebuddy/skills/web-code-review/SKILL.md`（Web 专项审查）
4. `.codebuddy/skills/cpp-qt-code-reviewer-skill/SKILL.md`（EZStation/EZTools Qt 专项审查）
5. `.codebuddy/skills/xlsx/SKILL.md`（XLSX 输出）

你的任务是：
在门禁约束下执行统一代码审查，并按"项目路径 + 文件扩展名"双条件智能路由到 EZStation/EZTools Qt 专项流程或通用流程。

执行步骤：
0. 阶段计时（供 `/metrics` §6 周期时间，建议执行）：开始时 `node .codebuddy/skills/delivery-metrics/scripts/stage-event.js review start --task=<规格/任务名>`；本命令结束（含 BLOCKED）前同参数执行 `end`。脚本缺失则跳过，不阻断。
1. 解析可选参数：`spec=<path>`、`tier=<L|M|H>`、`plan=<path>`
1.5. **智能路由判断（EZStation/EZTools Qt 专项分支）**：
   - 提取待审查文件路径（参数 / 当前打开 / git diff）
   - 双条件检测（必须同时满足才路由到专项）：
     * 条件 A — 项目路径含: `ezstation` | `eztools` | `EZStation` | `EZTools`（大小写不敏感）
     * 条件 B — 文件扩展名: `.cpp` `.h` `.hpp` `.c` `.cxx` `.hxx` `.ui` `.qrc` `.pro`
   - **双条件同时满足** → 调用 `cpp-qt-code-reviewer-skill` 专项审查
     * 路径含 `ezstation` → 按规范 5.1 节 `LOG_MESSAGE` 宏审查
     * 路径含 `eztools` → 按规范 5.2 节 `LOG_RECORD` 宏审查
     * 输出 `D:/Review/[name]_review.xlsx`
     * 流程终止（跳过后续步骤 2-10：不走 process-gatekeeper、通用五维、Web 专项、注释门禁等）
   - **否则** → 继续步骤 2（原有通用流程；C/C++ 标准类型由 `code-review-standards` 处理）
2. 调用 `process-gatekeeper`（`command=code-review`）
3. 若阻断：输出阻断报告并停止
3.5. **diff 风险加权 + 强制门禁触发（OPT-R1）**：
   - 运行 `node .codebuddy/skills/code-review-standards/scripts/diff-risk.js --range=<目标分支>...HEAD`（无远端则 `HEAD~1..HEAD`），基于**实际 diff**（代码文件的新增行，自动排除文档/测试/`.sample`）判定风险
   - 按 `reviewDepth` 定强度：`deep`=逐文件深审 + 强制下列门禁；`standard`=常规五维；`light`=纯文档/测试快速路径（五维择要，省人也省 token）
   - 按 `mandatoryGates` **强制联动**：命中 `/security-review` / `/perf-check` / `/data-safety-check` 则该门禁必须在本次审查内执行或已有通过记录，否则 BLOCKED 并提示先跑对应命令——**触发依据是 diff 命中的代码信号（鉴权/加密/DDL/查询等），不靠读 spec 关键词，杜绝漏触发**
   - 把风险维度与证据写入审查报告"风险评估"章节
4. 若通过：执行通用五维审查；对前端文件追加 Web 专项审查
5. 审查阶段严格只读：先输出问题清单（按严重程度分组），**不得直接修改代码**
6. 输出“修复建议列表 + 建议命令”，等待 Boss 明确确认后再进入修复流程
7. 强制检查日志规范：
   - 是否沿用项目日志结构与字段
   - 是否存在中文日志内容
   - 是否残留控制台输出（console/print/System.out/fmt.Print）
8. 强制检查代码注释规范（依据 `.codebuddy/rules/code-comment-conventions.md`）：
   - **硬门禁**（BLOCKED）：
     - L1 核心模块新增 > 5 行的函数缺中文函数头注释
     - TODO / FIXME 不带工单号
     - 出现英文的非技术术语注释
     - 过时注释（与代码语义不符）
   - **软门禁**（WARNING）：
     - 工具类/样板代码缺注释
     - 非 L1 模块函数缺函数头
     - 注释密度低于建议值
9. 输出时额外声明：
   - 证据是否完整
   - 是否存在越界修改
   - 未声明风险
   - merge / handoff owner
10. 输出报告：
    - **EZStation / EZTools Qt 专项分支**：`D:/Review/[filename]_review.xlsx`（由 cpp-qt-code-reviewer-skill 生成）
    - **通用分支**：`code-review-report.md`、`code-review-report.xlsx`，以及可选 `web-code-review-report.json`
11. **MR 行内化（GitLab 场景，P0-3）**：若审查目标是 GitLab MR 且 `gitlab-bridge` 写动作可用，除报告外把每条问题按"文件路径 + 行号"经 `mr.discussion` 贴成 MR **行内讨论线程**（含严重程度、问题、建议），配合项目设置「All threads must be resolved」形成软门禁。
    - 仍是只读 / MCP 不可用 → 退化：`mr.comment` 贴一条汇总评论，或仅产报告并输出人工提示，**不阻断**。
    - 行内讨论同样**默认只读、不改代码**；幂等：同一 MR 同一行不重复贴（已存在等价讨论则跳过）。
    - 可选：审查结论经 `commit.status`（`context=featureflow/review`）贴到 MR HEAD commit，便于在 MR 上一眼看状态（CE 下为展示态，非强制门禁）。

补充约束：
- `/code-review` 默认不承担自动修复职责
- 若 Boss 要求修复，先确认修复范围，再转入对应执行命令（如 `/execute-plan`、`/fix-bug` 或 `/code-self-check applyFix=true`）
- EZStation/EZTools 项目下的 C++/Qt 文件优先路由到 `cpp-qt-code-reviewer-skill`，遵循 `.codebuddy/rules/cpp-qt-coding-standard.md`
- 非 EZStation/EZTools 的 C/C++ 文件走通用流程，遵循 `code-review-standards` 多语言规范

$ARGUMENTS
