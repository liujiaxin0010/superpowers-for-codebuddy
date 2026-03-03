---
description: 代码简化，减少复杂度和冗余代码
---

# 代码简化（Code Simplifier）

基于 Anthropic 官方 code-simplifier 插件设计。在长时间编码后、PR 提交前、或简化历史代码时使用。**核心原则：只改实现方式，不改功能行为。**

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

---

## 何时使用

- Boss 明确要求简化代码
- 长时间编码会话结束后清理代码
- PR 提交前做最后一轮简化
- 对历史遗留代码进行重构
- 使用 `/simplify` 命令时

## 不可违反的约束

1. **保持功能不变** — 永远不改代码做什么，只改怎么做。所有原始功能、输出和行为必须完全保留
2. **所有测试必须通过** — 简化后运行全量测试，一个都不能少
3. **不引入新依赖** — 简化不是重写
4. **不跨模块重构** — 只在当前文件/模块范围内简化，除非 Boss 明确要求
5. **可读性优于简洁** — 目标是让代码更容易理解，不是让行数最少

---

## 简化策略（按优先级）

### 策略一：消除冗余

**DRY 原则** — 找到重复代码，提取为可复用函数/方法/模块：

```java
// ❌ 重复逻辑散布在多处
public void createOrder(OrderDTO dto) {
    if (dto.getAmount() <= 0) throw new BusinessException("金额必须大于0");
    if (dto.getAmount() > 999999) throw new BusinessException("金额超出上限");
    // ...业务逻辑
}
public void updateOrder(Long id, OrderDTO dto) {
    if (dto.getAmount() <= 0) throw new BusinessException("金额必须大于0");
    if (dto.getAmount() > 999999) throw new BusinessException("金额超出上限");
    // ...业务逻辑
}

// ✅ 提取公共校验
private void validateAmount(BigDecimal amount) {
    if (amount.compareTo(BigDecimal.ZERO) <= 0) throw new BusinessException("金额必须大于0");
    if (amount.compareTo(MAX_AMOUNT) > 0) throw new BusinessException("金额超出上限");
}
```

**用标准库替代手写实现**：

```python
# ❌ 手写去重保序
def unique_ordered(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

# ✅ 使用 dict.fromkeys（Python 3.7+ 保序）
def unique_ordered(items):
    return list(dict.fromkeys(items))
```

### 策略二：简化条件逻辑

**Guard Clause 提前返回**：

```go
// ❌ 深层嵌套
func processOrder(order *Order) error {
    if order != nil {
        if order.Status == "pending" {
            if order.Amount > 0 {
                // ...实际逻辑（已经缩进了3层）
                return nil
            } else {
                return errors.New("invalid amount")
            }
        } else {
            return errors.New("invalid status")
        }
    } else {
        return errors.New("nil order")
    }
}

// ✅ Guard Clause 拍平
func processOrder(order *Order) error {
    if order == nil {
        return errors.New("nil order")
    }
    if order.Status != "pending" {
        return errors.New("invalid status")
    }
    if order.Amount <= 0 {
        return errors.New("invalid amount")
    }
    // ...实际逻辑（缩进只有1层）
    return nil
}
```

**简化布尔表达式**：

```javascript
// ❌ 冗余判断
if (isValid === true) { ... }
if (list.length > 0 ? true : false) { ... }
if (value !== null && value !== undefined) { ... }

// ✅ 简洁
if (isValid) { ... }
if (list.length > 0) { ... }
if (value != null) { ... }
```

### 策略三：拆分大函数

超过 **50 行**的函数应该考虑拆分。判断标准：函数名是否需要用"和"来描述它做的事？

```python
# ❌ 一个函数做太多事
def process_and_save_and_notify(data):
    # 验证...（20行）
    # 处理...（30行）
    # 保存...（15行）
    # 通知...（10行）
    pass

# ✅ 单一职责
def process_order(data):
    validated = validate(data)
    result = calculate(validated)
    save(result)
    notify(result)
```

### 策略四：改善命名

```go
// ❌ 含糊的命名
func do(d map[string]interface{}) error { ... }
var tmp = getResult()
for _, v := range items { ... }

// ✅ 描述性命名
func processPayment(payload map[string]interface{}) error { ... }
var activeUsers = fetchActiveUsers()
for _, order := range pendingOrders { ... }
```

### 策略五：现代化语法

使用语言的现代特性替换冗长的旧写法（但不为了用新特性而用）：

```go
// Go: 使用 errors.Is / errors.As 替代字符串比较
// ❌
if err.Error() == "not found" { ... }
// ✅
if errors.Is(err, ErrNotFound) { ... }

// Go: 使用 slices 包（Go 1.21+）
// ❌
sort.Slice(items, func(i, j int) bool { return items[i].Name < items[j].Name })
// ✅
slices.SortFunc(items, func(a, b Item) int { return cmp.Compare(a.Name, b.Name) })
```

---

## 简化不做的事

| 禁止操作 | 原因 |
|---|---|
| 改变公共 API 签名 | 会破坏调用方 |
| 删除"看起来没用"的代码 | 可能有隐含依赖，需要 Boss 确认 |
| 过度抽象（为2处重复创建接口） | 过早抽象比重复更有害 |
| 嵌套三元表达式 | 降低可读性 |
| 合并不相关的逻辑 | 违反单一职责 |
| 删除有价值的注释 | 保留复杂逻辑的解释注释 |
| 改变错误处理策略 | 这是行为变更 |

---

## 执行流程

1. **确定范围** — 只简化最近修改的文件，或 Boss 指定的范围
2. **运行测试** — 确认简化前测试全部通过（建立基线）
3. **逐文件分析** — 识别简化机会，按策略优先级排序
4. **向 Boss 报告计划** — 展示将要做的简化及理由
5. **Boss 确认后执行** — 逐步简化，每步后运行测试
6. **运行全量测试** — 确保所有测试仍然通过
7. **更新三层文档** — 如果简化导致接口或职责变化，同步更新注释和 CONTEXT.md
8. **展示 diff** — 向 Boss 展示简化前后的对比

---

## 辅助文档

- **测试反模式清单** → `.codebuddy/skills/test-driven-development/testing-anti-patterns.md`（简化后测试质量不能降低）
