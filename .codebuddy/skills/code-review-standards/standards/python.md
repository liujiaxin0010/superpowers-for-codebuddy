# Python 安全编码规范

> **版本**：V2.0 &nbsp;|&nbsp; **适用范围**：所有基于 Python 语言开发的产品  
> **级别定义**：【规则】必须遵守的强制约定 ·【建议】应加以考虑的推荐约定  
> **基础标准**：本规范基于 PEP 8，在其基础上增加安全编码要求

---

## 1 代码布局

### 1.1 缩进与空白

| 项目 | 规范 |
|------|------|
| 缩进 | 4 个空格，禁止使用 Tab |
| 行长度 | 代码不超过 79 字符，注释/文档字符串不超过 72 字符 |
| 空行 | 顶层定义间 2 个空行，类方法间 1 个空行 |
| 编码 | UTF-8（Python 3 默认） |

### 1.2 续行规范

优先使用圆括号、方括号、花括号内的隐式续行。续行与包裹元素对齐或使用悬挂缩进。

```python
# ✓ 与左括号对齐
result = long_function(var_one, var_two,
                       var_three, var_four)

# ✓ 悬挂缩进
result = long_function(
    var_one, var_two,
    var_three, var_four)

# ✗ 不推荐：第一行有参数时不使用垂直对齐
result = long_function(var_one, var_two,
    var_three, var_four)
```

### 1.3 二元运算符换行

推荐在运算符之前换行，使运算符与操作数对齐。

```python
# ✓ 推荐
income = (gross_wages
          + taxable_interest
          - ira_deduction)
```

### 1.4 导入规范

- 每个导入独占一行
- 导入位于文件顶部（模块注释和文档字符串之后）
- 按分组排列：标准库 → 第三方库 → 本地模块，组间空行
- 推荐绝对路径导入
- 禁止通配符导入 `from module import *`

```python
# ✓ 正确
import os
import sys

from third_party import lib

from myproject import mymodule
```

---

## 2 安全编码规则

### 2.1 【规则】禁止使用 `eval()` / `exec()` 执行不可信数据

`eval()` 和 `exec()` 会执行任意 Python 代码，是代码注入的首要风险点。

```python
# ✗ 危险
result = eval(user_input)

# ✓ 安全：使用 ast.literal_eval 解析字面量
import ast
result = ast.literal_eval(user_input)
```

### 2.2 【规则】禁止使用 `os.system()` / `subprocess.shell=True` 执行外部输入

外部输入传入 shell 命令会导致命令注入。

```python
# ✗ 危险：shell 注入
import os
os.system("ping " + user_input)

import subprocess
subprocess.call("ping " + user_input, shell=True)

# ✓ 安全：使用列表形式传参，禁止 shell=True
subprocess.call(["ping", "-c", "3", validated_host])
```

### 2.3 【规则】SQL 操作须使用参数化查询

```python
# ✗ 危险：字符串拼接
cursor.execute("SELECT * FROM users WHERE name='%s'" % username)

# ✓ 安全：参数化查询
cursor.execute("SELECT * FROM users WHERE name=%s", (username,))
```

### 2.4 【规则】文件路径须进行标准化校验

对外部传入的文件路径须检查目录遍历字符，并使用 `os.path.realpath()` 标准化后校验。

```python
import os

def safe_read(base_dir, filename):
    filepath = os.path.realpath(os.path.join(base_dir, filename))
    if not filepath.startswith(os.path.realpath(base_dir)):
        raise ValueError("Path traversal detected")
    with open(filepath, 'r') as f:
        return f.read()
```

### 2.5 【规则】XML 解析须禁用外部实体

使用 `defusedxml` 库替代标准库的 XML 解析器，防止 XXE 攻击。

```python
# ✓ 安全
import defusedxml.ElementTree as ET
tree = ET.parse(xml_file)

# ✗ 危险
import xml.etree.ElementTree as ET  # 可能受 XXE 攻击
```

### 2.6 【规则】禁止使用 `pickle` 反序列化不可信数据

`pickle.loads()` 可执行任意代码，禁止反序列化来自不可信来源的数据。使用 JSON 等安全格式替代。

