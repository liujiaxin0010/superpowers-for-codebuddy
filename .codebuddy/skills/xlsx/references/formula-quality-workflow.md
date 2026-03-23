# 公式质量工作流

本文件只在创建、修改或修复公式时读取。若只是做纯数据提取或无公式导出，不需要加载本文件。

## 核心原则

1. 工作簿需要保持动态时，优先写 Excel 公式，而不是把 Python 计算结果硬编码进去
2. 假设值单独放单元格，公式引用单元格，不直接埋魔法数字
3. 任何新增或修改公式的工作簿，交付前都必须跑 `scripts/recalc.py`

## 强制流程

1. 修改公式或新增公式
2. 保存工作簿
3. 运行：`python .codebuddy/skills/xlsx/scripts/recalc.py <excel_file> [timeout_seconds]`
4. 读取 JSON 输出
5. 若 `status=errors_found`，修到没有公式错误为止

## `recalc.py` 输出怎么用

重点字段：

1. `status`: `success` 或 `errors_found`
2. `total_errors`: 错误总数
3. `error_summary`: 每类错误和具体位置
4. `total_formulas`: 公式总数

常见错误：

1. `#REF!`：引用失效
2. `#DIV/0!`：分母为零
3. `#VALUE!`：类型不匹配
4. `#NAME?`：函数名或名称错误

## 常见坑

1. 不要把 `load_workbook(..., data_only=True)` 打开的工作簿再保存，否则公式会被值覆盖
2. 不要在 Python 里先算好结果再写死到单元格，除非工作簿本来就不要求动态更新
3. 不要改完公式就直接交付，必须跑重算
4. 不要把 `office/validate.py` 当成 xlsx 质量门禁；当前校验器只覆盖 docx/pptx，不覆盖 xlsx

## 交付前快速检查

1. 关键单元格抽样验证 2-3 处
2. 检查跨工作表引用是否指向预期位置
3. 检查零值、负值、空值边界
4. 检查有没有意外循环引用
