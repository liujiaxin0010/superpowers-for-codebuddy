# Prompt Contracts

`Featureflow` 把 prompt contract 视为任务的最小执行合同，而不是对话补充说明。

它至少回答 5 个问题：

1. 输入是什么
2. 输出是什么
3. 能改哪里
4. 怎么验证
5. 要交什么证据

## 最小模板

```text
任务：
范围：
相关文件：
不要做：
输出要求：
验证方式：
交付证据：
遇到不确定时：先停下来问
```

## 在当前仓库里的落点

- 规格模板：`.codebuddy/skills/spec-lite/template.md`
- 合同模板目录：`.codebuddy/templates/task-contracts/`
- 门禁：`.codebuddy/skills/process-gatekeeper/SKILL.md`
- 状态面板：`.codebuddy/commands/status.md`

## 推荐字段

- 任务目标
- 背景与上下文
- 允许修改
- 禁止修改
- 验证命令
- 交付物
- 风险提示
- 人工确认点
- owner
- 超边界时如何处理

## 适用场景

- 新功能需要 spec / plan / execute 串起来时
- bugfix 需要最小修复边界时
- refactor 需要声明行为不变项时
- test 任务需要先给覆盖目标再落用例时
- review / PR 需要把证据与 owner 固化时

## 推荐做法

1. 每类高频任务至少维护一份合同模板
2. 合同必须写验证命令，不能只写“请自测”
3. 合同必须写交付证据，不能只交 diff
4. 任务变化后要先回写合同，再继续执行
