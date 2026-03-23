# Python 自动化工作流

本文件只在需要决定用 pandas、openpyxl 还是低层 OOXML 脚本时读取。

## 工具选择

1. `pandas`：适合表格数据分析、清洗、批量导入导出，格式和公式不是主诉求时优先
2. `openpyxl`：适合创建或编辑现有工作簿，尤其是要保留格式、公式和工作表结构
3. `scripts/office/unpack.py` + `pack.py`：只在需要做 OOXML 级手术、openpyxl 无法安全保留结构时使用

## 使用 `openpyxl` 的提醒

1. 公式会被保留，但不会自动计算
2. 读取值时可用 `data_only=True`，但不要在这种模式下保存
3. 大文件读取可考虑 `read_only=True`
4. 大量写入可考虑 `write_only=True`

## 常见工作流

### 创建新工作簿

1. 用 `openpyxl` 建工作簿和工作表
2. 写入表头、数据、公式和格式
3. 如果有公式，跑 `recalc.py`

### 编辑现有工作簿

1. 先理解现有模板的样式和公式布局
2. 用 `openpyxl` 修改指定单元格、插入行列或新增工作表
3. 如果改了公式，跑 `recalc.py`

### 低层 OOXML 处理

只在以下场景使用：

1. 需要直接解包和重打包 `.xlsx`
2. openpyxl 处理后会破坏现有结构
3. 文件本身已接近损坏，需要更低层定位

相关脚本：

1. `python .codebuddy/skills/xlsx/scripts/office/unpack.py <office_file> <output_dir>`
2. `python .codebuddy/skills/xlsx/scripts/office/pack.py <input_directory> <output_file> --validate false`
