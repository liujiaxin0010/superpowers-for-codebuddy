---
name: openapi-creator
description: >
  当 Boss 需要设计、定义或创建宇视平台的 OpenAPI 接口时使用本技能。它覆盖完整生命周期：
  需求澄清、接口定义文档生成（Markdown）、规范校验、字段标准核对、OpenAPI YAML 导出。
  技能强制执行《平台类 OpenAPI 接口定义规范》（2024.1.0），并将字段与公司标准字段库交叉核对。
  当 Boss 提到"设计接口/定义 OpenAPI/创建接口/接口定义文档/校验接口规范/导出 OpenAPI YAML"时触发。
---

# OpenAPI 接口创建技能

生成符合宇视《平台类 OpenAPI 接口定义规范》的平台类 OpenAPI 接口定义，附带自动化规范校验与 OpenAPI YAML 导出。

## 何时使用

- Boss 要求设计 / 定义 / 创建 OpenAPI 接口
- Boss 给出接口需求（粗略或具体），需要形成正式的接口定义
- Boss 需要把已有接口定义按规范做一次校验
- Boss 需要 OpenAPI YAML 产物用于工具链（Swagger UI、Postman 等）
- 在 `brainstorming` 头脑风暴的「阶段四 → 接口设计」子阶段，作为平台类 OpenAPI 接口的设计规范来源

## 五阶段工作流

### 阶段一：需求澄清

在生成任何接口定义之前，先通过交互式问答与 Boss 澄清需求。

**必须澄清项（把相关项分组，把交互轮次压到 3-4 轮）：**

1. **ServiceURI + 资源** —— 属于哪个子系统、主要资源是什么？参考 `references/openapi-spec.md` 中的 ServiceURI 表。若 Boss 的描述无法明确映射到某个 ServiceURI，列出最接近的 3 个候选项请 Boss 选择。同时确认资源命名（例如所选资源名是否适合用 lowerCamelCase）。
2. **操作 + 分页 + 批量** —— 每个资源需要哪些操作？使用 Action 词汇表。确认查询类接口是否分页（默认：是）。确认批量操作及其类型（批量查询、批量删除等）。
3. **关键参数 + 排序** —— 是否有特殊字段、过滤条件或排序需求？（例如按时间倒序、按结果类型排序）
4. **文件上传/下载 + 鉴权** —— 是否有文件相关接口？是否有标准鉴权之外的特殊鉴权需求？

**澄清输出格式：**

```markdown
## 接口需求确认

- **ServiceURI**: {serviceURI}
- **基础路径**: /openAPI/{serviceURI}/v1
- **接口列表**:
  1. {Resource} / {Action} — {简述}
  2. {Resource} / {Action} — {简述}
  ...
- **分页**: {是/否, 哪些接口}
- **批量操作**: {是/否, 具体类型}
- **排序**: {是/否, 排序字段}
- **文件相关**: {是/否}
```

**关键约束**：把确认摘要展示给 Boss，并**等待 Boss 明确批准**（例如"确认""OK""没问题"）后再进入阶段二。在 Boss 明确确认需求之前，**不得**生成任何 Markdown 接口定义文档。

### 阶段二：生成

基于已确认的需求和规范，生成 Markdown 接口定义文档。

**生成前，先获取公司标准字段库：**

标准字段库文档（《服务器产品数据项标准.docx》）托管在内部 GitLab 上，需要鉴权访问。

**步骤 1：通过 chrome-devtools MCP 下载 .docx 文件（Blob 下载方式）**

GitLab 凭据：使用 Boss 本人的 OA 账号。**如果是首次使用，向 Boss 索取 GitLab 用户名和密码**（内部 GitLab `igcode.uniview.com` 使用 OA 凭据）。在当前会话内保存这些凭据。

文档 URL（原始下载）为：

```
http://igcode.uniview.com/RD-UNIVIEW/public/module_guidelines/-/raw/main/%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BA%A7%E5%93%81%E6%95%B0%E6%8D%AE%E9%A1%B9%E6%A0%87%E5%87%86.docx
```

**下载流程（已验证可用）：**

