# `.codebuddy/state/`

存放跨会话/跨命令共享的状态文件。**必须纳入版本控制**，避免协作者重复全量索引或重置基线。

## 当前文件

| 文件 | 用途 | 维护者 |
|---|---|---|
| `gitnexus-baseline.json` | GitNexus 索引基线 commit + 时间 + 范围；详见 `.codebuddy/rules/gitnexus-code-intelligence.md` 模式 G | `/extend` `/code-review` `/code-self-check` 等命令在进入主体前自动维护 |

## 字段示例

```json
{
  "lastIndexedCommit": "abc1234",
  "indexedAt": "2026-04-17T06:00:00Z",
  "scope": ["src/", "internal/"],
  "excludedDirs": ["node_modules/", "vendor/", "dist/"],
  "gitnexusVersion": "x.y.z",
  "lastDelta": {
    "filesAdded": 0,
    "filesModified": 0,
    "filesDeleted": 0,
    "riskLevel": "low"
  }
}
```

文件不存在时，第一次进入受影响命令的 AI 必须创建空模板并触发一次全量 `npx gitnexus analyze`，然后写回真实基线。
