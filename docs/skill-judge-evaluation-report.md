# Skill Judge 评估报告 — superpowers-for-codebuddy

**评估日期**: 2026-03-23
**评估范围**: `.codebuddy/skills/` 下全部 33 个 SKILL.md
**评估标准**: skill-judge 8 维度 120 分制

---

## 总览

| # | Skill | 行数 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | 总分 | 等级 |
|---|-------|------|----|----|----|----|----|----|----|----|------|------|
| 1 | ai-interaction-scoring | 270 | 16 | 12 | 12 | 13 | 13 | 12 | 8 | 13 | **99** | **B** |
| 2 | brainstorming | 116 | 13 | 13 | 10 | 12 | 12 | 13 | 8 | 12 | **93** | **C** |
| 3 | bug-fix | 201 | 15 | 13 | 13 | 10 | 8 | 12 | 8 | 14 | **93** | **C** |
| 4 | code-review-standards | 289 | 12 | 10 | 9 | 13 | 13 | 11 | 8 | 12 | **88** | **C** |
| 5 | code-self-check | 122 | 14 | 12 | 11 | 12 | 11 | 13 | 7 | 12 | **92** | **C** |
| 6 | code-simplifier | 107 | 15 | 13 | 13 | 13 | 12 | 14 | 8 | 13 | **101** | **B** |
| 7 | custom-testing | 148 | 14 | 12 | 10 | 12 | 12 | 12 | 7 | 12 | **91** | **C** |
| 8 | devflow-router | 82 | 14 | 12 | 12 | 10 | 12 | 12 | 8 | 11 | **91** | **C** |
| 9 | dispatching-parallel-agents | 88 | 15 | 13 | 13 | 12 | 12 | 13 | 8 | 13 | **99** | **B** |
| 10 | executing-plans | 150 | 14 | 13 | 12 | 12 | 12 | 13 | 8 | 13 | **97** | **B** |
| 11 | extending-project | 113 | 14 | 13 | 12 | 12 | 12 | 13 | 7 | 12 | **95** | **C** |
| 12 | file-based-memory | 161 | 16 | 14 | 11 | 13 | 12 | 12 | 8 | 13 | **99** | **B** |
| 13 | finishing-branch | 158 | 14 | 12 | 13 | 13 | 12 | 13 | 8 | 13 | **98** | **B** |
| 14 | issue-draft-pr | 75 | 13 | 11 | 10 | 10 | 8 | 12 | 7 | 11 | **82** | **D** |
| 15 | parallel-delivery | 83 | 14 | 12 | 11 | 10 | 9 | 13 | 7 | 12 | **88** | **C** |
| 16 | postgres-best-practices | 105 | 16 | 13 | 13 | 13 | 12 | 12 | 8 | 12 | **99** | **B** |
| 17 | process-gatekeeper | 72 | 14 | 11 | 10 | 12 | 12 | 13 | 8 | 11 | **91** | **C** |
| 18 | pua | 112 | 17 | 14 | 12 | 13 | 12 | 12 | 8 | 12 | **100** | **B** |
| 19 | receiving-code-review | 98 | 15 | 13 | 13 | 12 | 11 | 13 | 7 | 12 | **96** | **B** |
| 20 | requesting-code-review | 86 | 13 | 12 | 10 | 12 | 11 | 13 | 7 | 12 | **90** | **C** |
| 21 | research | 129 | 14 | 14 | 10 | 12 | 8 | 13 | 8 | 12 | **91** | **C** |
| 22 | spec-lite | 201 | 14 | 13 | 10 | 10 | 8 | 12 | 8 | 13 | **88** | **C** |
| 23 | subagent-driven-development | 140 | 16 | 13 | 11 | 13 | 13 | 13 | 8 | 13 | **100** | **B** |
| 24 | systematic-debugging | 68 | 15 | 14 | 13 | 13 | 13 | 12 | 8 | 12 | **100** | **B** |
| 25 | task-contracts | 89 | 16 | 12 | 12 | 10 | 9 | 13 | 7 | 13 | **92** | **C** |
| 26 | testcase | 133 | 13 | 12 | 10 | 12 | 9 | 12 | 7 | 12 | **87** | **C** |
| 27 | unified-test | 222 | 13 | 10 | 8 | 13 | 14 | 12 | 8 | 12 | **90** | **C** |
| 28 | using-git-worktrees | 117 | 14 | 12 | 10 | 13 | 12 | 13 | 7 | 12 | **93** | **C** |
| 29 | version-control-branching | 82 | 12 | 11 | 10 | 13 | 12 | 12 | 7 | 11 | **88** | **C** |
| 30 | web-code-review | 186 | 13 | 11 | 12 | 13 | 12 | 12 | 8 | 13 | **94** | **C** |
| 31 | writing-plans | 160 | 14 | 13 | 12 | 12 | 8 | 13 | 8 | 13 | **93** | **C** |
| 32 | writing-skills | 112 | 16 | 14 | 12 | 12 | 12 | 13 | 8 | 12 | **99** | **B** |
| 33 | xlsx | 109 | 17 | 13 | 14 | 14 | 13 | 14 | 9 | 14 | **108** | **A** |

