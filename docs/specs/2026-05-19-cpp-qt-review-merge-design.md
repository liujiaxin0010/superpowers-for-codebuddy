# C++/Qt 代码审查能力合并设计

- 状态: Draft
- 创建日期: 2026-05-19
- 作者: Boss + Claude
- 源目录: `D:/CODE/feature-flow/need-merge/`
- 目标项目: `superpowers-for-codebuddy`

## 1. 背景与目标

需将 `D:/CODE/feature-flow/need-merge/` 下的 C++/Qt 代码审查相关资产合并进 `superpowers-for-codebuddy` 项目，使本项目具备针对 EZStation/EZTools 两个 C++/Qt 项目的专项代码审查能力，输出标准化 XLSX 报告到 `D:/Review/`。

需合并的源资产：

- `code_standard_ezs.md`（EZStation C++/Qt 规范，9.3KB，日志宏 `LOG_MESSAGE`）
- `code_standard_ezt.md`（EZTools C++/Qt 规范，8.9KB，日志宏 `LOG_RECORD`，其余与 ezs 99% 相同）
- `C++&Qt代码review/agents/cpp-code-reviewer.md`
- `C++&Qt代码review/commands/code-review.md`（含 C++/Qt 智能路由分支）
- `C++&Qt代码review/commands/cpp-code-review.md`
- `C++&Qt代码review/rules/Coding-Standard.md`（通义灵码版，与 ezs 99% 相同）
- `C++&Qt代码review/skills/cpp-qt-code-reviewer-skill/`（含 SKILL.md、README.md、references/缺陷.md、references/code-analysis-guide.md，共 384 行）

## 2. 现状盘点

当前 `superpowers-for-codebuddy` 工作空间相关结构：

- `.codebuddy/agents/code-reviewer.md` — 通用 code-reviewer Agent（中文 Boss 风格）
- `.codebuddy/commands/code-review.md` — 通用代码审查命令（含 Web 专项分支，无 C++/Qt 分支）
- `.codebuddy/rules/` — 通用规则（注释、日志、跨平台 shell 等），**无 C++/Qt 专项规范**
- `.codebuddy/skills/` — 41+ skill，含 `code-review-standards`、`web-code-review`、`process-gatekeeper`、`xlsx`，**无 `cpp-qt-code-reviewer-skill`**
- `.claude/` — 仅 settings.local.json，未维护 skill/agent 镜像

## 3. 设计方案

### 3.1 方案选型

采用 **方案 A：完整迁移 + 智能路由扩展**。

### 3.2 目录结构改动

```
.codebuddy/
├── skills/
│   └── cpp-qt-code-reviewer-skill/        [新增]
│       ├── SKILL.md                        ← 改写路径引用：.lingma → .codebuddy
│       ├── README.md                       ← 改写路径引用
│       └── references/
│           ├── 缺陷.md                     ← 原样搬运
│           └── code-analysis-guide.md     ← 原样搬运
├── agents/
│   └── cpp-code-reviewer.md                [新增] ← 重写 frontmatter + Boss 铁律
├── commands/
│   ├── code-review.md                      [修改] ← 增补 EZStation/EZTools Qt 路由分支
│   └── cpp-code-review.md                  [新增] ← 改写路径引用
└── rules/
    └── cpp-qt-coding-standard.md           [新增] ← 合并 ezs/ezt/lingma 三份规范
```

`.claude/` 不动；`need-merge/` 源目录保留（用户自行处理）。

### 3.3 路由逻辑（核心：`.codebuddy/commands/code-review.md`）

在现有命令的「步骤 2 调用 process-gatekeeper」之前插入「步骤 1.5 智能路由判断」：

```
步骤 1.5: 智能路由判断
  - 提取待审查文件路径（参数 / 当前打开 / git diff）
  - 双条件检测（必须同时满足）：
    条件 A — 项目路径包含: ezstation | eztools | EZStation | EZTools
    条件 B — 文件扩展名: .cpp .h .hpp .c .cxx .hxx .ui .qrc .pro
  - 双条件同时满足 → 调用 cpp-qt-code-reviewer-skill 专项审查
                  → 输出 D:/Review/[name]_review.xlsx
                  → 流程终止（跳过后续 process-gatekeeper / 通用审查 / Web 专项）
  - 否则 → 继续步骤 2（原有 process-gatekeeper + 通用 + Web 专项流程）
          → C/C++ 标准类型由 code-review-standards skill 处理
```

