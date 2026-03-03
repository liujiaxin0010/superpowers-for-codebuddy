# Java 安全编码规范

> **版本**：V2.0 &nbsp;|&nbsp; **适用范围**：所有基于 Java 语言开发的产品  
> **级别定义**：【规则】必须遵守的强制约定 ·【建议】应加以考虑的推荐约定

---

## 1 输入验证与数据校验

### 1.1 【规则】校验外部传递的不可信数据

所有来自信任边界之外的数据（用户输入、第三方系统、网络请求等），在使用前必须经过服务端校验。客户端校验仅用于提升用户体验，不能替代服务端校验。

**校验策略优先级**：

| 优先级 | 策略 | 说明 |
|--------|------|------|
| 1 | 白名单校验 | 仅接受已知合法字符集，**优先推荐** |
| 2 | 黑名单校验 | 排斥已知非法字符，须持续维护 |

```java
// ✓ 白名单：仅允许字母、数字和下划线
if (!Pattern.matches("^[0-9A-Za-z_]+$", name)) {
    throw new IllegalArgumentException("非法字符");
}
```

### 1.2 【规则】禁止使用不可信数据拼接 SQL

SQL 注入可导致数据泄露、数据篡改甚至远程代码执行。

**防护方案**：

| 方案 | 适用场景 | 优先级 |
|------|----------|--------|
| 参数化查询（`PreparedStatement`） | 所有 JDBC 场景 | **首选** |
| ORM 参数绑定 | Hibernate / MyBatis 等 | 推荐 |
| 存储过程参数化 | 数据库端 | 推荐 |
| 输入过滤 | 上述方案不适用时 | 兜底 |

```java
// ✗ 错误：字符串拼接
String sql = "SELECT * FROM item WHERE name='" + itemName + "'";
stmt.executeQuery(sql);

// ✓ 正确：参数化查询
String sql = "SELECT * FROM item WHERE name=?";
PreparedStatement stmt = conn.prepareStatement(sql);
stmt.setString(1, itemName);
ResultSet rs = stmt.executeQuery();
```

**MyBatis 注意事项**：使用 `#{}` 占位符（参数化），禁止使用 `${}` 直接拼接。

**Hibernate 注意事项**：使用命名参数或位置参数绑定，禁止 HQL/SQL 字符串拼接。

### 1.3 【规则】禁止使用不可信数据拼接 XML

**XML 注入防护**：

- 使用安全的 XML 构建库（如 dom4j 的 `setText()` 方法会自动进行 XML 编码）
- 对输入进行白名单校验，仅允许合法字符

**XXE（XML 外部实体攻击）防护**：

```java
// ✓ 方案一：禁用外部实体解析
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setExpandEntityReferences(false);
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);

// ✓ 方案二：黑名单检测
if (xml.contains("<!DOCTYPE") || xml.contains("<!ENTITY") || xml.contains("SYSTEM")) {
    throw new SecurityException("XML 中包含非法内容");
}
```

### 1.4 【规则】禁止使用不可信数据拼接 HTML 页面

XSS 漏洞允许攻击者注入恶意脚本，窃取用户 Cookie、会话等敏感信息。

**防护方案**：

- 对用户输入进行 HTML 编码后再输出到页面
- 使用安全编码库：`StringEscapeUtils.escapeHtml()` (Apache Commons)
- 实施输入过滤与输出编码双重防护

```java
// ✓ 输出编码
String safe = StringEscapeUtils.escapeHtml(userInput);
```

### 1.5 【规则】禁止直接使用不可信数据记录日志

未经净化的用户输入可能包含换行符，导致日志注入（伪造日志条目）或泄露敏感数据。

```java
// ✗ 错误：直接拼接
logger.severe("Login failed for: " + username);

// ✓ 正确：先校验再记录
if (!Pattern.matches("[A-Za-z0-9_]+", username)) {
    logger.severe("Login failed for unauthorized user");
} else {
    logger.severe("Login failed for: " + username);
}
```

