# 基于条件的等待模式（Condition-Based Waiting）

本文档是 `systematic-debugger` 子代理的辅助材料，解决异步操作调试中的等待和时序问题。

---

## 核心问题：异步 Bug 的不确定性

异步操作（网络请求、定时任务、消息队列、并发线程）中的 bug 最难调试，因为：
- 时序不确定——同样的代码执行顺序可能不同
- 竞争条件——多个操作同时修改共享状态
- 隐式依赖——A 操作依赖 B 操作先完成，但没有显式等待

---

## 反模式：固定时间等待

```javascript
// ❌ 固定等待——脆弱且浪费时间
await new Promise(resolve => setTimeout(resolve, 3000));
expect(element).toBeVisible();

// 如果操作 500ms 就完成了 → 浪费 2500ms
// 如果操作需要 3500ms → 测试失败
```

**永远不要用 `sleep(N)` 等待异步操作完成。** 这既不可靠又浪费时间。

---

## 正确模式：轮询等待（Poll Until）

```javascript
// ✅ 基于条件的等待
async function waitFor(conditionFn, { timeout = 5000, interval = 100 } = {}) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        try {
            const result = await conditionFn();
            if (result) return result;
        } catch (e) {
            // 条件还没满足，继续等
        }
        await new Promise(r => setTimeout(r, interval));
    }
    throw new Error(`等待超时 (${timeout}ms): 条件未满足`);
}

// 使用
await waitFor(() => document.querySelector('.result')?.textContent === 'Done');
```

---

## 常见异步调试场景及解决方案

### 场景一：事件驱动的先后顺序

```
问题：事件 A 的处理器假设事件 B 已经处理完毕，但实际 B 可能还没到
```

**调试方法**：
1. 在两个事件的处理器中都加日志（含时间戳）
2. 观察实际执行顺序
3. 确认是否存在未声明的时序依赖

**修复模式**：
```python
# ❌ 隐式依赖顺序
def handle_event_a():
    data = cache.get("b_result")  # 假设B已经执行过
    process(data)

# ✅ 显式等待依赖
def handle_event_a():
    data = wait_for_key("b_result", timeout=5)
    if data is None:
        raise TimeoutError("事件B未在预期时间内完成")
    process(data)
```

### 场景二：并发写入竞争

```
问题：两个请求同时修改同一条数据，后写入的覆盖先写入的
```

**调试方法**：
1. 检查是否使用了事务/锁
2. 在写入前后加日志，观察并发访问模式
3. 使用乐观锁的版本号检测冲突

**修复模式**：
```sql
-- 乐观锁
UPDATE t_order SET status = 'paid', version = version + 1
WHERE id = 123 AND version = 5;
-- 如果 affected_rows = 0，说明有并发冲突
```

### 场景三：回调地狱中的错误丢失

```javascript
// ❌ 错误被静默吞掉
fetchData(url, function(err, data) {
    if (err) return;  // 错误被忽略
    processData(data, function(err, result) {
        // 如果 processData 抛异常，没人知道
        saveResult(result);
    });
});

// ✅ 错误正确传播
async function pipeline(url) {
    const data = await fetchData(url);      // 错误自动抛出
    const result = await processData(data);  // 错误自动抛出
    await saveResult(result);                // 错误自动抛出
}
```

### 场景四：数据库连接池耗尽

```
症状：应用间歇性超时，日志显示 "connection pool exhausted"
```

**调试方法**：
1. 检查连接池配置（最大连接数、等待超时）
2. 搜索未关闭的连接（`grep -rn "getConnection\|openSession"` 然后检查对应的 close）
3. 检查长事务（`SELECT * FROM information_schema.innodb_trx`）
4. 检查连接泄漏监控日志

---

## 测试中的异步等待最佳实践

```javascript
// 前端测试框架通常提供内置的条件等待
// Jest + Testing Library
await waitFor(() => {
    expect(screen.getByText('加载完成')).toBeInTheDocument();
});

// Cypress
cy.get('.result').should('contain', '加载完成');  // 自动重试

// Playwright
await expect(page.locator('.result')).toHaveText('加载完成');
```

**原则**：
- 永远等待**业务条件**（"文本出现"、"状态变为X"），不要等待**固定时间**
- 设置合理的超时上限，超时即失败（不要无限等待）
- 超时失败的错误信息要包含**当前实际状态**（方便调试）
