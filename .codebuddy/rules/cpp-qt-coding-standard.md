---
trigger: cpp_qt_review
alwaysApply: false
appliesTo: ["*.cpp", "*.h", "*.hpp", "*.c", "*.cxx", "*.hxx", "*.ui", "*.qrc", "*.pro"]
---

# C++/Qt 编码规范（EZStation / EZTools 通用）

> 本规范用于指导 EZStation、EZTools 两个 Qt 项目在生成/补全 C++ 代码、以及 `cpp-qt-code-reviewer-skill` 进行代码审查时的行为。请严格遵守以下规则，未涉及的部分严格遵守 Qt 官方规范。
>
> **日志章节按项目分两个变体（5.1 EZStation / 5.2 EZTools），其余章节两个项目共享。**

## 1. 文件与目录

- 文件名：小写 + 下划线，如 `ez_websocket.cpp`

- 头文件扩展名，每个 `.h` 必须包含 **`#ifndef .. #endif`**，参考代码如下：

  ```C++
  #ifndef _EZ_WEBSOCKET_H
  #define _EZ_WEBSOCKET_H

  #include <QObject>
  #include <QWebSocket>
  #include <QTimer>

  class CWebSocket : public QObject
  {
    Q_OBJECT
  public:
    CWebSocket(QObject *Obj = nullptr);
    ~CWebSocket();

    void ConnectToServer(const QUrl &url);      /* 连接 */

  protected slots:
    void slotConnected();
  signals:
    void sigConnected();

  private:
    QWebSocket *m_pWebSocket;
    QTimer *m_pReconnectTimer;
  };

  #endif
  ```

- 实现文件参考代码如下：

  ```c++
  #include "ez_websocket.h"
  #include "common_log.h"

  #define  RECONNECT_INTERVAL  30000

  CWebSocket::CWebSocket(QObject *parent) :
    QObject(parent),
    m_pWebSocket(nullptr),
    m_pReconnectTimer(nullptr)
  {
    m_pWebSocket = new QWebSocket();

    /* 连接信号 */
    connect(m_pWebSocket, &QWebSocket::connected, this, &CWebSocket::slotConnected);
  }

  CWebSocket::~CWebSocket()
  {
    if (m_pWebSocket)
    {
        m_pWebSocket->close();
        delete m_pWebSocket;
        m_pWebSocket = nullptr;
    }
  }

  /*
  * @brief 连接到服务器
  * @param[in] url 服务器URL
  */
  void CWebSocket::ConnectToServer(const QUrl &url)
  {
    if (m_pWebSocket->state() != QAbstractSocket::UnconnectedState)
    {
        m_pWebSocket->close();
    }

    m_pWebSocket->open(url);
  }
  ```

## 2. 缩进与空格

- 使用 **4 个空格** 缩进（禁止 Tab）
- 运算符两侧加空格：`int a = b + c;`
- 函数参数逗号后加空格：`func(a, b, c)`
- 控制语句关键词后加空格：`if (cond)`、`for (int i = 0; ...)`

## 3. 命名规范

| 类型                       | 规则                                                         | 示例                                                      |
| -------------------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| 类                         | 类以 `C` 开头 + 大驼峰（PascalCase）                          | `CImageProcessor`                                         |
| 结构体                     | 以 `typedef` + `tag` + 大驼峰（PascalCase），别名为全大写 + 下划线 + `_S` 结尾 | `typedef struct tagServerCfgImport{} SERVERCFG_IMPORT_S` |
| 枚举                       | 以 `typedef` + `tag` + 大驼峰（PascalCase），别名为全大写 + 下划线 + `_E` 结尾 | `typedef enum tagMouseSection{} MOUSE_SECTION_E`          |
| 公共方法                   | 大驼峰（PascalCase）                                         | `ConnectToHost()`                                         |
| 保护方法/私有方法/普通函数 | 小驼峰（camelCase）                                          | `processFrame()`                                          |
| 临时变量                   | 小驼峰                                                       | `frameCount`                                              |
| 普通成员变量 - 整型        | 以 `m_l` 开头 + 大驼峰（PascalCase）                          | `m_lReconnectAttempts`                                    |
| 普通成员变量 - 浮点型      | 以 `m_f` 开头 + 大驼峰（PascalCase）                          | `m_fTemperature`                                          |
| 普通成员变量 - 类类型      | 以 `m_o` 开头 + 大驼峰（PascalCase）                          | `m_oMessageQueue`                                         |
| 普通成员变量 - 字符串      | 以 `m_str` 开头 + 大驼峰（PascalCase）                        | `m_strName`                                               |
| 普通成员变量 - 其他类型    | 以 `m_` 开头 + 大驼峰（PascalCase）                           | `m_BufferSize`                                            |
| 普通成员变量 - 指针类型    | 以 `m_p` 开头 + 大驼峰（PascalCase）                          | `m_pInstance`                                             |
| 宏                         | 全大写 + 下划线                                              | `DEBUG_LOG`                                               |

## 4. 注释

