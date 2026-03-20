---
name: writing-skills
description: 编写与重构技能的元技能。用于创建新 skill、重写现有 SKILL.md、补齐触发描述、设计 references/templates/scripts 结构，以及把教程式技能改造成协议式技能。用户提到“创建 skill/优化 skill/重写 SKILL.md/设计技能触发”时触发。
---

# 创建新技能

本技能不是教“怎么写 Markdown”，而是教“怎么把经验压缩成另一个 AI 可执行的 skill”。

## 何时使用

以下场景优先使用本技能：

1. 新建一个项目内 skill
2. 重写已有 skill 的 `SKILL.md`
3. 补齐 `name/description`
4. 决定是否拆出 `references/`、`templates/`、`scripts/`
5. 把教程式正文改造成协议式正文

## 资源加载规则

### 调整措辞与高压封堵前

只有在需要强化“反合理化”“高服从度”表达时，才读取：

- `persuasion-principles.md`

### 不要怎么加载

1. 不要每次写 skill 都先读整份说服文档
2. 不要把 `persuasion-principles.md` 的理论内容复制回主 `SKILL.md`

## 技能设计工作流

### 1. 先收集失败行为

不要先写规则，先找“没有这个 skill 时，AI 会怎么做错”。

至少记录：

1. 会漏什么步骤
2. 会乱做什么事
3. 会在哪些压力下绕过流程

### 2. 选模式，而不是直接开写

写 skill 前先判断它更像哪一类：

1. **Mindset**：强调判断力、品味、反模式
2. **Navigation**：主文件只做路由，细节下沉
3. **Process**：多阶段、多检查点流程
4. **Tool**：高精度、低自由度、强约束操作

模式选错，skill 往往就会写成“又长又没用”。

### 3. 决定哪些内容留在主文件

主 `SKILL.md` 只保留：

1. 高质量 `name/description`
2. 何时使用 / 何时不用
3. 关键约束
4. 工作流或决策协议
5. 资源加载规则
6. 禁止事项

以下内容优先下沉：

1. 长示例
2. 大段模板
3. 变体很多的细节规则
4. 只在特定阶段才需要读取的说明

### 4. 正确写 frontmatter

frontmatter 只保留：

```yaml
---
name: skill-name
description: skill 做什么、什么时候触发、用户会怎么说
---
```

不要再写旧格式里的 `alwaysApply`、`paths` 等字段，当前项目内 skill 规范不使用这些字段。

### 5. 把正文写成协议，而不是教程

优先写：

1. 何时用
2. 何时阻断
3. 如何决策
4. 何时读取哪个资源
5. 哪些事绝不能做

少写：

1. “什么是 X”
2. 长篇通用最佳实践
3. 模型本来就知道的基础操作

### 6. 用真实任务验证

至少检查：

1. description 能不能触发 skill
2. 主文件是否足够短而不失真
3. resources 是否真的会在正确时机被读取
4. skill 是否能抵抗“简单点”“跳过吧”这类压力

## 质量检查清单

- [ ] `name` 合法且简洁
- [ ] `description` 同时回答 WHAT / WHEN / KEYWORDS
- [ ] 主文件没有堆太多教程化内容
- [ ] 有清晰的资源加载规则
- [ ] 有阻断条件或边界约束
- [ ] 有禁止事项或反模式
- [ ] 技能模式选择合理

## 常见反模式

1. 把“何时使用”写在正文，不写进 `description`
2. 把 skill 写成给人类看的培训材料
3. 创建 `references/` 但主文件从不说明何时读取
4. 把所有细节都堆进主 `SKILL.md`
5. 沿用旧 skill 格式，写入当前项目不识别的 frontmatter 字段

## 禁止事项

1. 不要把基础知识当 skill 价值
2. 不要用 README/CHANGELOG/安装说明污染 skill 目录
3. 不要为了“完整”复制大段模板到主文件
4. 不要忽略反模式与压力场景
5. 不要在没有失败样本时臆造复杂规则
