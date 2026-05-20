请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/openapi-creator/SKILL.md`（OpenAPI 接口创建五阶段工作流）
2. `.codebuddy/skills/openapi-creator/references/openapi-spec.md`（平台类 OpenAPI 接口定义规范 2024.1.0）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
按 `openapi-creator` 技能执行完整五阶段流程，为宇视平台生成符合规范的 OpenAPI 接口定义。

执行步骤：
1. **阶段一 · 需求澄清**：按技能的 4 个必澄清项分组提问（ServiceURI+资源 / 操作+分页+批量 / 关键参数+排序 / 文件+鉴权），输出「接口需求确认」摘要，**等待 Boss 明确确认后**才进入阶段二
2. **阶段二 · 生成**：
   - 通过 chrome-devtools MCP 下载公司标准字段库《服务器产品数据项标准.docx》（首次需向 Boss 索取 GitLab/OA 凭据）
   - 解析字段库：优先方式 A（docx 技能解包，**当前项目无 docx 技能则跳过**），回退方式 B（python-docx）
   - 按技能的 Markdown 模板与生成规则产出接口定义文档，"字段标准引用"列逐字段填写
   - 生成后立即列出所有"未定义"字段并提醒 Boss
3. **阶段三 · 校验**：运行 `scripts/validate_api.py`，按 A/B/C/D 四类规则校验；结果严格按 🔴必须修复 / 🟡建议修复 分组；交互式修复，自动跳过类无需询问，必须询问类一次问一个
4. **阶段四 · Markdown 审查**：展示完整 Markdown 文档 + 校验摘要 + "未定义"字段修订提案提醒，**等待 Boss 明确确认**
5. **阶段五 · YAML 导出**：仅在校验通过且 Boss 确认 Markdown 后，生成 OpenAPI 3.0 YAML，校验格式，清理所有临时文件（只保留最终 `.md` 和 `.yaml`）

补充约束：
- 阶段一、阶段四的 Boss 确认是硬门禁，不得跳过
- 文件类型映射、required 数组、enum 约束严格按技能的「YAML 生成规则」执行
- 字段未在公司标准字段库中找到时，提醒 Boss 先提交修订提案
- docx 解析方式 A 依赖 `.codebuddy/skills/docx`（当前项目未提供），缺失时自动用方式 B
- 若作为 `/brainstorm` 阶段四「接口设计」子阶段的联动入口被调用：头脑风暴阶段只按本技能规则约束「接口清单 + 关键字段」草案，正式的定义/校验/YAML 导出仍走本命令完整流程
- 新增/更新的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

$ARGUMENTS