### 等级分布

| 等级 | 数量 | 技能 |
|------|------|------|
| **A (108+)** | 1 | xlsx |
| **B (96-107)** | 12 | ai-interaction-scoring, code-simplifier, dispatching-parallel-agents, executing-plans, file-based-memory, finishing-branch, postgres-best-practices, pua, receiving-code-review, subagent-driven-development, systematic-debugging, writing-skills |
| **C (84-95)** | 19 | brainstorming, bug-fix, code-review-standards, code-self-check, custom-testing, devflow-router, extending-project, parallel-delivery, process-gatekeeper, requesting-code-review, research, spec-lite, task-contracts, testcase, unified-test, using-git-worktrees, version-control-branching, web-code-review, writing-plans |
| **D (72-83)** | 1 | issue-draft-pr |
| **F (<72)** | 0 | — |

**整体均分**: 93.8/120 (78.2%) — **C+ 水平**

---

## 维度得分分析

### 各维度平均分

| 维度 | 平均分 | 满分 | 得分率 | 诊断 |
|------|--------|------|--------|------|
| D1: 知识增量 | 14.2 | 20 | 71% | 中等偏上，多数skill有真实专家知识 |
| D2: 思维模式+程序 | 12.4 | 15 | 83% | 较好，决策协议普遍到位 |
| D3: 反模式质量 | 11.3 | 15 | 75% | 有改进空间，部分理由不够深 |
| D4: 规范合规 | 12.1 | 15 | 81% | 较好，少数description偏弱 |
| D5: 渐进披露 | 11.2 | 15 | 75% | 中等，部分skill无reference却全塞主文件 |
| D6: 自由度校准 | 12.5 | 15 | 83% | 较好，普遍匹配任务脆弱性 |
| D7: 模式识别 | 7.7 | 10 | 77% | 中等，模式使用一致但少有精湛 |
| D8: 实用性 | 12.3 | 15 | 82% | 较好，决策树和边界清晰 |

**最强维度**: D2 (思维模式) 和 D6 (自由度校准) — 体现了技能设计者对"协议式"而非"教程式"的良好理解。

**最弱维度**: D1 (知识增量) 和 D5 (渐进披露) — 部分技能仍混入了 LLM 已知的通用知识；部分技能缺少对reference的按需加载设计。

---

## 顶级技能分析

### xlsx (108/120 — A)

**为什么得分最高**:
- **D1=17**: 公式质量门禁、`data_only=True` 陷阱、`recalc.py` 流程、OOXML 低层处理 vs openpyxl 的决策树——这些都是纯专家知识
- **D3=14**: 反模式极具体且有不明显的原因（"pandas 会丢失样式和合并单元格"）
- **D5=13**: 资源加载规则清晰，按任务类型分路加载，有"不要加载"指导
- **D7=9**: 近乎完美的 Tool 模式应用

### systematic-debugging (100/120 — B)

- 四阶段协议是真正的专家思维框架
- "3次失败必须架构反思" 是高价值知识增量
- 68行极度精炼，无冗余

### pua (100/120 — B)

- 失败模式分类 + 压力等级升级 = 独特的知识体系
- 7 项强制检查清单是真正的防摆烂工具
- "风味选择器" 是创造性设计

---

## 关键问题与优化方案

### 问题 1: description 质量参差不齐（影响 7 个 skill）

**受影响技能**: devflow-router, issue-draft-pr, parallel-delivery, spec-lite, task-contracts, version-control-branching, testcase

**症状**: description 缺少明确的 WHEN 触发场景或 KEYWORDS，导致 Agent 可能无法正确激活。

