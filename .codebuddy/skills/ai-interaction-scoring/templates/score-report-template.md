# AI 交互质量评分报告

## 被评人：{{name}}（工号：{{id}}）
## 需求名称：{{taskDescription}}
## 评分日期：{{scoringDate}}
## 对话来源：{{conversationSource}}

---

## 评分总览

| 评分维度 | 满分 | 得分 | 得分率 | 证据摘要 |
|----------|------|------|--------|----------|
| Spec-Coding 规范 | 10 | {{dim1Score}} | {{dim1Rate}} | {{dim1Summary}} |
| Skills/Agent 使用 | 5 | {{dim2Score}} | {{dim2Rate}} | {{dim2Summary}} |
| 项目完成度 | 10 | {{dim3Score}} | {{dim3Rate}} | {{dim3Summary}} |
| 扩展功能与美化 | 5 | {{dim4Score}} | {{dim4Rate}} | {{dim4Summary}} |
| **总分** | **30** | **{{totalScore}}** | **{{totalRate}}** | |

### 评分等级

| 等级 | 分数区间 | 说明 |
|------|----------|------|
| 优秀 | 25-30 | 流程合规、功能完整、界面精致 |
| 良好 | 19-24 | 基本合规、核心功能可用、存在小缺陷 |
| 合格 | 13-18 | 部分合规、部分功能可用、存在明显缺陷 |
| 待改进 | 0-12 | 流程、功能或两者均存在显著差距 |

**当前等级：{{scoreLevel}}**

---

## 详细分析

### 1. Spec-Coding 规范（{{dim1Score}}/10）

#### 评分明细

| 评估项 | 满分 | 得分 | 证据 |
|--------|------|------|------|
| 需求澄清 | 2 | {{specItem1}} | {{specEvidence1}} |
| 技术方向评估 | 2 | {{specItem2}} | {{specEvidence2}} |
| 正式规格文档 | 2 | {{specItem3}} | {{specEvidence3}} |
| 实施计划 | 2 | {{specItem4}} | {{specEvidence4}} |
| 持久化文档 | 1 | {{specItem5}} | {{specEvidence5}} |
| 质量门禁 | 1 | {{specItem6}} | {{specEvidence6}} |

#### 扣分原因
{{dim1Deductions}}

---

### 2. Skills/Agent 使用（{{dim2Score}}/5）

#### 使用的技能列表

| # | 技能/Agent | 使用场景 |
|---|-----------|----------|
{{skillsList}}

**去重后技能数量：{{skillsCount}}**

#### 扣分原因
{{dim2Deductions}}

---

### 3. 项目完成度（{{dim3Score}}/10）

#### 任务交付物评估

| # | 交付物 | 状态 | 证据级别 | 得分 |
|---|--------|------|----------|------|
{{deliverablesList}}

#### 补充证据
{{supplementaryEvidence}}

#### 负面证据（如有）
{{negativeEvidence}}

#### 扣分原因
{{dim3Deductions}}

---

### 4. 扩展功能与界面美化（{{dim4Score}}/5）

#### 扩展功能
{{extendedFeatures}}

#### 界面美化
{{uiBeautification}}

#### 扣分原因
{{dim4Deductions}}

---

## 反模式检测

| 反模式 | 是否检出 | 出现次数 | 影响说明 |
|--------|----------|----------|----------|
| 虚假完成 | {{ap1Detected}} | {{ap1Count}} | {{ap1Impact}} |
| 过早编码 | {{ap2Detected}} | {{ap2Count}} | {{ap2Impact}} |
| Bug 修复循环 | {{ap3Detected}} | {{ap3Count}} | {{ap3Impact}} |
| 忽略用户反馈 | {{ap4Detected}} | {{ap4Count}} | {{ap4Impact}} |

---

## 亮点总结

### 优势
{{strengths}}

### 不足
{{weaknesses}}

---

## 改进建议

{{recommendations}}

---

## 评分方法说明

本报告由 `ai-interaction-scoring` 技能（v1.0.0）生成。

- 评分基于对话证据（代理指标）
- 用户关于功能的陈述优先于代码分析
- 各维度独立评分
- 证据模糊时采用保守评分
- 反模式检测作为负面修正因子
