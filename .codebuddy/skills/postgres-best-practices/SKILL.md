---
description: Postgres SQL 最佳实践和查询优化
---

# Postgres SQL 最佳实践

基于 Supabase Postgres Best Practices（MIT 协议）的 SQL 性能优化与安全指南。在编写、审查或优化 SQL 查询、表结构设计、数据库配置时强制参考本技能。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

---

## 何时使用

在以下场景中**必须**参考本技能规则：
- 编写 SQL 查询或设计表结构
- 创建/优化索引
- 排查数据库性能问题
- 配置连接池或扩展方案
- 使用 Postgres 特有功能
- 实现行级安全策略（RLS）

---

## 规则分类（按影响等级排序）

### CRITICAL — 查询性能（10-100x 提升）

#### 1. 缺失索引

**错误**：在高频 WHERE/JOIN 列上无索引，导致全表扫描。

```sql
-- ❌ 无索引的 WHERE 查询
SELECT * FROM orders WHERE customer_id = 123;
-- 如果 customer_id 无索引 → Sequential Scan

-- ✅ 创建索引
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

**原则**：对所有 WHERE、JOIN ON、ORDER BY 中频繁出现的列创建索引。使用 `EXPLAIN ANALYZE` 验证查询是否使用了索引。

#### 2. 低效 JOIN

```sql
-- ❌ 子查询代替 JOIN
SELECT * FROM orders
WHERE customer_id IN (SELECT id FROM customers WHERE status = 'active');

-- ✅ 使用 JOIN
SELECT o.* FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.status = 'active';
```

#### 3. SELECT * 问题

```sql
-- ❌ 取所有列
SELECT * FROM orders WHERE status = 'pending';

-- ✅ 只取需要的列
SELECT id, amount, created_at FROM orders WHERE status = 'pending';
```

**影响**：减少 I/O、网络传输和内存消耗。大表效果尤其显著。

#### 4. N+1 查询

```sql
-- ❌ 循环中逐条查询
for order in orders:
    customer = db.query("SELECT * FROM customers WHERE id = %s", order.customer_id)

-- ✅ 批量查询
SELECT o.*, c.name FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending';
```

### CRITICAL — 连接管理

#### 5. 连接池

**必须使用连接池**，不得让应用直连数据库。

```
推荐配置：
- 连接池大小 = CPU核心数 * 2 + 磁盘数
- 最大连接数不超过 Postgres max_connections 的 80%
- 空闲连接超时 10-30 分钟
- 使用 PgBouncer 或应用内连接池
```

**铁律**：永远不要设置 `max_connections = 1000`。Postgres 连接很昂贵，每个连接约占 10MB 内存。

#### 6. 连接泄漏

```python
# ❌ 忘记关闭连接
conn = pool.getconn()
cursor = conn.cursor()
cursor.execute(query)
# 如果此处抛异常，连接永远不会归还

# ✅ 使用 context manager
with pool.getconn() as conn:
    with conn.cursor() as cursor:
        cursor.execute(query)
```

### CRITICAL — 安全与 RLS

#### 7. RLS 策略优化

```sql
-- ❌ RLS 中使用函数导致无法走索引
CREATE POLICY user_access ON orders
FOR SELECT USING (
    user_id = (SELECT id FROM users WHERE email = current_setting('app.user_email'))
);

-- ✅ 直接使用 session 变量
CREATE POLICY user_access ON orders
FOR SELECT USING (
    user_id = current_setting('app.user_id')::uuid
);
```

#### 8. SQL 注入防护

```sql
-- ❌ 字符串拼接（SQL注入漏洞）
query = f"SELECT * FROM users WHERE name = '{user_input}'"

-- ✅ 参数化查询
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```

### HIGH — 表结构设计（5-20x 提升）

#### 9. 部分索引

```sql
-- ❌ 全量索引（99% 订单是 completed 状态）
CREATE INDEX idx_orders_status ON orders(status);