### 1.6 【规则】禁止启用目录浏览权限

在 Apache、Tomcat、Nginx 等服务器配置中，须关闭目录浏览功能，防止目录结构泄露。

### 1.7 【规则】禁止直接解析不可信的文件目录地址

对来自外部的文件路径参数，须校验是否包含 `../` 等目录遍历字符。

```java
String path = req.getParameter("path");
if (path != null && path.trim().contains("../")) {
    request.getRequestDispatcher("error.jsp").forward(request, response);
    return;
}
```

### 1.8 【规则】禁止直接解析不可信的重定向链接

重定向 URL 须校验是否属于本站域名白名单，防止开放重定向钓鱼攻击。

### 1.9 【规则】禁止向 `Runtime.exec()` 传递不可信数据

外部输入传入命令执行函数可导致 OS 命令注入。防护方案：

- **首选**：使用 Java API 替代系统命令（如 `File.list()` 替代 `ls`/`dir`）
- **次选**：白名单校验输入，或将用户选择映射为固定命令
- **兜底**：严格过滤特殊字符（`&`、`|`、`;`、`` ` `` 等）

---

## 2 异常处理

### 2.1 【规则】禁止在异常中泄露敏感信息

异常消息传递到信任边界之外时，须过滤文件路径、堆栈信息等敏感内容。

```java
// ✗ 错误：暴露文件路径
throw new FileNotFoundException(filePath);

// ✓ 正确：返回通用错误信息
System.out.println("Illegal file information!");
```

### 2.2 【规则】通过预检查规避可预防的 RuntimeException

```java
// ✓ 正确
if (obj != null) { obj.method(); }