**典型案例**:
```yaml
# devflow-router — 缺少触发关键词
description: Featureflow 总控路由技能。用于把任意开发请求统一收口到一个入口...
# 问题：没有明确 "用户提到 XXX 时触发"
```

```yaml
# task-contracts — 缺少 WHEN
description: 统一任务合同技能。用于根据任务类型选择合同模板...
# 问题：没有说明用户什么场景会触发
```

**优化方案**:
每个 description 必须包含三要素：
1. **WHAT**: 做什么（已有）
2. **WHEN**: 什么场景触发（补充 "用户提到 XXX 时触发"）
3. **KEYWORDS**: 触发关键词（补充具体的用户话术）

**具体修改建议**:

```yaml
# devflow-router 改进
description: >
  Featureflow 总控路由技能。用于把任意开发请求统一收口到一个入口，
  自动识别文档产物意图、任务类型、判断前置条件，并路由到对应工作流。
  用户提到"Featureflow/统一入口/自动路由/我该用什么命令/帮我判断该走哪个流程"时触发。

# task-contracts 改进
description: >
  统一任务合同技能。用于根据任务类型选择合同模板，补齐目标、边界、验证、
  证据、owner 与超边界处理，并将模板压缩成 agent 可执行合同摘要。
  用户提到"生成合同/task contract/任务边界/补齐合同字段/合同模板"时触发。

# issue-draft-pr 改进
description: >
  以 issue 或 Jira 工单为起点，生成可审查的 draft PR 交付链路。
  适用于目标相对清晰、验收可定义、需要异步交接和 owner 收口的任务。
  用户提到"issue 转 PR/工单到 PR/draft PR/从 issue 开始开发"时触发。
```

---

### 问题 2: 部分 skill 的渐进披露设计缺失（影响 5 个 skill）

**受影响技能**: bug-fix, research, spec-lite, writing-plans, issue-draft-pr

**症状**: 主文件内容超过 100 行但没有 references/ 目录，所有内容堆在 SKILL.md 中。或者虽有 references 但加载触发不够明确。

**典型案例**:
- `bug-fix` (201行): 上下文分层读取策略、修改点识别、输出格式等都在主文件，没有下沉
- `spec-lite` (201行): 评分规则、GateContext 字段、TaskContract 字段全在主文件
- `writing-plans` (160行): 拆解启发式、依赖规则等应下沉

**优化方案**:

| Skill | 下沉内容 | 目标文件 |
|-------|----------|----------|
| bug-fix | 上下文分层读取策略详情、修改方案输出格式模板 | `references/context-reading-guide.md`, `templates/fix-report-template.md` |
| spec-lite | GateContext/TaskContract/GateResult 字段定义 | `references/gate-field-definitions.md` |
| writing-plans | 拆解启发式详情、依赖并行规则详情 | `references/decomposition-heuristics.md` |
| research | 输出报告模板 | `templates/research-report-template.md` |

每处下沉后，在主文件中保留加载触发：
```markdown
### 需要细化修改方案输出格式时
必须读取：
- `templates/fix-report-template.md`
```

---

### 问题 3: 反模式理由深度不足（影响 8 个 skill）

**受影响技能**: brainstorming, custom-testing, requesting-code-review, testcase, parallel-delivery, using-git-worktrees, version-control-branching, unified-test

**症状**: 有"禁止事项"但部分条目缺少 WHY（为什么这是个坏主意）。

**对比**:
```markdown
# 弱反模式（unified-test）
1. 不要在不支持的文件类型上硬走统一测试流程

# 强反模式（xlsx）
1. 不要在 Python 里算好结果后直接硬编码进本应动态更新的工作簿
   ——用户下次更新数据时公式不会自动重算
```

**优化方案**: 为每条禁止事项补充"——因为 XXX"后缀，说明不遵守的后果。这是专家知识的核心体现。

---

### 问题 4: code-review-standards 存在冗余知识（D1=12）

**问题**: 五大维度（正确性、性能、安全、代码质量、最佳实践）中的检查项大部分是 LLM 已知的通用知识。例如"边界条件处理（null、空值、越界）"、"SQL 注入、XSS"等，LLM 不需要提醒也会检查。

**优化方案**:
1. 将五大维度的通用检查项精简为一行引用："按 references/ 中对应语言审查清单逐条检查"
2. 主文件只保留**决策协议**（何时审查、审什么深度、如何与 web-code-review 协同）
3. 将具体检查维度细节下沉到 references/

