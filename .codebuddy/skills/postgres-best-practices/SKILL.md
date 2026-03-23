---
name: postgres-best-practices
description: PostgreSQL 设计、查询与调优技能。用于在编写 SQL、设计表结构、排查慢查询、处理锁争用、配置连接池、执行线上 DDL 或编写 RLS 策略时做诊断、决策与审查。用户提到“Postgres/PostgreSQL/索引/慢查询/RLS/连接池/SQL 优化/EXPLAIN”时触发。
---

# Postgres SQL 最佳实践

本技能用于帮助 AI 在 PostgreSQL 场景里做**正确的技术判断**，而不是机械背诵一堆 SQL 示例。

## 何时使用

以下场景必须使用：

1. 编写或审查 PostgreSQL SQL
2. 设计表结构、索引、分页、批量写入
3. 排查慢查询、锁争用、长事务
4. 设计或优化 RLS 策略
5. 配置连接池或线上 DDL

## 资源加载规则

当需要先做问题分诊、判断慢查询/锁/连接/RLS/线上 DDL 各自最小证据时，再读取：

- `references/problem-triage-matrix.md`

当需要看具体 SQL 例子、索引/锁/RLS 写法时，再读取：

- `references/query-patterns.md`

当需要输出诊断结论、审查摘要或改造建议时，再读取：

- `templates/postgres-review-summary.md`

不要一开始就把整份示例文件读进上下文，先根据当前问题判断属于哪个类别。

## 何时不用

1. 数据库不是 PostgreSQL
2. 问题只停留在 ORM 用法，不涉及 PostgreSQL 特性
3. 用户要的是通用 SQL 教程，而不是 PostgreSQL 场景决策

## 阻断条件

只有在用户要求“给出明确根因或明确线上操作建议”时，出现以下情况才返回 `BLOCKED`：

1. 慢查询没有 `EXPLAIN ANALYZE`
2. 线上 DDL 没有表规模、流量窗口或回退思路
3. 锁争用 / 死锁没有阻塞链或事务边界信息
4. RLS 问题没有策略文本或会话变量上下文

## 诊断协议

1. 先分问题类型：
   - 查询慢
   - 写入 / 事务慢
   - 锁争用 / 死锁
   - RLS / 安全
   - 表结构 / 数据类型
   - 连接池 / 线上 DDL

2. 再看最小证据：
   - 查询慢先看 `EXPLAIN ANALYZE`
   - 锁问题先看事务边界和阻塞链
   - RLS 先看策略文本和会话变量
   - 线上 DDL 先看流量窗口与回退方案

3. 再做 PostgreSQL 特有判断：
   - 慢查询：索引、`SELECT *`、`OFFSET`、N+1
   - 表结构：`UUID` 不用 `TEXT`，金额不用 `FLOAT`
   - 锁问题：事务长短、加锁顺序、`CONCURRENTLY`
   - RLS：避免复杂子查询，保留索引思维
   - 连接池：先怀疑连接管理而不是盲调 `max_connections`

## 审查清单

编写或审查 SQL 时，至少检查：

1. `WHERE/JOIN/ORDER BY` 列是否有合理索引
2. 是否误用 `SELECT *`
3. 是否存在 N+1
4. 事务范围是否过大
5. 是否使用参数化查询
6. 大表 DDL 是否考虑 `CONCURRENTLY`
7. 分页是否误用 `OFFSET`
8. 批量操作是否仍逐条执行
9. RLS 是否破坏索引利用
10. 连接池与超时是否有基本边界

## 高风险反模式

1. 金额用 `FLOAT`：会引入精度误差
2. UUID 用 `TEXT`：会丢失类型约束并增加转换成本
3. 大页码分页继续用 `OFFSET`：页码越大越慢
4. 在应用层循环发 SQL：极易演化成 N+1
5. 大表 DDL 不考虑 `CONCURRENTLY`：容易阻塞线上写入
6. RLS 策略里嵌复杂子查询：会拖慢查询且不利于索引
7. 依赖字符串拼接构造 SQL：既有注入风险，也破坏参数化

## 禁止事项

1. 不要在没有 `EXPLAIN ANALYZE` 的情况下拍脑袋说“索引有问题”
2. 不要把所有列都加索引当成优化
3. 不要把 PostgreSQL 当成通用 SQL，不考虑其锁、RLS、连接特性
4. 不要忽略事务边界，只盯单条 SQL
5. 不要为了示例好看而复制大段无关 SQL
