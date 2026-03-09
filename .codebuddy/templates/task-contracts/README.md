# devflow-ai Task Contracts

任务合同（Task Contract）是 `devflow-ai` 的统一任务边界层。

它的作用不是把 prompt 写长，而是把任务写成可复用、可验证、可审查的执行合同，连接：

1. 上游需求与规格
2. 下游计划与执行
3. 验证证据与 review 收口

## 最小字段

所有合同模板都至少包含以下字段：

- `任务目标`
- `范围边界`
- `允许修改`
- `禁止修改`
- `验证命令`
- `交付物`
- `交付证据`
- `人工确认点`
- `owner`
- `超边界时如何处理`

## 模板映射

| 任务类型 | 模板 | 默认入口 |
|---|---|---|
| `new-feature` | `new-feature.md` | `/spec-lite -> /write-plan -> /execute-plan` |
| `bugfix` | `bugfix.md` | `/fix-bug` |
| `refactor` | `refactor.md` | `/write-plan -> /execute-plan -> /simplify` |
| `test` | `test.md` | `/test-gen` 或 `/unified-test` |
| `research` | `research.md` | `/research` |
| `review-pr` | `review-pr.md` | `/code-review` + `/code-self-check` |
| `issue-draft-pr` | `issue-draft-pr.md` | `/issue-draft-pr` |
| `parallel-delivery` | `parallel-delivery.md` | `/parallel-delivery` |

## 使用方式

1. 先按任务类型选择模板
2. 再把模板压缩成 agent 可执行合同
3. 合同字段缺失时，不进入执行阶段
4. 验证失败或任务越界时，回退到上游合同或规格修订
