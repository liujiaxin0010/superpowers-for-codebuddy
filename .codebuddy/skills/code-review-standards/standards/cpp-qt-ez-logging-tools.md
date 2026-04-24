# EZTools 日志规范（variant = tools）

> 仅在 `cppQtProductVariant=tools` 时加载。共同部分见 `cpp-qt-ez-common.md`。

## 1. 日志宏

- 统一使用 `LOG_RECORD` 宏：`LOG_RECORD(日志等级, 日志内容);`

## 2. 日志等级枚举

```cpp
typedef enum tagLogLevel
{
    LOG_LEVEL_DEBUG   = 1,            /* DEBUG   */
    LOG_LEVEL_INFO    = 2,            /* INFO    */
    LOG_LEVEL_WARNING = 3,            /* WARNING */
    LOG_LEVEL_ERROR   = 4,            /* ERROR   */
    LOG_LEVEL_FATAL   = 5             /* FATAL   */
} LOGLEVEL_E;
```

## 3. 等级选用

- `LOG_LEVEL_DEBUG`：开发阶段的详细流程信息
- `LOG_LEVEL_INFO`：正常运行的关键流程
- `LOG_LEVEL_WARNING`：不影响运行但需关注
- `LOG_LEVEL_ERROR`：影响正常运行的错误
- `LOG_LEVEL_FATAL`：导致无法继续运行的致命错误

## 4. 内容规范

- **日志正文一律使用英文**（便于国际化与统一维护）
- 变参使用 `QString("...").arg(...)` 拼装

## 5. 示例

```cpp
LOG_RECORD(LOG_LEVEL_INFO, "WebSocket connected successfully");
LOG_RECORD(LOG_LEVEL_ERROR, QString("WebSocket error: %1, error code: %2")
                                .arg(m_pWebSocket->errorString())
                                .arg(error));
```

## 6. 审查要点（硬门禁）

- [ ] 是否使用 `LOG_RECORD` 而非 `LOG_MESSAGE` / `qDebug` / `std::cout` / `printf`
- [ ] 日志等级是否使用 `LOG_LEVEL_*` 枚举常量（注意**没有** `EN_` 前缀）
- [ ] 日志正文是否英文
- [ ] 是否在日志中残留中文 / 敏感信息（口令、token、密钥、证件号）
