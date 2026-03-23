---
name: writing-skills
description: 编写与重构技能的元技能。用于创建新 skill、重写现有 SKILL.md、补齐触发描述、选择合适的 skill 模式、设计 references/templates/scripts 结构，并把教程式技能改造成协议式技能。用户提到“创建 skill/优化 skill/重写 SKILL.md/设计技能触发/改造 skill 结构”时触发。
---

# 创建新技能

本技能不是教“怎么写 Markdown”，而是教“怎么把经验压缩成另一个 AI 可执行的 skill”。

## 资源加载规则

当不确定某个 skill 应该走 Mindset / Navigation / Process / Tool 哪种模式时，再读取：

- `references/pattern-selection-matrix.md`

当需要输出“新建 skill / 重写 skill”的结构化设计简报时，再读取：

- `templates/skill-design-brief.md`

当已经写完一个 skill，准备自检其触发、结构和资源装载是否合格时，再读取：

- `templates/skill-self-review.md`

当需要评估已写好的 description 质量时，参考以下标准：

| 质量等级 | 特征 | 示例 |
|---|---|---|
| 差 | 只有 WHAT，没有 WHEN 和 KEYWORDS | “处理文档相关功能” |
| 中 | 有 WHAT + WHEN，缺少 KEYWORDS | “用于代码审查，任务完成时触发” |
| 好 | WHAT + WHEN + KEYWORDS + 反向排除 | xlsx skill 的 description |

不要每次写 skill 都先读整份说服文档。

## 何时使用

1. 新建一个项目内 skill
2. 重写已有 skill 的 `SKILL.md`
3. 补齐 `name/description`
4. 决定是否拆出 `references/`、`templates/`、`scripts/`
5. 把教程式正文改造成协议式正文

## 阻断条件

出现以下任一情况时，先 `BLOCKED` 或先补输入，而不是直接开写：

1. 说不清这个 skill 要解决什么失败行为
2. 没法判断是新建、重写还是局部补强
3. 用户要的其实不是 skill，而是普通文档、README 或培训材料
4. 不知道当前项目的 skill 规范，就准备套旧格式

## 元设计协议

1. 先收集失败行为，而不是先写规则
2. 再选 skill 模式，而不是直接开写
3. 再决定主文件只保留什么、哪些内容必须下沉
4. 最后才写 frontmatter、正文协议和资源触发

frontmatter 只保留：

```yaml
---
name: skill-name
description: skill 做什么、什么时候触发、用户会怎么说
---
```

不要再写旧格式里的 `alwaysApply`、`paths` 等字段，当前项目内 skill 规范不使用这些字段。

## 主文件底线

主 `SKILL.md` 只保留：

1. 高质量 `name/description`
2. 何时使用 / 何时阻断
3. 关键约束
4. 决策协议或工作流
5. 资源加载规则
6. 禁止事项

优先下沉：

1. 长示例
2. 大段模板
3. 变体很多的细节规则
4. 只在特定阶段才需要读取的说明

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
6. 不要写完 skill 却不做自检
