请按以下顺序阅读并严格遵循：
1. 引擎仓库根目录 `CHANGELOG.md`（模板版本与变更记录）
2. `.codebuddy/skills/event-triggers/SKILL.md`（接收器模板归属）
3. `.codebuddy/skills/scheduled-automation/SKILL.md`（调度模板归属）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在当前业务项目里，对照引擎 `CHANGELOG.md` 检查所有**已实例化模板**的版本差异，产出迁移清单；经 Boss 确认后应用升级。

执行步骤：

1. **定位双方**：
   - 业务项目根目录（当前目录）；引擎仓库路径（询问 Boss 或从安装记录推断）
   - 在引擎仓库自身运行 → 输出 `BLOCKED`（引擎无"已实例化模板"可查）

2. **盘点已实例化产物及版本**：
   - 扫描业务项目内：`webhook-receiver.js`、`event-triggers.config.json`、`automation-settings.json`、调度配置（crontab 片段 / schtasks / Pipeline Schedules 登记）、`commit-msg-lint.sh`、`ci-poll.sh`
   - 版本识别：JS 头部 `TEMPLATE_VERSION` / JSON `_templateVersion`；**无标注一律视为 pre-1.1.0**

3. **对照 CHANGELOG 列落后项**：
   - 每个落后模板输出：当前版本 → 最新版本、变更摘要（尤其破坏性认知修正）、影响面（会不会挂死/漏护栏）

4. **产出迁移清单**（只读，默认不改动）：
   - 逐模板给出升级动作：整文件替换 or 增补字段；**本地配置值（路径/端口/allowlist/密钥引用）必须保留**，逐项列出迁移映射
   - 标注升级后的验证命令（如 `unattended-permission-checklist.md` §4 的最小验证）

5. **应用（须 Boss 确认）**：
   - 确认后执行替换/增补，重启接收器或重载调度；全程不直推 main，改动走 MR
   - 验证通过后输出结构化报告：升级了什么、保留了什么本地值、验证证据

补充约束：
- 默认只读分析；未经确认不落任何改动
- 密钥永不入文件：升级过程不得把 `GITLAB_WEBHOOK_SECRET` 等写进配置
- 生成文档默认中文

$ARGUMENTS
