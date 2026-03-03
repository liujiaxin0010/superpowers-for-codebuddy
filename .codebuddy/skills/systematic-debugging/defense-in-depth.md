# 纵深防御验证（Defense in Depth）

本文档是 `systematic-debugger` 子代理的辅助材料，提供多层验证方法论确保修复的完整性。

---

## 核心思想：一次修复，多层验证

修复一个 bug 就像修补一艘船——你不只修补一层船壳，而是在多个层面建立防线。每一层独立工作，即使某一层失效，其他层仍然能捕获问题。

```
第一层：输入校验（在源头拦截非法数据）
第二层：业务逻辑防御（计算过程中检测异常值）
第三层：输出校验（返回结果前验证合理性）
第四层：监控告警（生产环境中持续检测）
```

---

## 四层防御模型

### 第一层：输入边界防御

在数据进入系统的**最早位置**进行校验：

```java
// API 入口层
public OrderResponse createOrder(@Valid @RequestBody OrderRequest req) {
    // 1. 参数格式校验（由框架自动完成）
    // 2. 业务规则校验
    if (req.getAmount() <= 0) {
        throw new BusinessException("订单金额必须大于0");
    }
    if (req.getAmount() > MAX_ORDER_AMOUNT) {
        throw new BusinessException("订单金额超出上限");
    }
    // 3. 权限校验
    if (!currentUser.canCreateOrder()) {
        throw new ForbiddenException("无权创建订单");
    }
}
```

**原则**：永远不信任外部输入。来自用户、第三方 API、消息队列的数据都必须校验。

### 第二层：业务逻辑防御

在核心计算过程中添加断言和不变量检查：

```python
def calculate_discount(amount, rate):
    # 前置条件
    assert amount >= 0, f"金额不能为负: {amount}"
    assert 0 <= rate <= 1, f"折扣率必须在0-1之间: {rate}"

    discount = amount * rate

    # 后置条件
    assert 0 <= discount <= amount, f"折扣额异常: {discount}"
    return discount
```

**原则**：关键业务计算的输入输出都要有断言。断言是给开发者看的"在这里不可能出错"的声明——如果出错了，说明有更深层的问题。

### 第三层：输出完整性防御

在数据离开系统之前做最后一次检查：

```java
// 返回给前端之前
public OrderVO toVO(Order order) {
    OrderVO vo = new OrderVO();
    vo.setFinalAmount(order.getFinalAmount());

    // 输出防御：最终金额不可能为负
    if (vo.getFinalAmount() < 0) {
        log.error("订单{}最终金额为负: {}", order.getId(), vo.getFinalAmount());
        throw new SystemException("数据异常，请联系管理员");
    }
    return vo;
}
```

### 第四层：运行时监控防御

在生产环境中持续检测异常模式：

```yaml
# Prometheus 告警规则
- alert: NegativeOrderAmount
  expr: order_final_amount < 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "检测到负数订单金额"
```

---

## 修复验证检查清单

修复 bug 后，按以下清单验证：

```
□ 修复是否解决了根因（而非只是掩盖症状）？
□ 修复是否包含了输入校验（第一层防御）？
□ 修复是否包含了业务断言（第二层防御）？
□ 相关的单元测试是否已添加/更新？
□ 是否添加了回归测试（确保此 bug 不再复发）？
□ 是否检查了相似代码路径（同一类 bug 可能出现在多处）？
□ 是否需要修复历史脏数据？
□ 是否需要添加监控告警？
□ 修复是否影响了其他功能？（运行全量测试）
□ 修复是否需要通知 Boss 关注后续？
```

---

## 常见的修复不完整模式

| 不完整模式 | 风险 | 补全方式 |
|---|---|---|
| 只修了一处，相似逻辑还有多处 | 同类 bug 再次出现 | grep 全局搜索相似代码 |
| 只修了代码，没清理脏数据 | 历史数据仍然导致错误 | 编写数据修复脚本 |
| 只加了修复，没加测试 | 未来重构可能打回原样 | 必须添加回归测试 |
| 只修了症状层，没修根因层 | 其他路径仍然产生同样问题 | 使用根因追溯找到真正源头 |
