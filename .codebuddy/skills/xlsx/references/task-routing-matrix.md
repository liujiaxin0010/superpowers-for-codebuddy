# XLSX 任务路由矩阵

本文件只在还没确定该用哪条处理路径时读取。

## 快速表

| 任务类型 | 首选工具 | 必读资源 | 不要读 |
|---|---|---|---|
| 普通 CSV/XLSX 数据清洗 | `pandas` | `python-automation-guide.md` | 金融标准、OOXML 低层工具 |
| 编辑现有模板、保留格式和公式 | `openpyxl` | `python-automation-guide.md` | 不相关示例 |
| 新增或修复公式 | `openpyxl` + `recalc.py` | `formula-quality-workflow.md` | 把 Python 计算值硬编码进去 |
| 金融模型 / 管理报表 | `openpyxl` | `financial-modeling-standards.md` + `formula-quality-workflow.md` | 纯数据清洗路径 |
| 低层 OOXML 手术 | `scripts/office/unpack.py` + `pack.py` | `python-automation-guide.md` | `office/validate.py` 作为 xlsx 质量门禁 |

## 何时走低层 OOXML

1. openpyxl 会破坏现有结构
2. 文件已接近损坏，需要直接解包定位
3. 模板依赖无法由 openpyxl 安全保留