1. 先检查浏览器是否已登录 GitLab：导航到 `http://igcode.uniview.com/` 并截取快照。若已登录（页面显示仪表盘），跳过登录步骤。若未登录（显示登录表单），继续执行登录。
2. 若需要登录：导航到 `http://igcode.uniview.com/users/sign_in`，截取快照获取 UID，用 `fill_form` 填入 OA 用户名和密码，然后点击 "Sign in"。
3. 登录成功后，用 `evaluate_script` 通过 Blob URL 触发浏览器下载：

   ```javascript
   async () => {
     const resp = await fetch('/RD-UNIVIEW/public/module_guidelines/-/raw/main/%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BA%A7%E5%93%81%E6%95%B0%E6%8D%AE%E9%A1%B9%E6%A0%87%E5%87%86.docx');
     const blob = await resp.blob();
     const url = URL.createObjectURL(blob);
     const a = document.createElement('a');
     a.href = url;
     a.download = '{resource}_field_library.docx';
     document.body.appendChild(a);
     a.click();
     document.body.removeChild(a);
     URL.revokeObjectURL(url);
     return { status: resp.status, size: blob.size, type: blob.type };
   }
   ```

   **关键约束**：下载文件名**必须**基于接口资源名动态命名（例如 `{resource}_field_library.docx`，如 `device_field_library.docx`、`person_field_library.docx`），以避免同时处理多个 API 时文件名冲突。
4. 浏览器会把文件下载到默认的 Downloads 文件夹。
5. 搜索下载好的文件并拷贝到工作区：

   ```powershell
   # 在用户的 Downloads 文件夹中搜索（用户名可能不同）
   $file = Get-ChildItem -Path "$env:USERPROFILE\Downloads" -Filter '{resource}_field_library.docx' -ErrorAction SilentlyContinue | Select-Object -First 1
   if ($file) {
     Copy-Item $file.FullName '{workspace}\{resource}_field_library.docx' -Force
     Remove-Item $file.FullName -Force
   } else {
     # 兜底：递归搜索
     $file = Get-ChildItem -Path $env:USERPROFILE -Filter '{resource}_field_library.docx' -Recurse -ErrorAction SilentlyContinue -Depth 2 | Select-Object -First 1
     if ($file) {
       Copy-Item $file.FullName '{workspace}\{resource}_field_library.docx' -Force
       Remove-Item $file.FullName -Force
     }
   }
   ```

**关键约束 —— 不要用 base64 编码通过 evaluate_script 传输二进制文件！**

- `btoa(String.fromCharCode(...bytes))` 方式在大文件上会导致**栈溢出**
- 通过 evaluate_script 做分块 base64 会被 MCP 输出上限**截断**
- Blob 下载方式是唯一可靠的方式 —— 它使用浏览器原生的下载机制

**步骤 2：解析 .docx 文件**

有两种解析方式。先尝试**方式 A**；失败时回退到**方式 B**。

**方式 A：docx 技能解包 + `parse_field_library.py`（推荐，不依赖 python-docx）**

> ⚠️ **依赖说明**：方式 A 依赖 `.codebuddy/skills/docx` 技能（用于调用其 `scripts/office/unpack.py` 解包 .docx）。本项目已提供 docx 技能，方式 A 可直接使用。若该技能被移除，跳过方式 A，回退到方式 B（python-docx）。

1. 用 `use_skill` 调用 `"docx"` 技能激活 docx 技能
2. 解包 .docx 提取 XML：

   ```bash
   python {docx_skill_path}/scripts/office/unpack.py {resource}_field_library.docx {resource}_field_library_unpacked/
   ```

3. 用通用表格解析器解析 XML（**不要使用 --keywords 过滤，解析所有表格以保证完整性**）：

   ```bash
   python scripts/parse_field_library.py --input {resource}_field_library_unpacked/word/document.xml --output {resource}_field_library_parsed.json
   ```

   - `--input`：解包后 `document.xml` 的路径
   - `--output`：解析结果 JSON 的输出路径
   - **不要使用 `--keywords` 过滤**：像"设备""类型""结果"这类关键词过于宽泛，会匹配到无关表格（例如职业代码表）。完整解析更可靠；读结果时可以手动过滤。
