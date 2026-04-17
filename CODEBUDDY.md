# Featureflow 会话最小手册

面向每次会话启动的最小规则集。只保留必须立即生效的信息；详细说明统一放在 `README.md` 与 `docs/*`。

## 1) 三条铁律（最高优先级）

1. 称呼规则：每次回复第一句话必须称呼 `Boss`。
2. 决策确认：遇到不确定设计，先询问 `Boss`，不得擅自拍板。
3. 兼容性禁令：未经 `Boss` 明确要求，不得编写兼容性代码。

## 2) 会话启动必做

1. 识别版本控制：Git 或 SVN。
2. 默认加载核心规则（常驻）：
   - `.codebuddy/rules/verification-before-completion.md`
   - `.codebuddy/rules/file-based-memory.md`
   - `.codebuddy/rules/logging-conventions.md`
3. 重型规则按需加载（不在会话启动全量加载）：
   - `.codebuddy/rules/project-reading.md`：读项目/改代码前
   - `.codebuddy/rules/test-driven-development.md`：测试生成与实现阶段
   - `.codebuddy/rules/code-documentation.md`：`/doc-init`、`/doc-sync`、文档同步阶段
4. 复杂任务（>=3 步或 >5 次工具调用）强制启用 file-based-memory。
5. 检测 GitNexus MCP 可用性（可选但推荐）：
   - 尝试调用 GitNexus 工具，记录 `gitnexusAvailable` 状态
   - 可用时按需加载：`.codebuddy/rules/gitnexus-code-intelligence.md`
   - `npx gitnexus analyze` 若自动生成 `AGENT.md`、`CLAUDE.md`、`.claude/skills/*`，将其视为 GitNexus 参考提示层，不作为活跃技能注册目录
   - GitNexus 的探索/调试/影响分析/重构能力，统一映射回 `.codebuddy/*` 命令、规则与技能
   - 不可用时不报错，后续流程自动走手动路径

## 3) 默认入口与路由

优先单入口：

```text
/Featureflow <需求>
```

若明确知道任务类型，可直接走专用入口：

| 任务类型 | 默认入口 |
|---|---|
| new-feature | `/spec-lite` |
| bugfix | `/fix-bug` |
| refactor | `/write-plan` |
| test | `/test-gen` 或 `/unified-test` |
| research | `/research` |
| review-pr | `/code-review` |
| issue-draft-pr | `/issue-draft-pr` |
| parallel-delivery | `/parallel-delivery` |
| scoring | `/score-interaction` |

## 4) 主流程最小链路

### L/M 级

`/spec-lite -> /write-plan -> /execute-plan -> /test-gen|/unified-test -> /code-review -> /status`

### H 级 / 复杂任务

`/brainstorm -> /spec-lite -> /write-plan -> /execute-plan -> /requirement-coverage -> /test-gen|/unified-test -> /code-review -> /status`

或（需求已清晰，但 `/spec-lite` 判定为 H）：

`/spec-lite -> /brainstorm -> /write-plan -> /execute-plan -> /requirement-coverage -> /test-gen|/unified-test -> /code-review -> /status`

### `/extend` 已有项目扩展（强制四步前置）

`项目理解(三层→GitNexus→手动) -> historical-spec(Boss核实) -> /brainstorm -> requirement-analysis(Boss核实) -> /spec-lite -> /write-plan -> /execute-plan -> /requirement-coverage -> /unified-test -> /code-review -> /status`

门禁未通过时，必须 `BLOCKED` 并回退到正确上游步骤，不得硬推进。

### 项目分析 / 代码解释（信息源优先级铁律）

任何"分析项目 / 解释代码"请求统一按下列顺序选源，禁止跳级；详见 `.codebuddy/rules/project-reading.md`：

`三层代码自文档(CONTEXT.md + 头部 INPUT/OUTPUT/POS) -> GitNexus(先做模式 G 基线对比/刷新) -> 手动阅读四步法`

## 5) 持久化记录（强制）

- `docs/progress.md`：每个阶段、每次错误后更新。
- `docs/findings.md`：每 2 次搜索/读取后更新；出现新结论/决策时立即更新。
- `/extend` 特殊要求：
  - 每次执行结束（`BLOCKED`/门禁阻断/分流通过）都必须更新 `docs/progress.md`。
  - 若形成新的分流判断、风险结论或阻断经验，必须同步更新 `docs/findings.md`。

## 6) 回滚安全默认策略

- 默认仅允许“回滚准备 + dry-run 演练”。
- 真实回滚不是默认动作，必须 `Boss` 显式确认后才可执行。
- 真实回滚前必须记录快照点（commit/tag/备份点）与恢复命令。

## 7) 交付完成标准（最小）

1. 有可复现证据：命令、输出、退出码。
2. 质量门禁通过：`check-gates` + `check-quality`（按场景）。
3. 文档与代码同步：必要时执行 `/doc-sync`。
4. 收尾声明：剩余风险、owner、handoff 建议。
5. 审查阶段默认只读：`/code-review` 先报问题与建议，未经 `Boss` 确认不直接改代码。

## 8) 常用命令速查

- `/Featureflow`：单入口总控
- `/spec-lite`：规格与分级
- `/write-plan`：计划编排
- `/execute-plan`：批次执行
- `/extend`：已有项目功能扩展（强制 historical-spec → brainstorm → requirement-analysis 四步前置）
- `/fix-bug`：缺陷修复
- `/test-gen` `/unified-test`：测试
- `/requirement-coverage`：系统测试前的需求覆盖独立审查（H 级 / 复杂任务必跑）
- `/code-review`：审查
- `/status`：查看进度
- `/doc-sync`：文档同步
- `/pua`：激活防摆烂引擎（可带参数描述卡壳任务）
- `/score-interaction`：AI 交互质量评分

## 9) 详细文档位置（按需加载）

- 总说明：`README.md`
- 工作流：`docs/workflows/*`
- 流程实操：`docs/playbooks/workflow-playbook.md`
- 门禁矩阵：`.codebuddy/skills/process-gatekeeper/gate-matrix.md`
- 路由规则：`.codebuddy/skills/devflow-router/SKILL.md`
