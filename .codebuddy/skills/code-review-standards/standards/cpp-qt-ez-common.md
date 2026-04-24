# C++/Qt EZ 系列通用编码规范（共享正文）

> 适用 EZStation / EZTools 等 EZ 系列 Qt 产品的**共同部分**。日志部分在 variant 专用文件中。
> 未覆盖的条目沿用官方 Qt 规范。

## 1. 文件与目录

- 文件名小写 + 下划线，如 `ez_websocket.cpp` / `ez_websocket.h`
- 每个 `.h` 必须有 `#ifndef ... #define ... #endif` 头文件保护宏（大写 + 下划线，前后加 `_`）
- 头文件示例：

```cpp
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

- 实现文件示例：

```cpp
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
- 控制语句关键词后加空格：`if (cond)` / `for (int i = 0; ...)`

## 3. 命名规范

| 类型 | 规则 | 示例 |
|---|---|---|
| 类 | `C` + 大驼峰 | `CImageProcessor` |
| 结构体 | `typedef struct tagXxx{} XXX_S` | `typedef struct tagServerCfgImport{} SERVERCFG_IMPORT_S` |
| 枚举 | `typedef enum tagXxx{} XXX_E` | `typedef enum tagMouseSection{} MOUSE_SECTION_E` |
| 公共方法 | 大驼峰 | `ConnectToHost()` |
| 保护 / 私有方法 / 普通函数 | 小驼峰 | `processFrame()` |
| 临时变量 | 小驼峰 | `frameCount` |
| 成员变量 - 整型 | `m_l` + 大驼峰 | `m_lReconnectAttempts` |
| 成员变量 - 浮点 | `m_f` + 大驼峰 | `m_fTemperature` |
| 成员变量 - 类类型 | `m_o` + 大驼峰 | `m_oMessageQueue` |
| 成员变量 - 字符串 | `m_str` + 大驼峰 | `m_strName` |
| 成员变量 - 指针 | `m_p` + 大驼峰 | `m_pInstance` |
| 成员变量 - 其他 | `m_` + 大驼峰 | `m_BufferSize` |
| 宏 | 全大写 + 下划线 | `DEBUG_LOG` |

## 4. 注释（硬约束）

- **严格禁止 `//` 注释**，无论单行多行、任何位置
- **一律使用 `/* */`**，即使只有一行
- 多行注释必须整段包在 `/* */` 内，禁止混用
- 头文件函数声明后追加 `/* 功能说明 */` 行尾注释
- 示例：

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

    if (input == nullptr || output == nullptr)
    {
        lRet = ERROR_COMMON_FAILED;
    }

    return (lRet == ERROR_COMMON_SUCCEED);
}
```

- ❌ 禁止：`InitModel(); // 刷新视图`、`int a = 1; // 这是变量a`
- ✅ 允许：`InitModel(); /* 刷新视图 */`、`int a = 1; /* 这是变量a */`

## 5. Qt 信号与槽

- 信号定义在头文件 `signals:` 区，以 `sig` + 大驼峰命名：`void sigConnected();`
- 槽函数在头文件相应区，以 `slot` + 大驼峰命名：`void slotConnected();`
- 发送信号使用 `emit` 关键字，**禁用 `Q_EMIT`**
- 连接使用**函数指针形式**，**禁用 `SIGNAL()` / `SLOT()` 宏**

```cpp
connect(m_pWebSocket, &QWebSocket::connected, this, &CWebSocket::slotConnected);
emit sigDeviceListReceived(data);
```

## 6. 比较运算符（Yoda 风格）

- 常量 / 字面量 / 枚举放在比较运算符**左边**，变量放在**右边**
- 目的：防止 `==` 误写成 `=`

```cpp
/* ✅ */
if (MAX_VALUE > lValue)
if (TRUE == bCondition)
if (EN_VIEW_USERDEFINE_LOCAL == enCurViewType)
if (0 != lResult)

/* ❌ */
if (lValue < MAX_VALUE)
if (bCondition == TRUE)
if (enCurViewType == EN_VIEW_USERDEFINE_LOCAL)
if (lResult != 0)
```

## 7. 审查清单（用于 `/code-review` / `/code-self-check`）

- [ ] `.h` 是否有正确的 `#ifndef _XXX_H / #define / #endif`
- [ ] 缩进是否全部 4 空格（无 Tab）
- [ ] 成员变量前缀是否匹配类型（`m_l/m_f/m_o/m_str/m_p/m_`）
- [ ] 类名是否 `C` 前缀 + 大驼峰；public 方法是否大驼峰
- [ ] 是否出现 `//` 注释（除自动生成 / 第三方）→ BLOCKED
- [ ] 信号是否 `sig` 前缀；槽是否 `slot` 前缀
- [ ] 是否存在 `Q_EMIT` / `SIGNAL()` / `SLOT()` 宏 → BLOCKED
- [ ] 比较运算符是否 Yoda 风格（常量在左）