4. 解析器会把表格自动归类为 `field`（含"标识符/名称"+"表示格式"列）或 `enum`（含"代码"列），与文档章节编号无关
5. 转换为可校验格式：

   ```bash
   python scripts/convert_field_lib.py --input {resource}_field_library_parsed.json --output {resource}_field_library.json
   ```

**方式 B：`fetch_field_library.py`（使用 python-docx，可能因 KeyError 失败）**

```bash
python scripts/fetch_field_library.py --input {resource}_field_library.docx --output-dir .
```

它使用 python-docx 直接解析。部分来自内部 GitLab 的 .docx 文件可能与某些 python-docx 版本不兼容（关系类型上的 KeyError）。遇到这种情况时，使用上面的方式 A。

**步骤 3：把解析出的字段库作为参考**

1. 读取 `{resource}_field_library_parsed.json` 产物，了解可用的字段名和枚举值
2. 把 `{resource}_field_library.json` 作为阶段三校验的输入
3. 把每个字段的"引用的数据元"映射到对应的附录枚举值
4. **生成后立即**列出所有标记为"未定义"的字段，并提醒 Boss：
   > ⚠️ 以下字段未在《服务器产品数据项标准》中找到对应定义，建议先提交修订提案，待提案通过后再进行字段定义：
   > - `{fieldName1}`（{简要说明}）
   > - `{fieldName2}`（{简要说明}）

**Markdown 文档模板：**

```markdown
# {模块名称} OpenAPI 接口定义

## 接口概述
- 模块说明：{简要描述}
- ServiceURI：{如 video}
- 基础路径：/openAPI/{serviceURI}/v1

## 1. {接口中文名称}

### 基本信息
| 项目 | 内容 |
|------|------|
| URL | /openAPI/{serviceURI}/v1/{resource}/{action} |
| 方法 | POST |
| 描述 | {接口功能描述} |
| 注意事项 | {使用该接口需注意的事项} |

### 请求参数
| 参数名称 | 数据类型 | 是否必须 | 参数描述 | 字段标准引用 |
|----------|----------|----------|----------|--------------|
| ... | ... | 是/否 | ... | {标准字段名或附录编号,如"标准-性别"或"B.10-性别"} |

### 请求示例
{ ... }

### 响应参数
| 参数名称 | 数据类型 | 是否必须 | 参数描述 | 字段标准引用 |
|----------|----------|----------|----------|--------------|
| code | integer | 是 | 错误码 | — |
| message | string | 是 | 错误描述 | — |
| data | object | 否 | 返回数据 | — |

#### data 字段
| 参数名称 | 数据类型 | 是否必须 | 参数描述 | 字段标准引用 |
|----------|----------|----------|----------|--------------|
| ... | ... | 是/否 | ... | {标准字段名或附录编号} |

### 响应示例
{ ... }

---
```

**"字段标准引用"列填写规则：**

- 如果该字段（含枚举值）在《服务器产品数据项标准.docx》中有定义，填写对应的**标准字段名称**或**附录编号**
  - 例如：`标准-性别`、`B.10-性别`、`标准-年龄段`、`B.10-年龄段`
- 如果该字段是通用字段（如 `code`、`message`、`pageNo` 等），填写 `通用字段`
- 如果该字段在标准文档中未找到，填写 `未定义`，并在生成后提醒 Boss：
  > ⚠️ 字段 "{fieldName}" 未在《服务器产品数据项标准》中找到对应定义，建议先提交修订提案，待提案通过后再进行字段定义。
- 非枚举、非业务语义的纯技术字段（如 `code`、`message`）填写 `—`

**生成规则（必须严格遵守）：**

