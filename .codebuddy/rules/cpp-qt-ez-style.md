---
alwaysApply: true
---

# C++/Qt EZ 系列风格（按需触发；未命中完全静默）

> 常驻规则，但**仅触发器**。正文按需从 `.codebuddy/skills/code-review-standards/standards/` 加载。

## 触发条件（两项全满足才激活）

1. 目标仓库存在 `*.cpp` / `*.h` / `*.pro` / `CMakeLists.txt` 且命中 Qt 关键字
   （`QObject` / `Q_OBJECT` / `signals:` / `slots:`）
2. 变体指纹二选一：
   - **station**：`rg -q "LOG_MESSAGE\s*\(|EN_LOG_LEVEL_"` 命中
   - **tools**：`rg -q "LOG_RECORD\s*\(|\bLOG_LEVEL_(DEBUG|INFO|WARNING|ERROR|FATAL)\b"` 命中
3. **两者皆未命中 → `variant=none`，本规则立即静默退出：不提示、不 ASK、不加载任何正文**

## 命中后

1. 记录到 file-based-memory：`cppQtProductVariant = station | tools`
2. 当 `/execute-plan`、`/fix-bug`、`/extend`、`/simplify`、`/code-review`、`/code-self-check` 任一触发时：
   - 加载 `.codebuddy/skills/code-review-standards/standards/cpp-qt-ez-common.md`
   - 加载 `.codebuddy/skills/code-review-standards/standards/cpp-qt-ez-logging-{variant}.md`
   - 违反共同规范或对应日志规范 → BLOCKED

## 仲裁

- 若两个指纹同时命中（混合仓 / 迁移中）→ 以 `EN_LOG_LEVEL_` 优先判为 station
- 首次激活或 variant 切换时，在 `docs/progress.md` 记录一行：`cppQtProductVariant=<variant> source=<探测命令命中位置>`