```python
# ✗ 危险
import pickle
data = pickle.loads(untrusted_data)

# ✓ 安全
import json
data = json.loads(untrusted_data)
```

### 2.7 【规则】敏感信息禁止硬编码

口令、密钥、API Token 等不得写入源代码，须通过环境变量或安全的配置管理系统获取。

```python
# ✗ 错误
DB_PASSWORD = "s3cret"

# ✓ 正确
import os
DB_PASSWORD = os.environ.get("DB_PASSWORD")
```

### 2.8 【规则】使用安全的随机数生成器

安全场景（令牌、密钥、验证码等）须使用 `secrets` 模块，禁止使用 `random` 模块。

```python
# ✗ 不安全
import random
token = random.randint(0, 999999)

# ✓ 安全
import secrets
token = secrets.token_hex(32)
```

### 2.9 【规则】使用安全的哈希与加密算法

禁止使用 MD5、SHA1 进行安全用途。口令存储使用 `bcrypt`、`argon2` 或 `hashlib.pbkdf2_hmac`。

```python
import hashlib
import os

salt = os.urandom(32)
key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
```

### 2.10 【规则】日志中禁止记录敏感信息

日志不得包含口令、密钥、个人隐私数据等。

```python
# ✗ 错误
logger.info(f"User {user} login with password {password}")

# ✓ 正确
logger.info(f"User {user} login attempt")
```

---

## 3 类型与异常安全

### 3.1 【规则】与 `None` 比较使用 `is` / `is not`

```python
# ✓ 正确
if foo is not None:

# ✗ 错误
if foo != None:
if not foo is None:
```

### 3.2 【规则】类型比较使用 `isinstance()`

```python
# ✓ 正确
if isinstance(obj, int):

# ✗ 错误
if type(obj) is type(1):
```

### 3.3 【规则】空序列判断使用布尔求值

```python
# ✓ 正确
if not seq:    # 空
if seq:        # 非空

# ✗ 不推荐
if len(seq) == 0:
if len(seq):
```

### 3.4 【规则】异常捕获须指定具体异常类型

禁止使用裸 `except:` 捕获所有异常，这会掩盖 `SystemExit` 和 `KeyboardInterrupt`。

```python
# ✓ 正确
try:
    import optional_module
except ImportError:
    optional_module = None

# ✗ 错误
try:
    risky_operation()
except:  # 捕获了一切，包括 Ctrl+C
    pass
```

### 3.5 【规则】从 `Exception` 继承异常，而非 `BaseException`

### 3.6 【规则】`try` 块中只填充必要代码

```python
# ✓ 正确：缩小 try 范围
try:
    value = collection[key]
except KeyError:
    return key_not_found(key)
else:
    return handle_value(value)

# ✗ 错误：范围过大
try:
    return handle_value(collection[key])
except KeyError:
    return key_not_found(key)  # 也会捕获 handle_value 抛出的 KeyError
```

### 3.7 【规则】函数返回值保持一致

所有分支要么都返回表达式，要么都不返回。无值可返回时显式使用 `return None`。

```python
# ✓ 正确
def foo(x):
    if x >= 0:
        return math.sqrt(x)
    else:
        return None

# ✗ 错误：不一致
def foo(x):
    if x >= 0:
        return math.sqrt(x)
    # 隐式返回 None
```

---

## 4 资源管理安全

### 4.1 【规则】使用 `with` 语句管理资源

确保文件、网络连接、数据库连接等资源在使用后被正确释放。

```python
# ✓ 正确
with open('file.txt', 'r') as f:
    data = f.read()

# ✗ 不推荐
f = open('file.txt', 'r')
data = f.read()
f.close()  # 如果 read() 抛异常则不会执行
```

### 4.2 【规则】临时文件须及时清理

使用 `tempfile` 模块创建临时文件，并在使用后及时删除。

```python
import tempfile
import os

with tempfile.NamedTemporaryFile(delete=True) as tmp:
    tmp.write(data)
    tmp.flush()
    process(tmp.name)
# 退出 with 块后自动删除
```