- **表格格式**：使用标准 Markdown 管道表格，只用单个 `|`。每行必须以 `|` 开头和结尾。**绝不使用 `||`（双竖线）** —— 它不是合法 Markdown，会导致渲染问题。正确：`| cell1 | cell2 |`，错误：`|| cell1 | cell2 |` 或 `||| cell1 | cell2 |`
- **嵌套字段命名**：参数表中的嵌套字段用点号表示法（例如 `filter.bodyFeature.gender`、`filter.timeRange.startTime`）。点号分隔的路径是结构性的，**不是**字段名 —— 它们豁免 V-05 camelCase 校验
- **数据类型**：只能使用 `integer`、`number`、`string`、`array`、`object`
- **URL 格式**：`{Schema}://{Host}/openAPI/{ServiceURI}/{Version}/{Resource}[/{Child-Resource}]/{Action}`
- **URL 命名**：lowerCamelCase，只能用英文字母和数字
- **HTTP 方法**：始终为 POST
- **字段命名**：lowerCamelCase
- **数组字段命名**：使用 "List" 后缀（例如 `deviceList`）。**两个例外：**
  1. **过滤条件数组**如 `channelIndexCodes`、`regionIndexCodes` 使用语义后缀（"Codes"），可以不带 "List" 后缀
  2. **响应结果数组**可以用 `list` 作为字段名（查询结果的惯例）。List 父对象下的嵌套数组（例如 `searchEngineList.searchEngineInfo`）使用语义化命名。
- **批量输入数组**必须使用 "List" 后缀（例如 `{resource}IndexCodeList`，**不是** `{resource}IndexCodes`）。"Codes" 后缀保留给过滤条件；批量输入是另一种语义模式。
- **枚举字段**：在描述中列出所有可能取值及含义
- **时间字段**：在描述中指明格式为 ISO8601
- **可选字段**：必须说明何时携带 —— 使用诸如"传入{parentObject}时按需携带""不传则不过滤""需{condition}时才有意义"的措辞。这能主动满足 V-15 校验
- **响应结构**：必须包含 `code`（integer）和 `message`（string）；`data` 可选
- **分页**：使用 `pageNo`（从 1 开始）、`pageSize`、`total`
- **批量响应**：使用 `successList`/`failureList` 格式
- **布尔字段**：绝不使用 "is" 前缀（用 `supportXxx` 或 `successFlag`）。布尔语义用 `string` 类型表示，枚举值为 `0-未知/1-是/2-否`（遵循公司标准）
- **空值**：绝不返回 null；string 字段用空串 "" 或省略可选字段
- **根 IndexCode**：根节点用 "1"，根节点的父用 "-1"
- **数组长度字段**：不要在数组旁额外加长度/计数字段（例如 ❌ `deviceNum` + `deviceList` → ✅ 只保留 `deviceList`）。例外：当 "num" 字段有独立语义时（例如 `searchEngineList.num` 表示"跨多少台服务器搜索"）
- **排序**：若需要排序，在请求参数中加入 `sortField`（string）和 `sortOrder`（string，"asc"/"desc"），并在文档中说明可排序字段

### 阶段三：校验

#### 步骤 1：准备字段库 JSON

如果使用 `fetch_field_library.py`（阶段二步骤 2），其产物 `field_library.json` 已是正确格式 `{"categories": [{"fields": [...]}]}`，可直接使用。

如果使用自定义解析器（`{resource}_field_library_parsed.json`），需先转换：

```bash
python scripts/convert_field_lib.py --input {resource}_field_library_parsed.json --output {resource}_field_library.json
```

#### 步骤 2：运行规范校验

**推荐：使用内联 `python -c` 并加 `-u` 标志（无缓冲输出），避免 Windows 上的 stdout 缓冲问题：**

```bash
python -u -c "import sys; sys.path.insert(0, r'{skill_path}/scripts'); from validate_api import validate_all, load_field_library; md = open(r'{output}.md', encoding='utf-8').read(); field_lib = load_field_library(r'{resource}_field_library.json'); issues = validate_all(md, field_lib); [print(f'[{i.severity.value}][{i.id}] {i.location}: {i.message}') for i in issues]; print(f'Total: {len(issues)}')"
```

**如果倾向于用脚本文件，保存为 `run_validate.py` 并在 print 中加 `flush=True`：**

```python
import sys
sys.path.insert(0, r'{skill_path}/scripts')
from validate_api import validate_all, load_field_library

md = open(r'{output}.md', encoding='utf-8').read()
field_lib = load_field_library(r'{resource}_field_library.json') if __import__('os').path.exists(r'{resource}_field_library.json') else {"categories": []}
issues = validate_all(md, field_lib)
for i in issues:
    print(f'[{i.severity.value}][{i.id}] {i.location}: {i.message}', flush=True)
print(f'Total: {len(issues)}', flush=True)
```