设计依据：

- 与现有「通用 + Web 专项」路由架构同构，「C++/Qt 专项」作为第三条分支并列
- 双条件（路径 + 扩展名）避免误伤其他项目的 C/C++ 代码
- 专项路径直接终止后续流程，沿用 need-merge 原作者的设计意图：C++/Qt 专项审查走独立完整工作流（读取规范 → 缺陷映射 → 调用 xlsx skill 输出 XLSX），不复用通用流程的 process-gatekeeper / 五维审查 / Web 专项检查

### 3.4 规范合并（`.codebuddy/rules/cpp-qt-coding-standard.md`）

基于 ezs 版本为主，合并三份规范。差异仅在第 5 章「日志输出」，改写如下：

```markdown
## 5. 日志输出

> 本章节按项目类型分别说明日志宏与等级。两个项目共享其余编码规范（命名、注释、信号槽等）。

### 5.1 EZStation 项目（使用 LOG_MESSAGE 宏）

- 格式: LOG_MESSAGE(日志等级, 日志内容);
- 日志等级（typedef tagLogLevel ⇒ LOGLEVEL_E）:
  - EN_LOG_LEVEL_NOLOG   = 0  /* 不打印 */
  - EN_LOG_LEVEL_DEBUG   = 1  /* DEBUG   */
  - EN_LOG_LEVEL_INFO    = 2  /* INFO    */
  - EN_LOG_LEVEL_WARNING = 3  /* WARNING */
  - EN_LOG_LEVEL_ERROR   = 4  /* ERROR   */
  - EN_LOG_LEVEL_FATAL   = 5  /* FATAL   */
- 示例:
  LOG_MESSAGE(EN_LOG_LEVEL_INFO, QString("Device %1 TCP connected").arg(devId));

### 5.2 EZTools 项目（使用 LOG_RECORD 宏）

- 格式: LOG_RECORD(日志等级, 日志内容);
- 日志等级（typedef tagLogLevel ⇒ LOGLEVEL_E）:
  - LOG_LEVEL_DEBUG   = 1  /* DEBUG   */
  - LOG_LEVEL_INFO    = 2  /* INFO    */
  - LOG_LEVEL_WARNING = 3  /* WARNING */
  - LOG_LEVEL_ERROR   = 4  /* ERROR   */
  - LOG_LEVEL_FATAL   = 5  /* FATAL   */
- 示例:
  LOG_RECORD(LOG_LEVEL_INFO, "WebSocket connected successfully");

### 5.3 通用约束（两项目均适用）

- 日志内容必须使用英文，便于国际化和统一维护
- 不允许残留 console / print / qDebug / std::cout 等直接控制台输出
- 日志等级语义:
  - DEBUG:   开发阶段详细流程信息
  - INFO:    正常运行关键流程信息
  - WARNING: 不影响运行但需关注
  - ERROR:   影响正常运行的错误
  - FATAL:   导致无法继续运行的严重错误
```

其余 6 章（文件目录 / 缩进空格 / 命名 / 注释 / 信号槽 / 比较运算符）原样合并（三份本就 99% 一致）。

### 3.5 Agent 改写（`.codebuddy/agents/cpp-code-reviewer.md`）

frontmatter（按本项目风格）:

```yaml
---
name: cpp-code-reviewer
description: C++/Qt 代码审查专家。专注 EZStation/EZTools 项目的 .cpp/.h/.hpp/.c/.ui/.qrc/.pro 文件审查，调用 cpp-qt-code-reviewer-skill 生成 XLSX 报告到 D:/Review/。触发关键词："代码 review"、"cpp review"、"C++ 代码审查"、"Qt 代码审查"。
tools: read_file, replace_in_file, write_to_file, execute_command, search_content, search_file, use_skill, list_files, read_lints, delete_files
model: inherit
---
```

正文以原 `cpp-code-reviewer.md` 为基础，前置加入与 `code-reviewer.md` 一致的「⚠️ 三条铁律」与「禁止表演性赞同」段落：

