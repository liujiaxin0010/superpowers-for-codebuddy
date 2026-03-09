# devflow-ai 单入口封装

如果你想把当前项目作为“一个总 agent + 一个入口命令”导入到其他项目，推荐使用：

- 总控 agent：`.codebuddy/agents/devflow-ai.md`
- 单入口命令：`.codebuddy/commands/devflow-ai.md`
- 总控 skill：`.codebuddy/skills/devflow-router/SKILL.md`

## 使用方式

### 方式 1：完整导入

复制整个 `.codebuddy/` 与 `CODEBUDDY.md` 到目标项目。

然后只使用一个入口：

```text
/devflow-ai <你的需求>
```

### 方式 2：最小导入

至少复制以下目录和文件：

1. `CODEBUDDY.md`
2. `.codebuddy/commands/devflow-ai.md`
3. `.codebuddy/agents/devflow-ai.md`
4. `.codebuddy/skills/devflow-router/`
5. `.codebuddy/skills/task-contracts/`
6. `.codebuddy/skills/process-gatekeeper/`
7. `.codebuddy/templates/task-contracts/`

## 单入口能做什么

- 自动识别任务类型
- 遇到模糊需求时先分成 `must-brainstorm / should-brainstorm`
- 对严重模糊需求强制先路由到 `/brainstorm`
- 自动选择下游工作流
- 缺少前置条件时自动阻断并回退
- 保持统一的合同、门禁、证据和 owner 约束

## 适合的导入场景

- 其他仓库不想暴露太多命令
- 团队只希望记住一个入口
- 需要统一把需求收束到 spec / bugfix / review / parallel lane 等固定工作流
