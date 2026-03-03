# 覆盖率提升策略（前后端通用）

## 目标

分支覆盖率 ≥ 80%。达标即停，不过度追求 100%。

## 通用策略（前后端一致）

### 策略1: 优先覆盖错误分支

**最高效的覆盖率提升手段。**

大多数函数的未覆盖代码集中在错误处理分支（`if err != nil` / `catch(error)`）。
通过 Mock 返回错误即可触发这些分支：

| 语言 | 方法 |
|------|------|
| Go | `m.On("Method").Return(nil, errors.New("mock error")).Maybe()` |
| Vue | `mockAction.mockRejectedValueOnce(new Error("mock error"))` |

### 策略2: 覆盖条件分支的所有路径

对于 if/else、switch/case、三元表达式，确保每个分支至少有一个测试用例：

| 条件类型 | 需要的用例数 |
|---------|------------|
| `if (a)` | 2 个（a=true, a=false） |
| `if (a && b)` | 3 个（全true, a=false, b=false） |
| `switch (x)` | 每个 case 1个 + default 1个 |

### 策略3: 覆盖边界条件

| 边界类型 | 测试要点 |
|---------|---------|
| 空值 | null / nil / undefined / 空字符串 / 空数组 |
| 零值 | 0 / false / 空对象 |
| 上限 | 最大值、数组满、超出范围 |
| 类型边界 | 类型转换、parseInt 失败 |

### 策略4: 覆盖异步分支

| 场景 | 前端做法 | 后端做法 |
|------|---------|---------|
| Promise 成功 | `mockResolvedValue` | Mock 返回 (result, nil) |
| Promise 失败 | `mockRejectedValue` | Mock 返回 (nil, error) |
| 超时 | `jest.useFakeTimers()` | `context.WithTimeout` |
| 并发 | `await flushPromises()` | `time.Sleep` / channel |

## 前端特有策略 (Vue/Jest)

### 策略5: 覆盖生命周期钩子

```javascript
// mounted 中的异步调用
test("mounted 应该调用初始化方法", async () => {
  const wrapper = createWrapper();
  await flushPromises();
  expect(mockActions.init).toHaveBeenCalled();
});
```

### 策略6: 覆盖 computed 属性

```javascript
test("计算属性应该正确计算", async () => {
  await wrapper.setData({ items: [1, 2, 3] });
  expect(wrapper.vm.totalCount).toBe(3);
});
```

### 策略7: 覆盖 watch 侦听器

```javascript
test("watch 应该响应数据变化", async () => {
  await wrapper.setData({ searchKeyword: "new value" });
  await wrapper.vm.$nextTick();
  // 验证 watch 触发的副作用
});
```

### 策略8: 覆盖事件处理

```javascript
test("点击按钮应该触发方法", async () => {
  await wrapper.find('.submit-btn').trigger('click');
  expect(wrapper.emitted('submit')).toBeTruthy();
});
```

## 后端特有策略 (Go)

### 策略9: 覆盖数据库操作分支

```go
// Mock 数据库返回 RecordNotFound
m.On("SelectByID", mock.Anything).Return(nil, gorm.ErrRecordNotFound).Maybe()

// Mock 数据库返回其他错误
m.On("SelectByID", mock.Anything).Return(nil, errors.New("connection refused")).Maybe()
```

### 策略10: 覆盖全局变量条件

```go
// 测试全局开关为 true 的分支
{
    name: "test with CloudUse enabled",
    setupMock: func(m *MockDaoMgr, u *MockUpService) {
        global.CloudUse = true
        // ... 其他 mock
    },
    afterTest: func() {
        global.CloudUse = false  // 恢复
    },
},

// 测试全局开关为 false 的分支
{
    name: "test with CloudUse disabled",
    setupMock: func(m *MockDaoMgr, u *MockUpService) {
        global.CloudUse = false
        // ... 其他 mock
    },
},
```

### 策略11: 覆盖事务回滚分支

```go
// 测试事务中某步失败导致回滚
{
    name: "test rollback when CreatePark fails",
    setupMock: func(m *MockDaoMgr, u *MockUpService) {
        m.On("GetDB").Return(nil).Maybe()
        m.On("CreatePark", mock.Anything, mock.Anything).
            Return(0, errors.New("insert failed")).Maybe()
    },
    expectErr: errors.New("insert failed"),
},
```

## 迭代改进检查表

每轮迭代后检查：

- [ ] 所有 `if err != nil` 分支都有对应的错误用例？
- [ ] 所有 `if/else` 的两个分支都被覆盖？
- [ ] 所有 `switch/case` 都有对应用例？
- [ ] 空值/零值/边界条件都被测试？
- [ ] 异步成功和失败路径都被覆盖？
- [ ] 全局变量/配置开关的不同值都被测试？

## 何时停止

- ✅ 分支覆盖率 ≥ 80% → **立即停止**
- ⚠️ 连续两轮无提升 → 停止，当前已是合理最大值
- ⚠️ 无法生成新用例 → 停止
- ❌ 不要为了追求 100% 而写无意义的测试