1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定的设计问题时，必须先询问 Boss，不得擅自行动
3. 不得编写兼容性代码，除非 Boss 主动明确要求

保留原工作流：接收输入 → 准备审查 → 调用 cpp-qt-code-reviewer-skill → 处理 XLSX 输出 → 报告结果。

### 3.6 命令改写（`.codebuddy/commands/cpp-code-review.md`）

原文搬运，仅修改路径引用：

- `.lingma/rules/Coding-Standard.md` → `.codebuddy/rules/cpp-qt-coding-standard.md`
- `skills/cpp-qt-code-reviewer-skill/references/缺陷.md` → `.codebuddy/skills/cpp-qt-code-reviewer-skill/references/缺陷.md`

### 3.7 Skill 改写（`.codebuddy/skills/cpp-qt-code-reviewer-skill/`）

- `SKILL.md`：步骤 2「读取配置和规则」、步骤 3「加载参考材料」中所有 `.lingma/rules/Coding-Standard.md` 引用替换为 `.codebuddy/rules/cpp-qt-coding-standard.md`
- `README.md`：「规则来源」「技能结构」段落中 `.lingma/` 引用同步替换
- `references/缺陷.md`、`references/code-analysis-guide.md`：原样搬运，不改动

## 4. 验证策略

合并完成后人工自检（本项目无自动化测试）：

- [ ] `grep -rn "\.lingma" .codebuddy/` 应无残留（除非有意保留）
- [ ] `.codebuddy/rules/cpp-qt-coding-standard.md` 存在且包含 5.1 / 5.2 / 5.3 三节
- [ ] `.codebuddy/skills/cpp-qt-code-reviewer-skill/SKILL.md` 等文件存在
- [ ] `.codebuddy/agents/cpp-code-reviewer.md` frontmatter `model: inherit`，含 Boss 铁律三条
- [ ] `.codebuddy/commands/cpp-code-review.md` 存在
- [ ] `.codebuddy/commands/code-review.md` 已包含「步骤 1.5 智能路由判断」段
- [ ] 手工验证：构造一个 EZStation 路径下的 .cpp 文件路径，模拟 `/code-review` 调用，确认会路由到 cpp-qt-code-reviewer-skill
- [ ] 手工验证：构造一个 .js / .vue 文件路径，确认走原有 Web 专项流程
- [ ] 手工验证：构造一个非 EZStation/EZTools 项目的 .cpp 文件，确认走通用 code-review-standards 流程

## 5. 范围外（不做）

- 不删除 `D:/CODE/feature-flow/need-merge/` 源目录
- 不修改 `.claude/`、`docs/`（除本 spec）、`spec/`、`CODEBUDDY.md`、`README.md`
- 不引入新的 npm/python 依赖（依赖现有 `xlsx` skill 即可）
- 不改造已有的 `code-review-standards`、`web-code-review`、`process-gatekeeper` skill
- 不为路由分支增加单元测试（项目本无测试基建）

## 6. 风险与权衡

| 风险 | 缓解措施 |
|---|---|
| 项目路径关键字 `ezstation`/`eztools` 大小写匹配遗漏 | 路由规则同时匹配 4 种大小写形式：`ezstation`、`eztools`、`EZStation`、`EZTools` |
| 合并后的日志规范两节内容易混淆 | 5.1/5.2/5.3 三节标题明确，且 cpp-qt-code-reviewer-skill 审查时按项目路径自动选用对应章节 |
| Skill 内部仍有 `.lingma` 字样残留 | 验证清单含 grep 校验项 |
| 用户希望保留 EZS/EZT 两份独立规范 | 已在方案选型阶段确认采用单份合并（用户选择） |

## 7. 实施顺序（粗粒度）

1. 新增 `.codebuddy/rules/cpp-qt-coding-standard.md`
2. 新增 `.codebuddy/skills/cpp-qt-code-reviewer-skill/` 全套
3. 新增 `.codebuddy/agents/cpp-code-reviewer.md`
4. 新增 `.codebuddy/commands/cpp-code-review.md`
5. 修改 `.codebuddy/commands/code-review.md`（增补路由分支）
6. 跑验证清单
7. （待用户决定）是否 commit / 是否新建分支

详细 step-by-step 实施计划由 `writing-plans` skill 在 spec 批准后生成。
