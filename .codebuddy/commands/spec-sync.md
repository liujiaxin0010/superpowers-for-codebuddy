请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/spec-backfill/SKILL.md`（自动规格回填）
2. `.codebuddy/skills/spec-organization/SKILL.md`（规格文档组织）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
把代码变更反向同步到 `spec/` 设计文档，按 `mode` 走对应层级的回填。**只改 `spec/`，不改 CONTEXT.md，不改源码。**

执行步骤：

1. 解析参数：`mode=<immediate|daily|weekly>`（默认 daily）、可选 `path=<spec子路径>`
2. 无 `spec/` 结构 → 提示先用 `spec-organization` 建立，停止
3. 按 `mode` 执行（详见 `spec-backfill/references/three-layer.md`）：
   - `immediate`：针对刚生成的代码，同步核心流程 + 接口定义
   - `daily`：`git log --since="24 hours ago"`，按提交类型（feat/fix/refactor）判断文档影响并增改
   - `weekly`：读 `spec/` 全部建模型 → 扫本周变化 → README 全量重写 + 模块增量 → 跑自检清单
4. 写作遵循三段式（概述 → Mermaid → 功能与设计要点）与回填红线（`references/three-paragraph-style.md` + `redlines.md`）
5. Merge-Back：发现 `spec/AI2AI/` 等临时规格已验证 → 回填到 `spec/` 主文档
6. 跑回填自检清单（流程图可渲染/功能完整/术语一致/无实现细节/无过时信息/只改 spec）
7. 经 MR 流程提交（定时场景由 scheduled-automation 编排轮询 CI + auto-merge）；手动场景输出变更摘要待 Boss 确认

补充约束：
- 禁止改 CONTEXT.md（那是 /doc-sync）与任何源码文件
- 不复述代码、不罗列完整 API 字段、不留过时信息（红线）
- 报告须声明「本次仅修改 spec/ 文档，未改源码 / CONTEXT.md」

$ARGUMENTS