注意：`load_field_library` 已经能优雅处理 None / 缺失文件（返回 `{"categories": []}`），所以不需要 DummyFieldLib 之类的变通方案。

**校验分类：**

**A. 规范符合性（来自 openapi-spec.md）：**

| ID | 检查项 |
|----|-------|
| V-01 | 字段类型只允许 integer/number/string/array/object |
| V-02 | URL 格式匹配 `{Schema}://{Host}/openAPI/{ServiceURI}/{Version}/{Resource}/{Action}` |
| V-03 | URL 使用 lowerCamelCase，只含字母和数字 |
| V-04 | HTTP 方法为 POST |
| V-05 | 字段名使用 lowerCamelCase |
| V-06 | 枚举字段在描述中列出取值和含义 |
| V-07 | 时间字段在描述中指明 ISO8601 格式 |
| V-08 | 响应体包含 code + message，data 可选 |
| V-09 | 布尔字段不使用 "is" 前缀 |
| V-10 | 没有多余的数组长度字段 |
| V-11 | 数组字段使用 "List" 后缀 |
| V-12 | ServiceURI 匹配规范词汇表 |
| V-13 | Action 匹配规范词汇表 |
| V-14 | 响应中无 null 值 |
| V-15 | 可选字段说明何时携带 |

**B. 业务逻辑校验：**

| ID | 检查项 |
|----|-------|
| B-01 | 列表/查询接口包含 pageNo/pageSize |
| B-02 | 批量接口使用 successList/failureList |
| B-03 | 无业务编码的批量接口使用 seqNo |
| B-04 | 根 IndexCode 为 "1"，父为 "-1" |
| B-05 | 文件上传使用 multipart/form-data |
| B-06 | 日期值符合 ISO8601 |

**C. 字段一致性校验（对照公司标准字段库）：**

| ID | 检查项 |
|----|-------|
| F-01 | 字段名匹配公司标准字段库 |
| F-02 | 字段库中存在但接口缺失的字段 —— 建议补充 |

**D. 字段标准引用校验：**

| ID | 检查项 |
|----|-------|
| R-01 | "字段标准引用"列不得为空，每个字段必须填写引用来源 |
| R-02 | 标记为"未定义"的字段需提醒 Boss 提交修订提案 |
| R-03 | 枚举字段的引用必须指向《服务器产品数据项标准.docx》中具体字段或附录编号 |

**已知校验细节（来自实测）：**

- **V-05（点号路径上的 camelCase）**：含点号的字段名（例如 `filter.bodyFeature.gender`、`filter.timeRange.startTime`）是嵌套对象路径，**不是**真实字段名。各段（`filter`、`bodyFeature`、`gender`）本身都是合法 camelCase。这类 V-05 告警应**跳过**。
- **V-10（数组长度字段）**：`searchEngineList.num` 不是冗余数组长度 —— 它表示"涉及的搜索引擎数量"，有独立语义。V-10 只应在计数字段明显冗余时告警（例如 `deviceNum` 与 `deviceList` 并存且 `deviceNum` = `len(deviceList)`）。
- **V-11（List 后缀）**：作为**过滤参数**的数组字段（例如 `channelIndexCodes`、`regionIndexCodes`）可以不带 "List" 后缀 —— "Codes" 后缀对过滤条件更语义化。响应数组字段 `list` 也可接受 —— 它是查询结果数组的惯用名。List 父对象下的嵌套数组（例如 `searchEngineList.searchEngineInfo`）也可接受。**但批量输入数组（例如 `{resource}IndexCodes`）必须用 "List" 后缀** —— 它们不是过滤条件。
- **V-07（时间字段格式）**：名字里含 "time" 的 object 类型字段（例如 `filter.timeRange`，它是含 `startTime`/`endTime` 的 `object`）本身不是时间字段 —— 跳过这类告警。
- **V-06（枚举值）**：若某字段在标准中是 `c(N)` string 类型（例如 `equipmentType`），它不是固定枚举，不要求列出取值。
- **V-15（可选字段条件）**：要主动通过 V-15，每个可选字段都必须含一句条件措辞，如"传入{parent}时按需携带""不传则不过滤""需{condition}时才有意义"。这些应在「生成」阶段写好，而不是事后补。
- **F-01（字段不在库中）**：常见平台字段如 `pageNo`、`pageSize`、`total`、`startTime`/`endTime`（查询条件）、`channelIndexCodes`/`regionIndexCodes`（过滤参数）不在字段库中但被普遍接受 —— 跳过这类告警。
- **F-01（snapURL 与 picURL）**：标准库里有 `picURL`，但人脸抓拍场景下 `snapURL` 是产品惯例且更语义化 —— 可接受的偏差。
- **B-02（批量识别）**：校验器只在 URL 含 "batch" 或描述含 "批量" 时识别批量接口。对于像 `bodyRecords/get` 这种接受数组输入并返回 `successList`/`failureList` 的接口，确保描述里明确写出 "批量" 以触发 B-02 校验。

