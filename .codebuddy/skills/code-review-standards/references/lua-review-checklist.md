# Lua Code Review Checklist

Comprehensive checklist for reviewing Lua code, covering common pitfalls, performance, and best practices.

## Variable Scope

### 1. Global Variable Leaks
```lua
-- ❌ WRONG - Accidental global
function process()
    result = 10  -- Global variable!
    for i = 1, 10 do
        temp = i * 2  -- Another global!
    end
end

-- ✅ CORRECT - Use local
function process()
    local result = 10
    for i = 1, 10 do
        local temp = i * 2
    end
end
```

### 2. Local Variable Shadowing
```lua
-- ❌ WRONG - Confusing shadowing
local x = 10
function test()
    local x = 20  -- Shadows outer x
    if true then
        local x = 30  -- Shadows again
    end
end

-- ✅ CORRECT - Use distinct names
local globalX = 10
function test()
    local localX = 20
    if true then
        local innerX = 30
    end
end
```

## Table Operations

### 1. Table Length
```lua
-- ❌ WRONG - # operator with holes
local t = {1, 2, nil, 4, 5}
print(#t)  -- Undefined behavior!

-- ✅ CORRECT - Use explicit count
local function tableLength(t)
    local count = 0
    for _ in pairs(t) do
        count = count + 1
    end
    return count
end
```

### 2. Table Iteration
```lua
-- ❌ WRONG - ipairs stops at nil
local t = {1, 2, nil, 4}
for i, v in ipairs(t) do
    print(v)  -- Only prints 1, 2
end

-- ✅ CORRECT - Use pairs for sparse tables
for k, v in pairs(t) do
    print(k, v)
end
```

### 3. Table Copy
```lua
-- ❌ WRONG - Reference copy
local original = {a = 1, b = 2}
local copy = original  -- Same table!
copy.a = 10  -- Modifies original!

-- ✅ CORRECT - Shallow copy
local function shallowCopy(t)
    local copy = {}
    for k, v in pairs(t) do
        copy[k] = v
    end
    return copy
end
```

## Performance

### 1. String Concatenation
```lua
-- ❌ WRONG - O(n²) complexity
local result = ""
for i = 1, 1000 do
    result = result .. tostring(i)
end

-- ✅ CORRECT - Use table.concat
local parts = {}
for i = 1, 1000 do
    parts[i] = tostring(i)
end
local result = table.concat(parts)
```

### 2. Local Function References
```lua
-- ❌ WRONG - Global lookup each call
for i = 1, 1000000 do
    math.sin(i)  -- Global lookup
end

-- ✅ CORRECT - Cache in local
local sin = math.sin
for i = 1, 1000000 do
    sin(i)  -- Faster local access
end
```

## Static Analysis Tools

Recommended tools:
- **luacheck**: Static analyzer and linter
- **selene**: Modern Lua linter

Configuration (.luacheckrc):
```lua
globals = {"vim", "love"}
max_line_length = 120
```