// ✗ 错误：用 catch 替代检查
try { obj.method(); } catch (NullPointerException e) { ... }
```

### 2.3 【规则】禁止用异常做流程控制

异常机制的开销远高于条件判断，应仅用于处理真正的异常情况。

### 2.4 【规则】`finally` 块须关闭资源，禁止在 `finally` 中 `return`

JDK 7+ 推荐使用 `try-with-resources` 自动关闭资源。`finally` 中的 `return` 会覆盖 `try` 中的返回值，造成逻辑混乱。

### 2.5 【规则】事务场景中异常被 `catch` 后须手动回滚

### 2.6 【建议】防止 NPE 的常见场景

- 基本类型返回值自动拆箱可能产生 NPE
- 数据库查询结果可能为 `null`
- 远程调用返回对象须进行空指针判断
- 避免级联调用 `a.getB().getC()`，推荐使用 `Optional`

---

## 3 IO 操作安全

### 3.1 【规则】临时文件使用完毕须及时删除

临时文件中可能缓存敏感数据，必须在使用后删除，推荐使用 `File.deleteOnExit()` 或 `try-finally` 确保清理。

### 3.2 【规则】避免在共享目录操作文件

在 `/tmp` 等全局可写目录创建文件须使用唯一文件名和严格权限控制，防止符号链接攻击。

### 3.3 【规则】严格控制文件上传

- 校验文件类型（基于 Magic Number 而非扩展名）
- 限制文件大小
- 存储到非 Web 可访问目录
- 重命名上传文件

### 3.4 【规则】安全地从 `ZipInputStream` 提取文件

- 检查解压后的文件路径是否包含 `../`，防止 Zip Slip 漏洞
- 检查解压后的总大小，防止 Zip Bomb（压缩炸弹）
- 限制条目数量

```java
ZipEntry entry = zis.getNextEntry();
String name = entry.getName();
if (name.contains("..")) {
    throw new SecurityException("Path traversal detected");
}
File destFile = new File(destDir, name);
if (!destFile.getCanonicalPath().startsWith(destDir.getCanonicalPath())) {
    throw new SecurityException("Path traversal detected");
}
```

---

## 4 序列化安全

### 4.1 【规则】禁止序列化未加密的敏感数据

包含敏感字段的类须将敏感字段声明为 `transient`，或在序列化前进行加密。

### 4.2 【规则】防止反序列化被利用来绕过安全管理

- 不要反序列化不可信来源的数据
- 使用白名单过滤可反序列化的类（`ObjectInputFilter`，JDK 9+）
- 考虑使用 JSON/Protobuf 等替代 Java 原生序列化

---

## 5 平台与运行时安全

### 5.1 【规则】不要信任环境变量的值

环境变量可被攻击者控制，使用前须进行校验。

### 5.2 【规则】生产代码禁止包含调试入口和后门

任何调试代码、硬编码的测试账号、绕过认证的入口在发布前须全部移除。

### 5.3 【规则】用户鉴别信息须加密后传输

口令、令牌等认证信息必须通过 HTTPS/TLS 加密通道传输，禁止明文传输。

### 5.4 【规则】多线程中必须对共享资源进行同步操作

使用 `synchronized`、`ReentrantLock`、`ConcurrentHashMap` 等机制保护共享状态。

---

## 6 敏感数据保护

### 6.1 【规则】禁止在日志中保存口令、密钥等敏感信息

包括明文和密文形式的口令、密钥均不得出现在日志中。

### 6.2 【规则】口令存储须使用加盐哈希

使用 `BCrypt`、`SCrypt` 或 `PBKDF2` 进行口令哈希存储，禁止使用 MD5/SHA1。

### 6.3 【规则】禁止将敏感信息硬编码

数据库密码、API 密钥、加密密钥等须通过安全的配置管理系统获取。

### 6.4 【规则】使用强随机数

安全场景（令牌生成、密钥生成、验证码等）须使用 `java.security.SecureRandom`，禁止使用 `java.util.Random` 或 `Math.random()`。

---

## 7 Web 安全规约

### 7.1 【规则】实施权限控制校验

用户个人页面和功能须进行水平与垂直权限校验，防止未授权访问。

### 7.2 【规则】用户敏感数据须脱敏展示

手机号、身份证号、银行卡号等个人信息须部分隐藏后再展示。

### 7.3 【规则】表单和 AJAX 提交须执行 CSRF 验证

使用 CSRF Token 机制防止跨站请求伪造攻击。

### 7.4 【规则】外部重定向须执行白名单过滤

### 7.5 【规则】用户输入的 SQL 参数须使用参数绑定

禁止字符串拼接 SQL 访问数据库。

---

## 8 日志规约

### 8.1 【规则】使用日志门面框架（SLF4J / JCL）

禁止直接使用 Log4j / Logback API，应通过门面模式统一日志接口。

### 8.2 【规则】日志输出使用占位符方式

```java
// ✓ 正确：占位符
logger.debug("Processing trade id: {} symbol: {}", id, symbol);

// ✗ 错误：字符串拼接
logger.debug("Processing trade id: " + id + " symbol: " + symbol);
```

### 8.3 【规则】trace/debug/info 级别日志须进行级别判断

```java
if (logger.isDebugEnabled()) {
    logger.debug("Current ID: {} name: {}", id, getName());
}
```

### 8.4 【规则】生产环境禁止使用 `System.out` / `e.printStackTrace()`

### 8.5 【规则】异常日志须包含现场信息和堆栈信息

```java
logger.error("inputParams:{} errorMessage:{}", params, e.getMessage(), e);
```

### 8.6 【规则】日志配置须设置 `additivity=false` 避免重复打印

---

## 9 代码检查

### 9.1 【规则】所有 Java 代码须通过 FindBugs/SpotBugs 检查，消除所有告警

### 9.2 【规则】所有 Java 代码须通过 CheckStyle 检查，使用产品线指定的配置文件

---

## 参考文献

- CERT Oracle Secure Coding Standard for Java (SEI CERT)
- OWASP Top 10
- CWE/SANS Top 25
- 《Java 开发手册》嵩山版