#### 步骤 3：展示校验结果

把所有问题**严格按严重程度分组**展示：

- 🔴 **必须修复（Critical）**：违反规则（V-xx、B-xx、R-xx）—— 先全部列出
- 🟡 **建议修复（Warning）**：违反建议、字段不一致（F-xx）—— 列在 Critical 之后

示例格式：

```
🔴 必须修复:
  [V-11] 接口: {接口名} / 字段: alarmItems: 数组字段 'alarmItems' 未使用 'List' 后缀
  [V-06] 接口: {接口名} / 字段: deviceType: 枚举字段 'deviceType' 的描述中未列举可能的取值及含义

🟡 建议修复:
  [F-01] 接口: {接口名} / 字段: deviceIndexCode: 字段 'deviceIndexCode' 不在公司标准字段库中
  [V-12] 接口: {接口名}: ServiceURI 'xxx' 不在规范用词列表中
```

#### 步骤 4：交互式修复

对每个问题，判断处理动作：

**自动跳过类（无需询问 Boss）：**

- **V-12**（新增 ServiceURI）：若 Boss 在阶段一已确认新 ServiceURI，自动跳过并注明"新增子系统，用户已确认"
- **V-13**（批量 action）：标准批量操作命名，自动跳过
- **F-01**（字段不在库中）：常见平台字段（`pageNo`、`pageSize`、`total`、`startTime`/`endTime`、`filter.*`、`successList`/`failureList`）—— 自动跳过并注明"通用平台字段或新增业务字段"
- **V-02**（新 ServiceURI 的 URL 格式）：若 URL 结构正确（`/openAPI/{newURI}/v1/{Resource}/{Action}`），自动跳过并注明"URL格式实际符合规范，验证器不识别新ServiceURI"

**必须询问类（一次问一个）：**

- V-01、V-03、V-04、V-05、V-08、V-09、V-10、V-11、V-14：这些是必须修复的硬规则违规
- V-06、V-07、V-15：这些需要 Boss 对内容做判断

对每个必须询问的问题，按如下方式呈现：

```
🔴 V-09: 布尔字段 "isSupport" 使用了 "is" 前缀
   建议: 改为 "supportXxx" 或 "successFlag"
   是否修正? [是/否/跳过]
```

按 Boss 的指示应用修复。若某字段未在标准库中找到，提醒 Boss：

> ⚠️ 字段 "{fieldName}" 未在公司标准字段库中找到，建议先提交修订提案，待提案通过后再进行字段定义。

### 阶段四：Markdown 审查

把**完整生成的 Markdown 文档**（已应用校验修复）展示给 Boss 审查。

**必需的输出小节：**

1. **完整文档展示**：展示完整的 Markdown 文档内容（不只是摘要）
2. **校验结果摘要**：回顾修复了什么、跳过了什么
3. **"未定义"字段修订提案提醒**：始终包含本小节，列出所有标记为"未定义"的字段：
   > ⚠️ 以下字段未在《服务器产品数据项标准》中找到对应定义，建议先提交修订提案，待提案通过后再进行字段定义：
   > - `{fieldName1}`（{简要说明}）
   > - `{fieldName2}`（{简要说明}）

**关键约束**：等待 Boss 明确确认（例如"确认""OK""没问题"）后再进入阶段五。在 Boss 确认 Markdown 之前，**不得**进入 YAML 生成。

### 阶段五：YAML 导出

