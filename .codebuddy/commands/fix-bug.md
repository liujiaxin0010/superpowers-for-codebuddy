---
description: 根据问题单（网址/截图/描述）定位并修复代码缺陷
---

# /fix-bug 问题单修改

请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/process-gatekeeper/SKILL.md`（流程硬门禁）
2. `.codebuddy/skills/task-contracts/SKILL.md`（统一任务合同）
3. `.codebuddy/skills/bug-fix/SKILL.md`（问题单修复方法论）
4. `.codebuddy/templates/task-contracts/bugfix.md`（Bugfix 合同模板）

根据问题单信息，全流程完成缺陷定位与修复。

## 输入方式

- **网址**：提供问题单URL（需Chrome DevTools MCP）
- **截图**：上传问题单截图（需图片理解模型）
- **描述**：直接描述问题现象
- **可选**：关联代码文件、修改方案、预期现象

## 执行步骤

### 第一步：读取问题单

- 🔸 **网址输入**：调用 `chrome-devtools` MCP 读取网页，提取问题单号、描述、现象、期望行为
- 🔸 **截图输入**：解析图片内容，提取问题单信息（不调用MCP）
- 🔸 **描述输入**：直接从用户描述中提取关键信息

### 第一步半：生成 bugfix contract

1. 按 `.codebuddy/templates/task-contracts/bugfix.md` 生成最小执行合同
2. 若缺少复现条件、期望/实际行为、允许修改范围或验证方式：调用 `process-gatekeeper`（`command=fix-bug`）并返回 `BLOCKED`
3. 合同确认后再进入定位与修改

### 第一步四：失败回归测试（强制门禁，M/H 级不可跳过）

1. 按 `.codebuddy/skills/bug-fix/templates/regression-test-contract.md` 生成回归测试合同
2. **在动任何业务代码之前**，先写一个能稳定复现 bug 的失败测试
3. 独立执行该测试，记录完整失败输出（stdout+stderr+退出码），保存路径写入 bugfix contract 的 `failingRegressionTestEvidence`
4. 连续运行 3 次确认稳定失败；若 flaky，必须解决稳定性后再进入下一步
5. 缺少 `failingRegressionTestPath / failingRegressionTestCommand / failingRegressionTestEvidence` 三件套之一 → 返回 BLOCKED
6. 仅当问题是 L 级 (<=2 文件单模块) 且 Boss 明确 OK 时，可以省略正式失败测试，但必须记录"省略理由 + 手动复现证据"到 `docs/progress.md`
7. 线上紧急 hotfix 允许先修后补测试，但必须在 24 小时内补齐并登记 `docs/findings.md`

### 第二步：上下文读取与问题定位

使用 `bug-fix` 技能的**上下文分层读取策略**：

#### 用户提供了文件时：
1. 完整读取主文件（>2000行则分段读取）
2. 提取关键变量名、方法名、类名等关键词
3. 使用 `search_content` 并行搜索关键词在项目中的使用、定义、引用位置
4. 读取相关文件，优先级：引用文件 > 定义文件 > 相似逻辑文件
5. 构建完整上下文，绘制调用关系，标记所有可能修改位置

#### 用户未提供文件时：
1. 基于问题描述提取功能模块、业务场景关键词
2. 搜索相关代码文件、配置文件、数据结构定义
3. 读取最相关的候选文件
4. 确认问题位置，无法确定则向用户列出候选文件

**完成后执行上下文完整性检查清单（见 bug-fix 技能）**

### 第三步：修改分析与方案生成

1. **多维度分析**：代码逻辑、变量使用、依赖关系、相似模式对比
2. **全面修改点识别**（见 bug-fix 技能的必查检查项）
3. **按格式输出修改方案**（见 bug-fix 技能的修改方案输出格式）
4. 如用户提供了方案：验证正确性 → 检查完整性 → 补充遗漏 → 风险评估

**等待用户确认后再执行修改**

### 第四步：精准执行修改

1. 执行 bug-fix 技能的**修改前验证流程**
2. 使用 `replace_in_file` 按修改点列表依次执行
3. 执行 bug-fix 技能的**修改后验证流程**
4. 异常处理：old_str不唯一→扩大范围；文件变更→重新读取；发现新问题→先询问用户
5. **修复后必须重新运行第一步四中登记的失败测试**，展示完整通过输出与退出码 0；与修复前失败输出做前后对比，同步附到 `docs/quality/fix-bug-<bug-id>-evidence.md`

### 第五步：输出修改记录

按 bug-fix 技能的**修改完成输出格式**输出结果，并补充：

- bugfix contract 摘要
- 最小复现关闭证据
- 回归结果
- 剩余风险与 owner