### 4.3 【规则】创建文件须设置合理权限

```python
import os

# 设置文件权限为 0o640（-rw-r-----）
fd = os.open('secret.conf', os.O_WRONLY | os.O_CREAT, 0o640)
with os.fdopen(fd, 'w') as f:
    f.write(config_data)
```

---

## 5 命名规范

### 5.1 命名风格一览

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块/包 | 全小写，可用下划线 | `my_module` |
| 类 | 首字母大写驼峰 | `MyClass` |
| 异常 | 首字母大写驼峰 + `Error` 后缀 | `ValueError` |
| 函数/方法 | 全小写，下划线分隔 | `get_data()` |
| 常量 | 全大写，下划线分隔 | `MAX_OVERFLOW` |
| 实例变量 | 全小写，下划线分隔 | `user_name` |
| 内部使用 | 单下划线前缀 | `_internal_var` |
| 避免与关键字冲突 | 单下划线后缀 | `class_` |

### 5.2 【规则】禁止使用 `l`、`O`、`I` 作为单字符变量名

这些字符在某些字体中与数字 `0`、`1` 难以区分。

---

## 6 文档与注释

### 6.1 【规则】注释与代码不一致时优先更新注释

### 6.2 【规则】所有公共模块、函数、类、方法须编写文档字符串

```python
def fetch_data(url, timeout=30):
    """从指定 URL 获取数据。

    Args:
        url: 请求的目标地址。
        timeout: 超时时间（秒），默认 30。

    Returns:
        响应的文本内容。

    Raises:
        ConnectionError: 网络连接失败时抛出。
    """
```

### 6.3 【规则】多行文档字符串的结尾三引号须独占一行

---

## 7 编程建议

### 7.1 【规则】使用 `str.startswith()` / `str.endswith()` 代替切片比较

```python
# ✓ 正确
if foo.startswith('bar'):

# ✗ 不推荐
if foo[:3] == 'bar':
```

### 7.2 【规则】使用 `def` 定义函数，不要将 `lambda` 赋值给变量

```python
# ✓ 正确
def f(x): return 2 * x

# ✗ 不推荐
f = lambda x: 2 * x
```

### 7.3 【规则】使用字符串方法代替 `string` 模块

字符串方法更快且与 Unicode 共享相同 API。

### 7.4 【规则】不要用 `==` 与 `True` / `False` 比较

```python
# ✓ 正确
if greeting:

# ✗ 不推荐
if greeting == True:
if greeting is True:
```

### 7.5 【建议】使用 `is not` 代替 `not ... is`

```python
# ✓ 推荐
if foo is not None:

# ✗ 不推荐
if not foo is None:
```

### 7.6 【建议】使用格式化工具自动校验

推荐使用 PyCharm 快捷键 `Ctrl+Alt+L` 或命令行工具：

| 工具 | 用途 |
|------|------|
| `black` | 代码自动格式化 |
| `flake8` | PEP 8 风格检查 |
| `mypy` | 静态类型检查 |
| `bandit` | Python 安全漏洞扫描 |
| `safety` | 依赖包已知漏洞检查 |

---

## 8 Web 安全（适用于 Django/Flask 等框架）

### 8.1 【规则】所有外部输入须在服务端校验

客户端校验仅用于用户体验优化，不可作为安全保障。

### 8.2 【规则】模板输出须自动转义

Django 和 Jinja2 默认启用自动转义，禁止使用 `|safe` / `{% autoescape off %}` 输出未过滤的用户数据。

### 8.3 【规则】启用 CSRF 防护

Django 默认启用 CSRF 中间件，确保所有表单包含 `{% csrf_token %}`。

### 8.4 【规则】会话配置须安全

```python
# Django settings.py
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 8.5 【规则】生产环境须关闭 `DEBUG` 模式

`DEBUG = True` 会在异常时泄露源代码、数据库结构等敏感信息。

---

## 参考文献

- PEP 8 — Style Guide for Python Code (https://peps.python.org/pep-0008/)
- OWASP Python Security Cheat Sheet
- Bandit — Python Security Linter (https://github.com/PyCQA/bandit)