- **严格禁止使用 `//` 注释**，无论在任何位置、任何上下文。
- **所有注释必须使用 `/* */` 格式**，即使只有一行。
- **多行注释也必须用 `/* */` 包裹**，不能混合使用。
- **示例**：

  ```cpp
  /*
  * @brief 对输入图像进行去雾处理
  * @param input 原始图像指针
  * @param output 输出图像指针
  * @return true 成功，false 失败
  */
  bool Defog(const Image* input, Image* output)
  {
      /* 初始化参数 */
      int lRet = ERROR_COMMON_SUCCEED;

      /* 调用核心算法 */
      if (input == nullptr || output == nullptr)
      {
          lRet = ERROR_COMMON_FAILED;
      }

      return (lRet == ERROR_COMMON_SUCCEED);
  }
  ```

- 头文件中的函数声明后面，增加注释函数功能，参考如下：

  ```c++
  bool Defog(const Image* input, Image* output);   /* 对输入图像进行去雾处理 */
  ```

- 禁止以下写法（错误示例）：

  ```c++
  InitModel(); // 刷新视图        ❌ 不允许
  int a = 1; // 这是变量a         ❌ 不允许
  ```

- 正确写法（必须使用 `/* */`）：

  ```c++
  InitModel(); /* 刷新视图 */     ✅ 允许
  int a = 1; /* 这是变量a */       ✅ 允许
  ```

## 5. 日志输出

> 本章按项目分变体。`cpp-qt-code-reviewer-skill` 在审查时根据项目路径关键字（`ezstation` / `eztools`，大小写不敏感）自动选用对应小节作为日志规范。

### 5.1 EZStation 项目（使用 `LOG_MESSAGE` 宏）

- 格式：`LOG_MESSAGE(日志等级, 日志内容);`

- 日志等级定义如下：

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

- 示例：

  ```cpp
  LOG_MESSAGE(EN_LOG_LEVEL_INFO, QString("Device %1 TCP connected, ActiveCount:%2, WaitingCount:%3")
                                           .arg(oTask.m_lDevId)
                                           .arg(m_oActiveTaskMap.size())
                                           .arg(m_oWaitingQueue.size()));
  LOG_MESSAGE(EN_LOG_LEVEL_ERROR, QString("Failed to create TCP client for device %1").arg(oTask.m_lDevId));
  ```

### 5.2 EZTools 项目（使用 `LOG_RECORD` 宏）

- 格式：`LOG_RECORD(日志等级, 日志内容);`

- 日志等级定义如下：

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

- 示例：

  ```cpp
  LOG_RECORD(LOG_LEVEL_INFO, "WebSocket connected successfully, URL: %1");
  LOG_RECORD(LOG_LEVEL_ERROR, QString("WebSocket error: %1, error code: %2").arg(m_pWebSocket->errorString()).arg(error));
  ```

### 5.3 通用约束（两个项目均适用）

- 日志使用规范：
  - `DEBUG`：调试信息，用于开发阶段输出详细流程信息
  - `INFO`：普通信息，用于输出正常运行时的关键流程信息
  - `WARNING`：警告信息，用于输出不影响程序运行但需要注意的情况
  - `ERROR`：错误信息，用于输出影响程序正常运行的错误
  - `FATAL`：致命错误，用于输出导致程序无法继续运行的严重错误
- 日志内容必须使用英文，便于国际化和统一维护
- 不允许残留 `console` / `print` / `qDebug` / `std::cout` 等直接控制台输出

## 6. Qt 信号与槽

- 信号定义：在头文件中的 `signals:` 区域定义信号，命名规范：以 `sig` 开头 + 大驼峰（PascalCase），参考如下：

  ```c++
  void sigConnected();
  ```

- 发送信号：在实现中使用 `emit` 关键字发送信号，而不是 `Q_EMIT` 宏

  ```cpp
  emit deviceListReceived(data);
  ```

- 槽函数定义：在头文件中定义槽函数的命名规范：以 `slot` 开头 + 大驼峰（PascalCase），参考如下：

  ```cpp
  void slotConnected();
  ```

- 信号和槽的绑定方式：以函数指针的形式绑定，禁止使用 `SIGNAL` 和 `SLOT` 宏，参考如下：

  ```c++
  connect(m_pWebSocket, &QWebSocket::connected, this, &CWebSocket::slotConnected);
  ```

## 7. 比较运算符规范

- **比较运算符优先顺序**：将明确的值（常量、字面量、枚举）放在比较运算符的左边，将变量放在比较运算符的右边
- **优点**：避免意外赋值（防止将 `==` 误写成 `=`），提高代码可读性和安全性
- **示例**：

  ```cpp
  /* 正确写法 - 将常量放在左边 */
  if (MAX_VALUE > lValue)           /* ✅ 允许 */
  if (TRUE == bCondition)           /* ✅ 允许 */
  if (EN_VIEW_USERDEFINE_LOCAL == enCurViewType)  /* ✅ 允许 */
  if (0 != lResult)                 /* ✅ 允许 */

  /* 错误写法 - 将变量放在左边 */
  if (lValue < MAX_VALUE)           /* ❌ 不允许 */
  if (bCondition == TRUE)           /* ❌ 不允许 */
  if (enCurViewType == EN_VIEW_USERDEFINE_LOCAL)  /* ❌ 不允许 */
  if (lResult != 0)                 /* ❌ 不允许 */
  ```
