# 回归测试合同（Regression Test Contract）

> 用途：在修复代码 *之前*，先提交一个能稳定证明 bug 存在的失败测试。修复完成后该测试应由红转绿。
> 位置：`docs/specs/YYYY-MM-DD-<bug-id>-regression-test.md`
> 前置：`bugfix` TaskContract 已确认；复现步骤清晰。

---

## 1. 元信息

- 关联工单：
- 关联 bugfix contract：`.codebuddy/templates/task-contracts/bugfix.md`
- 作者：
- 创建时间：
- 对应 commit（首次失败证据）：

## 2. 失败测试声明

- 测试文件：`path/to/test_file`
- 测试用例 ID / 函数名：
- 测试类型：`unit | integration | e2e | contract`
- 运行命令（单独执行该用例）：
  ```
  $ <cmd>
  ```
- 首次失败的完整输出（修复前证据）：
  ```
  <stderr / stack trace / assertion diff>
  ```
- 退出码：

## 3. 断言与 bug 的对应关系

| 断言 | 证明的业务不变量 | 对应问题单字段 |
|---|---|---|
| | | 期望行为 §x |

## 4. 稳定性自证

- 连续运行 3 次均失败的输出摘要：
- 不依赖机器本地状态（时间、环境变量、外部网络）的说明：
- 如有不可避免的外部依赖，Mock / Fixture 方案：

## 5. 修复后预期

- 预期断言转为通过
- 预期不会破坏的其他用例清单（回归保命集）：
- 预期运行时长变化（秒）：

## 6. 合入策略

- **本测试用例必须与修复代码在同一 PR 内合入**，不允许"先合修复再补测试"
- 测试文件纳入长期回归集，禁止在后续清理中删除
