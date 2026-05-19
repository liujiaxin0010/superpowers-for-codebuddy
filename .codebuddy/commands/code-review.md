请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/code-review-standards/SKILL.md`（通用审查）
3. `.codebuddy/skills/web-code-review/SKILL.md`（Web 专项审查）
4. `.codebuddy/skills/cpp-qt-code-reviewer-skill/SKILL.md`（EZStation/EZTools Qt 专项审查）
5. `.codebuddy/skills/xlsx/SKILL.md`（XLSX 输出）

你的任务是：
在门禁约束下执行统一代码审查，并按"项目路径 + 文件扩展名"双条件智能路由到 EZStation/EZTools Qt 专项流程或通用流程。

执行步骤：
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

补充约束：
- `/code-review` 默认不承担自动修复职责
- 若 Boss 要求修复，先确认修复范围，再转入对应执行命令（如 `/execute-plan`、`/fix-bug` 或 `/code-self-check applyFix=true`）
- EZStation/EZTools 项目下的 C++/Qt 文件优先路由到 `cpp-qt-code-reviewer-skill`，遵循 `.codebuddy/rules/cpp-qt-coding-standard.md`
- 非 EZStation/EZTools 的 C/C++ 文件走通用流程，遵循 `code-review-standards` 多语言规范

$ARGUMENTS