在 Boss 确认 Markdown（阶段四）**且**所有校验问题已解决或跳过（阶段三）之后，生成 OpenAPI 3.0 YAML 文件。

**关键约束**：YAML 生成只能在以下两件事都满足后进行：

1. 已运行校验，且所有问题已解决或跳过（阶段三）
2. Boss 已明确批准 Markdown 文档（阶段四）

**YAML 结构：**

```yaml
openapi: 3.0.0
info:
  title: {模块名称} OpenAPI
  version: v1
  description: {模块描述}

servers:
  - url: https://{host}/openAPI/{serviceURI}/v1
    description: Production

paths:
  /{resource}/{action}:
    post:
      summary: {接口描述}
      operationId: {operationId}
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                ...
              required:
                - ...
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                    description: 错误码
                  message:
                    type: string
                    description: 错误描述
                  data:
                    type: object
                    description: 返回数据
                    properties:
                      ...
```

**YAML 生成规则：**

- 使用 `openapi: 3.0.0`
- 所有 path 使用 POST 方法
- 字段类型映射：`integer` → `type: integer`，`number` → `type: number`，`string` → `type: string`，`array` → `type: array`，`object` → `type: object`
- **`required` 数组**：每个 Schema/Object 都要包含 `required` 数组，列出所有"是否必须"= "是"的字段。适用于：
  - 顶层请求体属性
  - 嵌套对象属性（例如 `filter` 对象的必填字段）
  - 响应 data 对象属性
  - `successList`/`failureList` 内数组项的属性
- **`enum` 约束**：对描述中有明确枚举值的字段（例如 "1-行李箱/2-背包/3-手提包"），加 `enum` 属性：

  ```yaml
  {resource}Type:
    type: string
    description: {资源}类型，1-类型A/2-类型B/3-类型C
    enum: ["1", "2", "3"]
  ```

- 为所有字段加 `description`
- 请求体内容类型用 `application/json`
- 文件上传接口用 `multipart/form-data` 内容类型，配 `type: string, format: binary`

**生成 YAML 后，校验格式：**

通过尝试解析来确认 YAML 是合法的 OpenAPI 3.0 文档：

```bash
python -u -c "import yaml, json; data = yaml.safe_load(open(r'{output}.yaml', encoding='utf-8')); assert data.get('openapi','').startswith('3.0'), 'Invalid OpenAPI version'; assert 'paths' in data, 'Missing paths'; assert 'info' in data, 'Missing info'; print(f'YAML validation passed: {len(data[\"paths\"])} paths, {data[\"info\"][\"title\"]}')"
```

若校验失败，修复 YAML 并重新校验。

**清理临时文件：**

YAML 生成并校验后，清理过程中创建的所有临时文件：

```powershell
# 清理本次 API 相关的所有临时文件
Remove-Item '{workspace}\{resource}_field_library.docx' -Force -ErrorAction SilentlyContinue
Remove-Item '{workspace}\{resource}_field_library_parsed.json' -Force -ErrorAction SilentlyContinue
Remove-Item '{workspace}\{resource}_field_library.json' -Force -ErrorAction SilentlyContinue
Remove-Item '{workspace}\{resource}_field_library_unpacked' -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item '{workspace}\run_validate.py' -Force -ErrorAction SilentlyContinue
```

**关键约束**：`field_library.json` 和所有中间文件**必须**清理。工作区只应保留最终的 `{output}.md` 和 `{output}.yaml`。

## 与头脑风暴的联动

当 `brainstorming` 头脑风暴进行到「阶段四 → 软件设计 → 子阶段 1：接口设计」，且接口属于**平台类 OpenAPI 接口**（对外 RESTful 接口、`/openAPI/...` 路径）时：

- 头脑风暴阶段只确认「接口清单 + 关键业务字段」，遵循本技能的「生成规则」对接口草案做约束（命名、数据类型、URL 格式、分页、批量、字段标准引用等）
- 头脑风暴阶段**不**展开本技能的完整五阶段流程
- 正式的接口定义文档生成、规范校验、YAML 导出，在头脑风暴结束后通过 `/openapi` 命令完成

## 错误处理

### 字段库下载失败

若通过 chrome-devtools MCP 下载失败：

