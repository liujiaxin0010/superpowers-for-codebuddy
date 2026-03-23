---
name: xlsx
description: 当电子表格文件（.xlsx/.xlsm/.csv/.tsv）是主要输入或交付物时使用本技能。适用于创建新工作簿、编辑现有模板、批量生成报表、清洗表格数据、修复公式或在电子表格格式之间转换。用户直接提到文件名、路径，或要求“生成/修改/修复 xlsx 表格”时触发；如果主要交付物是 Word、HTML、独立脚本、数据库管道或 Google Sheets API 集成，即使中间涉及表格数据也不要触发。
---

# XLSX 创建、编辑与修复

本技能回答的是：**这次应该用什么工具处理电子表格，什么场景必须保留模板，什么时候必须跑公式质量门禁。**

## 资源加载规则

当还没确定任务该走“数据清洗 / 现有模板编辑 / 公式修复 / OOXML 低层处理”哪条路时，再读取：

- `references/task-routing-matrix.md`

当交付物是金融模型、管理报表或对格式有明确要求的工作簿时，再读取：

- `references/financial-modeling-standards.md`

当需要新增、修改或修复公式，或工作簿必须保持动态更新时，必须读取：

- `references/formula-quality-workflow.md`

当需要在 `pandas`、`openpyxl` 和低层 OOXML 脚本之间做工具选择时，再读取：

- `references/python-automation-guide.md`

当 Windows 路径包含空格或脚本执行报引用路径错误时，再读取：

- `references/windows-paths.md`

当需要向用户或 owner 汇报最终工作簿交付信息时，再读取：

- `templates/spreadsheet-delivery-template.md`

如果只是做简单的 CSV/XLSX 数据清洗，不要加载金融模型标准。

## 何时使用

1. 用户要创建、编辑、修复或转换 `.xlsx/.xlsm/.csv/.tsv`
2. 主要交付物本身就是电子表格文件
3. 需要保留工作表、格式、公式、图表或模板约定

## 何时不用

1. 主要交付物不是电子表格，而是 Word、HTML、数据库管道或独立脚本
2. 只是借助表格数据做中间分析，但最终不交付工作簿
3. 主要需求是 Google Sheets API 或在线表格集成

## 阻断条件

出现以下任一情况时，返回 `BLOCKED`：

1. 目标文件或模板路径不存在
2. 用户要求的是非电子表格交付物
3. 需要保留现有模板，但模板本身未提供
4. 公式工作簿在交付前仍有未修复的公式错误

## 决策协议

1. 先判断任务类型：数据分析/清洗、创建新工作簿、编辑现有工作簿、低层修复
2. 再选工具：
   - `pandas` 适合批量读写和表格清洗，格式不是主诉求时优先
   - `openpyxl` 适合保留工作簿结构、样式和公式
   - `scripts/office/unpack.py` + `pack.py` 只用于 OOXML 级手术或 openpyxl 无法安全保留结构的场景
3. 若修改现有模板，优先匹配原有格式，不要顺手做风格统一
4. 若工作簿需要保持动态，优先写 Excel 公式，不要把 Python 计算结果硬编码进去
5. 任何新增或修改公式的工作簿，交付前都必须运行 `python .codebuddy/skills/xlsx/scripts/recalc.py <excel_file> [timeout_seconds]`
6. 若 `recalc.py` 返回 `errors_found`，先修复再交付
7. 如果只是普通 CSV/XLSX 清洗，不要额外加载金融标准或 OOXML 级工具

## 质量门禁

1. 模板样式和现有约定没有被无意破坏
2. 公式工作簿没有 `#REF!`、`#DIV/0!`、`#VALUE!`、`#N/A`、`#NAME?`
3. 需要动态更新的单元格没有被硬编码值替代
4. 没有在 `data_only=True` 打开的工作簿上直接保存，导致公式丢失
5. 硬编码假设值有来源说明

## 工具边界

1. `recalc.py` 是 xlsx 的主要质量门禁
2. `office/validate.py` 当前不提供 xlsx 专用校验，不要把它当成 xlsx 门禁
3. `pack.py` 虽然支持 `.xlsx` 打包，但对 xlsx 不提供专用 validator；它主要用于低层重打包

## 输出要求

1. 说明输出文件路径
2. 说明修改了哪些工作表
3. 说明是否新增或修改公式
4. 若跑了 `recalc.py`，给出命令和结果
5. 说明模板约定、假设来源和剩余风险

## 禁止事项

1. 不要在 Python 里算好结果后直接硬编码进本应动态更新的工作簿——用户下次更新数据时公式不会自动重算
2. 不要在 `data_only=True` 模式下保存公式工作簿——这会永久丢失所有公式，只保留最后一次缓存值
3. 不要修改现有模板时顺手重做格式体系——模板的格式约定可能对接下游系统或打印布局
4. 不要把 `office/validate.py` 误说成 xlsx 校验器——它只做 OOXML 结构校验，不检查公式和数据
5. 不要在 Windows 带空格路径里使用脆弱的 `cmd.exe` 嵌套引号——用 Python `subprocess` 的 list 形式传参
6. 不要用 `pandas` 读取后再写回需要保留格式的工作簿——pandas 会丢失样式、合并单元格和图表

## recalc.py 不可用时的备选方案

若 `recalc.py` 不可用或执行失败：

1. 用 `openpyxl` 逐单元格检查是否存在 `#REF!`、`#DIV/0!` 等错误值
2. 手动验证关键公式的引用范围是否覆盖新增数据行
3. 在输出中明确标注"未经自动公式校验，需人工确认"