-- ✅ 部分索引（只索引活跃状态）
CREATE INDEX idx_orders_pending ON orders(status)
WHERE status IN ('pending', 'processing');
```

#### 10. 正确的数据类型

```sql
-- ❌ 用 text 存储 UUID
CREATE TABLE orders (id TEXT PRIMARY KEY);

-- ✅ 用原生类型
CREATE TABLE orders (id UUID PRIMARY KEY DEFAULT gen_random_uuid());

-- ❌ 用 FLOAT 存储金额
CREATE TABLE orders (amount FLOAT);

-- ✅ 用 NUMERIC 避免精度问题
CREATE TABLE orders (amount NUMERIC(12,2));
```

#### 11. 复合索引列顺序

```sql
-- 查询：WHERE status = 'active' AND created_at > '2024-01-01'

-- ❌ 顺序错误（选择性低的列在前）
CREATE INDEX idx_wrong ON orders(status, created_at);

-- ✅ 等值条件在前，范围条件在后
CREATE INDEX idx_right ON orders(status, created_at);
-- 如果 status 只有几个值，这个顺序恰好是对的
-- 如果 status 有很多值，考虑只建 created_at 索引

-- 经验法则：等值列在前 > 范围列在后 > ORDER BY 列最后
```

### MEDIUM-HIGH — 并发与锁

#### 12. 避免长事务

```sql
-- ❌ 长事务（持有锁太久）
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- ... 中间做了很多其他事情 ...
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- ✅ 最小化事务范围
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

#### 13. 死锁预防

```sql
-- ❌ 不同顺序更新同一组行（可能死锁）
-- 事务A: UPDATE accounts SET ... WHERE id = 1; UPDATE ... WHERE id = 2;
-- 事务B: UPDATE accounts SET ... WHERE id = 2; UPDATE ... WHERE id = 1;

-- ✅ 统一按 ID 升序锁定
-- 所有事务都按 id ASC 顺序更新
SELECT * FROM accounts WHERE id IN (1, 2) ORDER BY id FOR UPDATE;
```

#### 14. 在线 DDL

```sql
-- ❌ 普通 CREATE INDEX 会锁表
CREATE INDEX idx_orders_email ON orders(email);

-- ✅ CONCURRENTLY 不阻塞写入
CREATE INDEX CONCURRENTLY idx_orders_email ON orders(email);
```

### MEDIUM — 数据访问模式

#### 15. 分页优化

```sql
-- ❌ OFFSET 大页码性能差
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- ✅ 游标分页（Keyset Pagination）
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;
```

#### 16. 批量操作

```sql
-- ❌ 逐条插入
INSERT INTO logs (msg) VALUES ('a');
INSERT INTO logs (msg) VALUES ('b');
INSERT INTO logs (msg) VALUES ('c');

-- ✅ 批量插入
INSERT INTO logs (msg) VALUES ('a'), ('b'), ('c');

-- 更大批量使用 COPY
COPY logs (msg) FROM STDIN;
```

### LOW-MEDIUM — 监控与诊断

#### 17. 慢查询检测

```sql
-- 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 记录超过1秒的查询
SELECT pg_reload_conf();

-- 查看当前活跃的长查询
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

#### 18. 索引使用率

```sql
-- 查看索引命中率
SELECT relname, idx_scan, seq_scan,
       CASE WHEN seq_scan + idx_scan > 0
            THEN round(100.0 * idx_scan / (seq_scan + idx_scan), 1)
            ELSE 0 END AS idx_hit_pct
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;

-- 查看未使用的索引（浪费存储和写入性能）
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE 'pg_%';
```

---

## 代码审查清单

编写或审查 SQL 时，逐条检查：

```
□ WHERE/JOIN 列有索引吗？
□ 是否使用了 SELECT * ？（应该只选需要的列）
□ 有没有 N+1 查询？
□ 事务范围是否最小化？
□ 是否使用参数化查询？（禁止字符串拼接）
□ 大表的 DDL 是否使用 CONCURRENTLY？
□ 分页是否使用游标分页而非 OFFSET？
□ 批量操作是否使用了批量语法？
□ 连接池是否配置正确？
□ EXPLAIN ANALYZE 的结果是否符合预期？
```
