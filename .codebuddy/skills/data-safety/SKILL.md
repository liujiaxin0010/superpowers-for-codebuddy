---
name: data-safety
description: 数据安全技能。用于在触达生产数据 / 共享存储 / 表结构的操作（迁移、批量 UPDATE/DELETE、TRUNCATE/DROP、索引重建、rm -rf、kubectl delete）进入执行前，产出"行数预估 + 备份快照 + dry-run + 回滚脚本"四件套并取得 Boss 签字。用户提到"数据迁移 / 批量更新 / 批量删除 / schema 变更 / 索引重建 / 在生产跑 SQL"时触发。
---

# 数据安全

回答的核心问题：**这次数据操作一旦跑错，还能否把数据恢复？代价是什么？**

是 CODEBUDDY 第 4 条铁律的执行层。**铁律不是建议**：任何命中触发条件的操作必须先过本门禁。

## 触发条件（命中任一即必须执行）

1. 数据库 DDL：`CREATE / ALTER / DROP / TRUNCATE`
2. 数据库 DML 且影响行数估计 ≥ 1000 或条件不带唯一键
3. 生产 / staging 环境执行任意 SQL
4. `rm -rf` / `find -delete` / `git clean -fdx` / `xargs rm`
5. `kubectl delete` / `terraform destroy` / 任何 IaC 销毁动作
6. 对象存储批量删除 / 覆盖写（S3 / OSS / COS）
7. 消息队列 purge / topic 删除
8. 索引重建、分片迁移、数据迁移脚本
9. 涉及生产数据的脱敏 / 回灌 / 复制

## 何时不用

1. 本地开发数据库、内存测试、临时容器内的操作
2. CI 沙盒内可抛弃的测试数据
3. 只读查询

## 阻断条件（BLOCKED）

1. 缺少"四件套"中的任一项
2. Boss 未显式签字确认
3. 触发条件 #5-#7 在非维护窗口 / 无人值守时

## 输入参数

`/data-safety-check operation=<描述> [env=prod|staging|dev] [rows=<估计>] [planPath=<path>]`

## 四件套（硬要求）

### 1. 行数 / 作用域预估

- 原始统计 SQL / 命令（必须是只读的 count / dry-run）：
  ```sql
  SELECT COUNT(*) FROM <table> WHERE <same-condition>;
  ```
- 预估行数 / 文件数 / 对象数：
- 上下界：最小 / 最大可能影响面
- 与业务约束是否一致（如"清理 30 天前日志"预估不应超出日志总量 1/X）

### 2. 备份 / 快照

- 快照方式：`mysqldump` / `pg_dump` / `xtrabackup` / `volume snapshot` / 对象存储版本
- 快照存储位置与保留时长：
- 快照验证：能否从快照恢复出一张完整表 / 一个完整目录（必须演练一次）
- 快照标识（commit / tag / snapshot-id）：

### 3. dry-run 证据

- dry-run 命令（必须不造成副作用）：
  ```
  BEGIN;
  <real-statement>;
  ROLLBACK;
  ```
  或
  ```
  rsync --dry-run ...
  kubectl delete ... --dry-run=client -o yaml
  ```
- dry-run 输出（片段）：
- 与预估值偏差是否在可接受范围：

### 4. 回滚脚本

- 回滚命令 / SQL（文件路径）：
- 回滚 RTO / RPO 预估：
- 回滚前必须具备的前置条件（如"24 小时内"、"保留了 binlog"）：
- 回滚演练结果：已在 staging 跑通 / 尚未演练（未演练必须 Boss 显式接受）

## 窗口与人员

- 允许执行的窗口：
- 通知方：
- 变更单号：
- 值守人员：
- 终止条件（告警触发、慢查询暴增、错误率 > X）：

## 输出

报告：`docs/plans/YYYY-MM-DD-<op-name>-data-safety.md`（基于本模板填写）
签字记录：Boss 确认语录原文 + 时间戳写入 `docs/progress.md`

## 与执行命令的耦合

- `/execute-plan` 命中触发条件时必须先存在本报告并状态=已签字
- `/release` 若包含数据迁移，必须在"pre-release checklist"里引用本报告
- `/rollback` 复用本报告中的回滚脚本与 RTO/RPO

## 禁止事项

1. 禁止用"我知道自己在做什么"跳过四件套——生产事故几乎都来自"这次例外一下"
2. 禁止用演示库 / staging 的 dry-run 替代生产 dry-run（schema / 数据分布可能不同）
3. 禁止回滚脚本与正向脚本在同一次 PR 内都缺测试
4. 禁止把备份存放到将被本次操作波及的位置
5. 禁止在 Boss 未签字时执行——即便"时间紧急"
