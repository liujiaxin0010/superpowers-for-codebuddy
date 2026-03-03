# Lua 安全编码规范

> **版本**：V1.0 &nbsp;|&nbsp; **适用范围**：所有基于 Lua 语言开发的产品（含 LuaJIT、OpenResty）
> **级别定义**：【规则】必须遵守的强制约定 ·【建议】应加以考虑的推荐约定

---

## 1 变量作用域

### 1.1 【规则】所有变量须使用 `local` 声明

未声明 `local` 的变量会泄漏到全局环境，导致命名冲突和难以追踪的 Bug。

```lua
-- ✗ 错误：全局变量泄漏
count = 0
function increment()
    count = count + 1
end

-- ✓ 正确
local count = 0
local function increment()
    count = count + 1
end
```

### 1.2 【规则】禁止变量遮蔽（Shadowing）外层同名变量

```lua
-- ✗ 错误
local value = 10
if condition then
    local value = 20  -- 遮蔽外层 value
end
```

### 1.3 【建议】模块级变量集中声明在文件顶部

---

## 2 Table 操作

### 2.1 【规则】稀疏 Table 禁止使用 `#` 获取长度

`#` 操作符对稀疏表行为未定义。

```lua
-- ✗ 错误
local t = {[1] = "a", [3] = "c"}
print(#t)  -- 结果不确定

-- ✓ 正确：手动计数或使用连续数组
local count = 0
for _ in pairs(t) do count = count + 1 end
```

### 2.2 【规则】遍历 Table 须选择正确的迭代器

- `ipairs()` — 连续整数键（数组部分），遇到 `nil` 停止
- `pairs()` — 所有键值对（无序）

### 2.3 【规则】深拷贝 Table 须递归处理

```lua
local function deep_copy(orig)
    if type(orig) ~= "table" then return orig end
    local copy = {}
    for k, v in pairs(orig) do
        copy[deep_copy(k)] = deep_copy(v)
    end
    return setmetatable(copy, getmetatable(orig))
end
```

---

## 3 性能

### 3.1 【规则】字符串拼接须使用 `table.concat`

```lua
-- ✗ 错误：每次拼接创建新字符串
local s = ""
for i = 1, 1000 do
    s = s .. tostring(i)
end

-- ✓ 正确
local parts = {}
for i = 1, 1000 do
    parts[#parts + 1] = tostring(i)
end
local s = table.concat(parts)
```

### 3.2 【规则】热路径中须将全局函数缓存为 local

```lua
-- ✗ 不推荐
for i = 1, 100000 do
    math.sin(i)
end

-- ✓ 推荐
local sin = math.sin
for i = 1, 100000 do
    sin(i)
end
```

### 3.3 【建议】避免在循环中创建闭包

---

## 4 错误处理

### 4.1 【规则】可能失败的操作须使用 `pcall` / `xpcall`

```lua
-- ✓ 正确
local ok, result = pcall(json.decode, raw_str)
if not ok then
    log.error("JSON 解析失败: " .. tostring(result))
    return nil
end
```

### 4.2 【规则】模块函数须返回明确的错误信息

```lua
-- ✓ 正确：返回 nil + 错误信息
local function read_config(path)
    local f, err = io.open(path, "r")
    if not f then
        return nil, "无法打开配置文件: " .. err
    end
    local content = f:read("*a")
    f:close()
    return content
end
```

---

## 5 安全性

### 5.1 【规则】禁止对外部输入使用 `loadstring` / `load`

```lua
-- ✗ 错误：代码注入
local fn = loadstring(user_input)
fn()
```

### 5.2 【规则】禁止在生产环境使用 `debug` 库

`debug` 库可绕过访问控制，须在生产环境中移除或禁用。

### 5.3 【规则】文件路径须验证防止路径穿越

---

## 6 模块化

### 6.1 【规则】模块须返回 Table，禁止污染全局环境

```lua
-- ✓ 正确
local M = {}

function M.greet(name)
    return "Hello, " .. name
end

return M
```

### 6.2 【规则】`require` 的模块路径禁止拼接外部输入

---

## 7 工程化

### 7.1 【规则】代码提交前须通过以下工具检查

| 工具 | 用途 |
|------|------|
| `luacheck` | 静态分析（未使用变量、全局泄漏） |
| `selene` | 高级 Lint 检查 |
| `stylua` | 代码格式化 |

---

## 参考文献

- Lua Style Guide (https://github.com/Olivine-Labs/lua-style-guide)
- Programming in Lua (https://www.lua.org/pil/)
