请阅读以下技能并严格遵循：
1. `.codebuddy/skills/code-simplifier/SKILL.md`（代码简化策略）
2. `.codebuddy/skills/verification-before-completion/SKILL.md`（完成前验证）

**务必遵守三条铁律：**
1. 每次回复先称呼 "Boss"
2. 不确定的设计问题必须先问 Boss
3. 不写兼容性代码，除非 Boss 主动要求

**你的任务是：简化指定范围的代码。**

执行步骤：
1. 确定范围（路径参数或最近修改的文件）
2. 运行测试建立基线
3. 逐文件识别简化机会
4. 若 `cppQtProductVariant ∈ {station, tools}`（由 `.codebuddy/rules/cpp-qt-ez-style.md` 写入），加载 `.codebuddy/skills/code-review-standards/standards/cpp-qt-ez-common.md` + `cpp-qt-ez-logging-{variant}.md`，禁止在化简过程中违反（如把 `/* */` 改成 `//`、把 `emit` 换成 `Q_EMIT`、改变成员变量前缀等）；否则跳过本步
5. 向 Boss 展示简化计划
6. 确认后逐步执行，每步运行测试
7. 全量测试通过后更新文档
8. 展示前后对比

$ARGUMENTS
