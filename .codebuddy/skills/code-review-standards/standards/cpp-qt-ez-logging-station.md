# EZStation 日志规范（variant = station）

> 仅在 `cppQtProductVariant=station` 时加载。共同部分见 `cpp-qt-ez-common.md`。

## 1. 日志宏

- 统一使用 `LOG_MESSAGE` 宏：`LOG_MESSAGE(日志等级, 日志内容);`

## 2. 日志等级枚举

```cpp
typedef enum tagLogLevel
{
    EN_LOG_LEVEL_NOLOG   = 0,          /* 不打印  */
    EN_LOG_LEVEL_DEBUG   = 1,          /* DEBUG   */
    EN_LOG_LEVEL_INFO    = 2,          /* INFO    */
    EN_LOG_LEVEL_WARNING = 3,          /* WARNING */
    EN_LOG_LEVEL_ERROR   = 4,          /* ERROR   */
    EN_LOG_LEVEL_FATAL   = 5           /* FATAL   */
} LOGLEVEL_E;
```

## 3. 等级选用

- `EN_LOG_LEVEL_NOLOG`：完全不打印
- `EN_LOG_LEVEL_DEBUG`：开发阶段的详细流程信息
- `EN_LOG_LEVEL_INFO`：正常运行的关键流程
- `EN_LOG_LEVEL_WARNING`：不影响运行但需关注
- `EN_LOG_LEVEL_ERROR`：影响正常运行的错误
- `EN_LOG_LEVEL_FATAL`：导致无法继续运行的致命错误

## 4. 内容规范

- **日志正文一律使用英文**（便于国际化与统一维护）
- 变参使用 `QString("...").arg(...)` 拼装

## 5. 示例

```cpp
LOG_MESSAGE(EN_LOG_LEVEL_INFO, QString("Device %1 TCP connected, ActiveCount:%2, WaitingCount:%3")
                                   .arg(oTask.m_lDevId)
                                   .arg(m_oActiveTaskMap.size())
                                   .arg(m_oWaitingQueue.size()));
LOG_MESSAGE(EN_LOG_LEVEL_ERROR, QString("Failed to create TCP client for device %1").arg(oTask.m_lDevId));
```

## 6. 审查要点（硬门禁）

- [ ] 是否使用 `LOG_MESSAGE` 而非 `LOG_RECORD` / `qDebug` / `std::cout` / `printf`
- [ ] 日志等级是否使用 `EN_LOG_LEVEL_*` 枚举常量
- [ ] 日志正文是否英文
- [ ] 是否在日志中残留中文 / 敏感信息（口令、token、密钥、证件号）