1. 检查浏览器是否已登录 GitLab（导航到 `http://igcode.uniview.com/` 检查）
2. 若未登录，用 Boss 的 GitLab 凭据重新登录
3. 若 Blob 下载方式失败，尝试重新运行 evaluate_script
4. 若所有自动方式都失败，告知 Boss：
   > ⚠️ 无法通过自动方式访问公司标准字段库文档。请手动从 GitLab 下载《服务器产品数据项标准.docx》并放置到当前目录，然后使用 docx 技能解析（详见阶段二步骤 2）。
5. 仅用 A+B+D 类校验继续（跳过 F 类字段一致性检查）
6. 提醒 Boss：没有标准字段库时，"字段标准引用"列需手动填写

### python-docx 不兼容

若 `fetch_field_library.py` 报 `KeyError: "no relationship of type ..."`：

1. 这是部分 .docx 文件与某些 python-docx 版本的已知问题
2. 改用方式 A（docx 技能解包 + `parse_field_library.py`，见阶段二步骤 2）；本项目已提供 `.codebuddy/skills/docx` 技能，方式 A 可直接使用
3. **XML 解析器的关键点**：命名空间必须是 `http://purl.oclc.org/ooxml/wordprocessingml/main`（**不是** `schemas.openxmlformats.org`）
4. 解析后转换格式：`python scripts/convert_field_lib.py --input {resource}_field_library_parsed.json --output {resource}_field_library.json`

### .doc 格式转换失败

若没有 LibreOffice 做 .doc → .docx 转换：

1. 若文件已是 .docx，使用 docx 技能
2. 若文件是 .doc 格式，告知 Boss 并请其手动转换或提供 .docx 版本

### 无匹配的 ServiceURI

若 Boss 的需求无法映射到任何 ServiceURI：

1. 列出最接近的匹配项
2. 建议使用最相关的现有 ServiceURI
3. 若确实是全新的，标注需要注册新 ServiceURI

## 速查：最常见的违规

以下是最常被违反的规则 —— 务必反复检查：

1. **数据类型**：不要 `boolean`、`long`、`float`、`double` —— 用 `integer`/`number`/`string`
2. **布尔命名**：不要 "is" 前缀（❌ `isEnable` → ✅ `enableFlag` 或 `xxFlag`，配 string 枚举 `0-未知/1-是/2-否`）
3. **空值**：绝不返回 `null`（❌ `"name": null` → ✅ `"name": ""` 或省略字段）
4. **数组命名**：用 "List" 后缀（❌ `devices` → ✅ `deviceList`）。例外：过滤数组如 `channelIndexCodes`
5. **批量输入数组**：必须用 "List" 后缀（❌ `deviceIndexCodes` → ✅ `deviceIndexCodeList`）。"Codes" 后缀只给过滤条件
6. **URL 大小写**：lowerCamelCase（❌ `SearchPerson` → ✅ `searchByCondition`）
7. **HTTP 方法**：始终 POST，绝不 GET
8. **日期格式**：只用 ISO8601（❌ `2023/01/01` → ✅ `2023-01-01T00:00:00Z`）
9. **分页**：用 `pageNo`（从 1 开始），不是 `pageIndex` 或 `pageNum`
10. **数组长度**：不加多余计数字段（❌ `deviceNum` + `deviceList` → ✅ 只留 `deviceList`）。例外：有独立语义的 `num`
11. **根节点**：IndexCode="1"，parentIndexCode="-1"，绝不为 null
12. **字段标准引用**：每个字段必须标注引用来源，枚举字段必须指向具体标准定义
13. **可选字段条件**：每个可选字段都必须说明何时携带（例如"传入bodyFeature时按需携带""不传则不过滤"）
14. **嵌套字段路径**：点号分隔路径如 `filter.bodyFeature.gender` 是结构性的，**不是**字段名 —— 不要触发 V-05
15. **批量接口描述**：描述里必须含 "批量" 以触发 B-02 校验
16. **YAML 中的枚举值**：有明确枚举值的字段必须在 YAML schema 中含 `enum` 属性
17. **YAML 中的 required**：每个 object schema 都必须基于"是否必须=是"字段含 `required` 数组
