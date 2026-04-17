# Bugfix Task Contract

任务类型：`bugfix`

问题描述：

复现步骤：

期望行为：

实际行为：

根因假设/待验证点：

允许修改范围：

禁止修改：

验证命令：

**failingRegressionTestPath**（必填，M/H 级强制）：

**failingRegressionTestCommand**（必填，M/H 级强制）：

**failingRegressionTestEvidence**（必填，修复前首次失败的完整输出片段或日志路径）：

交付物：根因说明、最小修复、回归结果、剩余风险

交付证据：最小复现关闭证据、**修复前失败测试 → 修复后通过测试**的前后对比、回归输出、diff 说明

人工确认点：

owner：

超边界时如何处理：超出最小修复边界时先停止，回退到合同确认，不顺手做结构重写。
