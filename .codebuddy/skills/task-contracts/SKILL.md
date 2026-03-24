---
name: task-contracts
description: 统一任务合同技能。用于根据任务类型选择合同模板，补齐目标、边界、验证、证据、owner 与超边界处理，并将模板压缩成 agent 可执行合同摘要。用户提到"生成合同/task contract/任务边界/补齐合同/定义验收标准/合同模板/明确修改范围"时触发。
---

# 任务合同（Task Contracts）

把任务从“聊天描述”收敛成“可执行合同”。

## 何时使用

- 需要把需求压缩成稳定输入时
- 需要在 spec / plan / execute / review 之间共享同一套边界时
- 需要明确可编辑位置、验证命令、交付证据与 owner 时
- 任何使用 `.codebuddy/templates/task-contracts/*.md` 的场景

## 合同最小字段

必须至少包含：

1. `任务目标`
2. `范围边界`
3. `允许修改`
4. `禁止修改`
5. `验证命令`
6. `交付物`
7. `交付证据`
8. `人工确认点`
9. `owner`
10. `超边界时如何处理`

## 好合同 vs 坏合同

| 字段 | 坏合同 | 好合同 |
|---|---|---|
| 任务目标 | "优化性能" | "将 /api/users 响应时间从 800ms 降至 200ms 以下" |
| 允许修改 | "相关文件" | "src/api/users.ts, src/db/queries/users.sql" |
| 验证命令 | "跑测试" | "npm test -- --grep users && curl -w '%{time_total}' /api/users" |
| 交付证据 | "测试通过" | "测试输出截图 + 响应时间对比（优化前 vs 后）" |
| 超边界处理 | 未填 | "若需改 DB schema，暂停并升级给 owner" |

## 常见合同失败模式

1. **目标含糊**：写"改善用户体验"而不是具体指标——导致无法判断是否完成
2. **边界缺失**：不写 `forbiddenPaths`——子代理可能改动共享契约
3. **验证命令是伪命令**：`echo "done"` 不是验证——验证必须能检测失败
4. **TBD 透传**：合同里有 `TBD` 就分发——子代理会自行脑补需求

## 执行流程

1. 先识别任务类型——**若任务类型不明确，必须先读取 `references/task-types.md`，确认类型后再继续**
2. 选择对应模板
3. 补齐最小字段
4. 检查是否存在 `TBD/待定/未确认`——有 TBD 必须阻断
5. 将模板压缩为 agent 合同摘要——**压缩前必须读取 `references/compression-checklist.md`，逐项核查后再输出**
6. 若缺少关键字段，则阻断并回退上游规格或人工确认

## 模板与任务类型映射

- `new-feature` -> `../../templates/task-contracts/new-feature.md`
- `bugfix` -> `../../templates/task-contracts/bugfix.md`
- `refactor` -> `../../templates/task-contracts/refactor.md`
- `test` -> `../../templates/task-contracts/test.md`
- `research` -> `../../templates/task-contracts/research.md`
- `review-pr` -> `../../templates/task-contracts/review-pr.md`
- `issue-draft-pr` -> `../../templates/task-contracts/issue-draft-pr.md`
- `parallel-delivery` -> `../../templates/task-contracts/parallel-delivery.md`

## 阻断条件

出现以下任一情况时，返回 `BLOCKED`：

1. 任务目标写不出可验证的完成定义
2. 合同中存在 `TBD/待定/未确认` 且无法当场补齐
3. 缺少 owner 或 owner 无法做超边界决策
4. 验证命令不能真正检测失败（如 `echo done`）

## 禁止事项

1. 不要把含糊目标直接写进合同——"优化"不是目标，"将 X 从 A 降到 B"才是
2. 不要省略 `forbiddenPaths`——没有禁区的合同等于授权子代理改任何文件
3. 不要带着 TBD 分发合同——TBD 会被子代理用自己的假设填充
4. 不要把合同当成沟通记录——合同是可执行的边界约束，不是聊天纪要
5. 不要在合同中写实现方案——合同定义 WHAT 和边界，不定义 HOW