预计可将主文件从 289 行压缩到 ~120 行，同时提高 D1 和 D5 得分。

---

### 问题 5: issue-draft-pr 内容过于骨架化（D 级，82分）

**问题**: 75 行中有效专家知识密度不够。工单质量快速判断表和 Draft PR 最小质量标准是有价值的，但缺少：
1. 资源加载规则（只在末尾提了一个 reference）
2. 思维模式框架
3. 更深入的决策协议

**优化方案**:
1. 添加标准的资源加载规则节
2. 补充"工单质量判断 → 合同生成 → 实现 → 审查 → PR" 的决策协议
3. 补充 Draft PR 常见反模式（如"PR 描述复制粘贴 issue 原文但不映射验收标准"）

---

### 问题 6: 跨 skill 一致性问题

**观察**: 33 个 skill 的结构高度一致（何时使用/何时不用/阻断条件/资源加载规则/禁止事项），这本身是优点。但有几处不一致：

| 不一致项 | 涉及 skill | 建议 |
|----------|-----------|------|
| "何时使用"放在 body 而非 description | devflow-router, task-contracts | 将核心触发场景移入 description |
| 有的用"禁止事项"、有的用"禁止行为" | bug-fix vs 其他 | 统一为"禁止事项" |
| 有的在 description 中用引号包裹、有的不用 | 混合 | 统一格式 |

---

## Top 10 优先优化清单

按影响力排序：

| 优先级 | 优化项 | 影响 skill 数 | 预期收益 |
|--------|--------|---------------|----------|
| **P0** | 补齐 7 个 skill 的 description 触发关键词 | 7 | 直接决定 skill 能否被正确激活 |
| **P1** | bug-fix/spec-lite/writing-plans 内容下沉 | 3 | 减少 300+ 行主文件负担 |
| **P1** | 为所有禁止事项补充 WHY 后缀 | 8 | 提升反模式质量维度 |
| **P2** | code-review-standards 精简通用知识 | 1 | 从 289 行压缩到 ~120 行 |
| **P2** | issue-draft-pr 补充资源加载和决策协议 | 1 | 从 D 级提升到 C 级 |
| **P2** | unified-test 反模式补充 WHY | 1 | 提升 D3 从 8 到 11+ |
| **P3** | 统一禁止事项措辞 | 全部 | 一致性改善 |
| **P3** | research 输出模板下沉到 templates/ | 1 | 主文件减少 ~30 行 |
| **P3** | version-control-branching 增加知识增量 | 1 | D1 从 12 提升 |
| **P3** | parallel-delivery 补充资源加载触发 | 1 | D5 从 9 提升到 12 |

---

## 整体评价

### 优势

1. **结构一致性极高**: 33 个 skill 统一遵循"何时使用/阻断条件/资源加载/决策协议/禁止事项"结构，形成了清晰的项目内规范
2. **协议式而非教程式**: 绝大多数 skill 采用"先判断、再决策、再执行"的协议模式，而非机械的 step-by-step 教程
3. **资源加载规则普遍到位**: 几乎所有 skill 都有"何时加载/不要怎么加载"的明确指导
4. **禁止事项覆盖全面**: 每个 skill 都有具体的 NEVER 清单
5. **技能间协同设计**: skill 之间的边界划分（如 requesting-code-review vs code-review-standards vs web-code-review）体现了系统性思考

### 可改进方向

1. **知识增量**: 部分 skill 仍混入了 LLM 已知的通用编程知识，可进一步精炼
2. **渐进披露**: 3-5 个 100+ 行的 skill 可以通过内容下沉进一步优化
3. **反模式深度**: 补充 WHY 可以显著提升专家知识密度
4. **description 质量**: 约 20% 的 skill description 缺少触发关键词

### 与官方 skill 的对比

以 xlsx 为标杆（接近官方 docx/pdf 的 Tool 模式水平），该项目的 skill 整体质量：
- **结构设计**: 超过多数开源 skill（统一规范是巨大优势）
- **知识密度**: 接近官方水平，少数 skill 需要去冗余
- **渐进披露**: 略低于官方最佳实践（官方 docx skill 的 MANDATORY READ 触发更严格）
- **实用性**: 与官方持平，决策协议和边界定义清晰

---

*本报告由 skill-judge 评估框架生成*
