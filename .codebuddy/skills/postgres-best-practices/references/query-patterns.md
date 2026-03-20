# PostgreSQL 查询与调优示例

本文件只在需要**具体 SQL 写法**时读取。主 `SKILL.md` 已提供决策规则，本文件提供典型例子。

## 缺失索引

```sql
-- 慢：高频过滤列无索引
SELECT * FROM orders WHERE customer_id = 123;

-- 优化
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

## 低效 JOIN 与 N+1

```sql
-- 慢：应用层循环查
for order in orders:
    customer = db.query("SELECT * FROM customers WHERE id = %s", order.customer_id)

-- 优化：一次 JOIN
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending';
```

## SELECT *

```sql
-- 慢：无差别取列
SELECT * FROM orders WHERE status = 'pending';

-- 优化：只取需要列
SELECT id, amount, created_at
FROM orders
WHERE status = 'pending';
```

## Keyset Pagination

```sql
-- 慢：大页码 OFFSET
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- 优化：游标分页
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;
```

## 数据类型

```sql
-- 差
CREATE TABLE orders (id TEXT PRIMARY KEY, amount FLOAT);

-- 优化
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  amount NUMERIC(12,2)
);
```

## 在线 DDL

```sql
-- 大表风险较高
CREATE INDEX idx_orders_email ON orders(email);

-- 更稳
CREATE INDEX CONCURRENTLY idx_orders_email ON orders(email);
```

## 长事务与死锁

```sql
-- 差：事务范围过大
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- 中间夹杂大量其他动作
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

```sql
-- 更稳：缩短事务并统一加锁顺序
BEGIN;
SELECT * FROM accounts WHERE id IN (1, 2) ORDER BY id FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

## RLS 策略

```sql
-- 差：子查询使策略复杂且不利于索引
CREATE POLICY user_access ON orders
FOR SELECT USING (
  user_id = (SELECT id FROM users WHERE email = current_setting('app.user_email'))
);

-- 优化：直接使用会话变量
CREATE POLICY user_access ON orders
FOR SELECT USING (
  user_id = current_setting('app.user_id')::uuid
);
```

## 参数化查询

```sql
-- 差
query = f"SELECT * FROM users WHERE name = '{user_input}'"

-- 优化
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```
