---
name: web-code-review
description: >
  Web 前端代码审查技能。对 Vue/JS/TS 代码进行系统化缺陷检测，
  覆盖代码逻辑、视觉呈现、交互体验、性能表现、内容准确性 5 大缺陷类别。
  输出结构化的缺陷报告（JSON 格式），每条缺陷包含位置、严重程度、分类、修复建议。
  当用户提到"代码审查"、"code review"、"帮我看看代码"、"检查代码质量"、
  "有没有 bug"、"代码有什么问题"时触发此技能。
  即使用户只上传了一个 .vue/.js/.ts 文件并说"帮我看看"，也应触发。
---

# Web Code Review — Web 前端代码审查技能

## Overview

对 Vue / JavaScript / TypeScript 前端代码进行系统化的缺陷检测与质量评审。
审查覆盖 5 大缺陷类别、3 级严重程度，输出结构化的 JSON 缺陷报告。

本技能源自 Code Analysis Guide for Web Code Review 方法论，
专为 Vue 2.x / Vue 3.x 组件及其相关 JS/TS 代码设计。

## 输入

```typescript
interface ReviewInput {
  targetFile: string;            // 被审查文件路径（.vue / .js / .ts）
  context?: {
    relatedFiles?: string[];     // 相关文件（被导入的组件、工具函数等）
    projectType?: string;        // 项目类型（如 "Vue 2 + Element UI"）
    focusAreas?: string[];       // 重点关注领域（如 ["性能", "安全"]）
  };
  options?: {
    severity?: string;           // 最低报告级别: "Major" | "General" | "Suggest"（默认 "General"）
    maxDefects?: number;         // 最大报告缺陷数（默认不限制）
    outputFormat?: string;       // "json" | "markdown"（默认 "json"）
  };
}
```

## 审查流程

### Step 1: 读取并理解代码

```
1. 读取目标文件完整内容
2. 如果是 .vue 文件，分别分析 <template>、<script>、<style> 三个部分
3. 如果提供了 relatedFiles，一并读取以理解上下文
4. 识别技术栈（Vue 2/3、Options API/Composition API、UI 框架等）
```

### Step 2: 按 5 大类别逐一扫描

按以下顺序对代码进行系统化扫描（详细检查项见 `references/review-checklist.md`）：

| 类别 | 英文 | 审查重点 |
|------|------|---------|
| ① 代码逻辑类 | Code Logic | 函数逻辑、条件判断、返回值、参数校验、算法 |
| ② 视觉呈现类 | Visual Presentation | CSS/样式、布局、响应式、主题一致性 |
| ③ 交互体验类 | User Interaction | 事件处理、用户反馈、表单验证、加载状态 |
| ④ 性能表现类 | Performance | 内存泄漏、渲染性能、不必要的重渲染、算法效率 |
| ⑤ 内容准确性类 | Content Accuracy | 文案错误、拼写、日期格式、国际化、数据展示 |

**每个类别的审查必须独立完成**，避免遗漏。

### Step 3: 评估严重程度

对每个发现的缺陷，评估严重程度：

| 级别 | 标准 | 是否必须报告 |
|------|------|-------------|
| **Major**（严重） | 安全漏洞、数据丢失风险、核心功能崩溃、阻断性 bug | 必须报告 |
| **General**（一般） | 代码质量问题、小性能问题、不一致模式、可能导致 bug | 当 severity 设置 ≤ General 时报告 |
| **Suggest**（建议） | 最佳实践、代码风格、微优化、可读性改进 | 当 severity 设置 = Suggest 时报告 |

### Step 4: 缺陷分类定位

对每个缺陷，从缺陷分类表中匹配 `source → type → subtype`
（详见 `references/defect-classification.md`）：

```
source:   缺陷引入阶段（需求分析 / 概要设计 / 详细设计 / 编码）
type:     缺陷类型（函数模块接口 / 条件分支循环 / 资源类 / ...）
subtype:  缺陷子类型（函数功能不单一 / 返回值处理 / 参数校验 / ...）
category: 缺陷大类（5 类之一）
```

### Step 5: 生成修复建议

对每个缺陷提供**具体、可执行的修复建议**：

- 不要只说"建议优化"，要说**怎么优化**
- 如果可能，提供修复后的代码示例
- 多个修复方案时，推荐最佳方案并说明理由

### Step 6: 输出缺陷报告

#### JSON 格式（默认）

```json
{
  "reviewSummary": {
    "targetFile": "src/components/xxx/Component.vue",
    "reviewDate": "2026-03-02",
    "totalDefects": 5,
    "bySeverity": { "Major": 1, "General": 3, "Suggest": 1 },
    "byCategory": {
      "代码逻辑类": 2,
      "视觉呈现类缺陷": 0,
      "交互体验类缺陷": 1,
      "性能表现类缺陷": 1,
      "内容准确性类缺陷": 1
    }
  },
  "defects": [
    {
      "id": 1,
      "reviewer": "AI",
      "description": "handleSubmit 方法中对 formData.name 未做空值校验，当 name 为空字符串时会发送无效请求。修改建议：在提交前增加 if (!this.formData.name?.trim()) { this.$message.warning('名称不能为空'); return; } 校验。",
      "location": "Component.vue:85",
      "module": "src/components/xxx/Component.vue",
      "severity": "Major",
      "source": "编码",
      "type": "函数、模块接口_编码",
      "subtype": "形参和实参类型匹配、参数说明及校验",
      "category": "代码逻辑类",
      "suggestedFix": "if (!this.formData.name?.trim()) {\n  this.$message.warning('名称不能为空');\n  return;\n}"
    }
  ]
}
```

#### Markdown 格式（当 outputFormat = "markdown"）

```markdown
# 代码审查报告

**文件**: src/components/xxx/Component.vue
**日期**: 2026-03-02
**缺陷总数**: 5（Major: 1, General: 3, Suggest: 1）

## 🔴 Major 缺陷

### #1 缺少参数校验 (Component.vue:85)
**分类**: 代码逻辑类 > 编码 > 函数模块接口 > 参数校验
**描述**: handleSubmit 方法中...
**建议修复**:
（代码示例）

## 🟡 General 缺陷
...
```

## 审查原则

| # | 原则 | 说明 |
|---|------|------|
| 1 | **确定性优先** | 只报告确定的问题，不确定的用 "Suggest" 级别标注 |
| 2 | **可执行建议** | 每条缺陷都附带具体修复方案，而非笼统建议 |
| 3 | **上下文感知** | 理解代码意图后再判断，避免误报 |
| 4 | **严重性准确** | 不夸大问题严重性，不把 Suggest 标为 Major |
| 5 | **不重复报告** | 同一模式的问题只报告一次，备注"同类问题还出现在…" |
| 6 | **安全优先** | XSS、SQL 注入、敏感信息泄露等安全问题始终标为 Major |

## 技能文件索引

| 文件 | 说明 | 何时加载 |
|------|------|---------|
| `SKILL.md`（本文件） | 审查流程 + 输出格式 | 技能触发时 |
| `references/defect-classification.md` | 完整缺陷分类表（source/type/subtype） | Step 4 分类定位时 |
| `references/review-checklist.md` | 5 大类别的详细检查项清单 | Step 2 逐类扫描时 |
| `templates/defect-report-template.json` | 报告 JSON 模板 | Step 6 输出时 |
