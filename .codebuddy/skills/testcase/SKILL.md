---
description: 测试用例产出阶段技能，基于设计与架构文档生成 testcase 与覆盖分析文档。
---

# 测试用例

根据 `spec/AI2AI` 文档生成测试用例与覆盖分析，不直接执行业务实现。

## 输入

1. `spec/AI2AI/Design.md`
2. `spec/AI2AI/Architecture_Info.md`
3. `spec/AI2AI/Protocol_and_Data.md`
4. 可选：`spec/AI2AI/test.md`

## 执行要求

1. 覆盖功能、异常、边界、组合场景
2. 对高风险路径单独标注用例
3. 输出可追踪统计信息（总数、覆盖率目标、缺口）
4. 产出的 Markdown 文档内容默认使用中文（代码、命令、路径、字段名可保留英文）

## 输出

1. `spec/AI2AI/testcase.md`
2. `spec/AI2AI/testcase_analysis.md`
