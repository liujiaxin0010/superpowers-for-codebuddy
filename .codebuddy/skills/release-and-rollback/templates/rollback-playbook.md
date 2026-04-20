# Rollback Playbook - <feature/version>

> 路径：`docs/runbooks/<feature>-rollback.md`

## 1. 元信息

- 关联发布版本：
- 关联 release notes：
- 关联 spec / plan：
- Owner：
- 最近一次演练日期：
- 最近一次演练结果：

## 2. 回滚目标

- 回到哪个已知好版本：
- 回滚范围（代码 / 数据 / 配置 / 资源）：
- 回滚不包含的内容：

## 3. 快照点

| 对象 | 标识（commit / tag / snapshot-id） | 位置 | 有效期 |
|---|---|---|---|
| 代码 | | | |
| 数据库 | | | |
| 配置 | | | |
| 资源 | | | |

## 4. 前置条件

- [ ] 快照点仍有效
- [ ] 依赖服务版本兼容
- [ ] 通知链已就位
- [ ] 值守人已到岗
- [ ] Boss 已签字（真实回滚必备）

## 5. 回滚步骤（dry-run 与真实执行共用）

```bash
# 步骤 1
<command>
# 步骤 2
<command>
# 步骤 3
<command>
```

每一步的验证方式：

- 步骤 1 验证：
- 步骤 2 验证：
- 步骤 3 验证：

## 6. RTO / RPO

- 预估 RTO（从决策到恢复）：
- 预估 RPO（最多丢失多少数据）：
- 超出该值时的升级路径：

## 7. 演练记录

| 日期 | 环境 | 执行者 | 结果 | 发现问题 |
|---|---|---|---|---|
| | | | | |

## 8. 真实回滚执行记录

> 每次真实回滚必须新建一份 `docs/runbooks/<feature>-rollback-<YYYYMMDD-HHmm>.md`

- Boss 签字原文：
- 触发原因：
- 开始时间：
- 结束时间：
- 实际 RTO：
- 实际 RPO：
- 事后复盘：`docs/findings.md#<anchor>`
