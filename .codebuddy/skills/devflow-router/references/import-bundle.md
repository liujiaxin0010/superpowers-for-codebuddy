# Import Bundle

若要把 `Featureflow` 作为单入口导入到其他项目，最少复制：

1. `CODEBUDDY.md`
2. `.codebuddy/commands/Featureflow.md`
3. `.codebuddy/agents/Featureflow.md`
4. `.codebuddy/skills/devflow-router/`
5. `.codebuddy/skills/task-contracts/`
6. `.codebuddy/skills/process-gatekeeper/`
7. `.codebuddy/templates/task-contracts/`

如果要保留完整工作流能力，再一并复制对应的下游技能与命令。
