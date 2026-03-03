# Go 安全编码规范

> **版本**：V2.0 &nbsp;|&nbsp; **适用范围**：所有基于 Go 语言开发的产品  
> **级别定义**：【规则】必须遵守的强制约定 ·【建议】应加以考虑的推荐约定

---

## 1 工程化要求

### 1.1 【规则】代码提交前须通过以下工具检查

| 工具 | 用途 |
|------|------|
| `gofmt` | 代码格式化 |
| `goimports` | 导入检查与格式化 |
| `golint` / `golangci-lint` | 代码规范检查 |
| `go vet` | 静态分析 |

### 1.2 【规则】包导入规范

- 按组分块：标准库 → 第三方包 → 内部包，组间空行分隔
- 只导入使用到的包
- 禁止使用相对路径导入和 Import Dot（`.`）
- 包名不匹配导入路径末段时须使用别名

---

## 2 内存安全

### 2.1 【规则】操作 Slice 前必须判断长度是否合法

未检查长度直接访问索引会导致 `index out of range` panic。

```go
// ✗ 错误
func decode(data []byte) bool {
    if data[0] == 'F' && data[1] == 'U' { ... }
}

// ✓ 正确
func decode(data []byte) bool {
    if len(data) >= 6 {
        if data[0] == 'F' && data[1] == 'U' { ... }
    }
    return false
}
```

### 2.2 【规则】指针操作前必须判断是否为 nil

尤其在进行结构体 `Unmarshal` 后，嵌套指针可能为 `nil`。

```go
if packet.Data == nil {
    return
}
fmt.Printf("Stat: %v\n", packet.Data.Stat)
```

### 2.3 【规则】数字运算须做长度限制

- 确保无符号整数运算不会反转
- 确保有符号整数运算不会溢出
- 确保整型转换不会截断或产生符号错误

```go
func overflow(num int32) {
    result := num + 1
    if result < 0 {
        fmt.Println("integer overflow")
        return
    }
}
```

### 2.4 【规则】用于数组索引、对象长度、循环边界的外部值须严格校验

### 2.5 【规则】`make` 分配内存时须校验外部可控的长度参数

```go
// ✗ 错误：未校验外部长度
buffer := make([]byte, lenControlByUser)

// ✓ 正确：限制长度范围
if size > 64*1024*1024 {
    return nil, errors.New("value too large")
}
buffer := make([]byte, size)
```

### 2.6 【规则】禁止重复释放 Channel

使用 `defer close(c)` 统一管理 Channel 关闭，避免在多个分支中重复调用 `close`。

### 2.7 【规则】确保每个 Goroutine 都能退出

无退出条件的 Goroutine 会导致内存泄漏。

### 2.8 【建议】不使用 `unsafe` 包

`unsafe` 绕过 Go 内存安全机制，可能导致内存破坏。若必须使用，须做好安全校验。

---

## 3 并发安全

### 3.1 【规则】禁止在闭包中直接使用循环变量

多个 Goroutine 共享同一循环变量会产生数据竞争。

```go
// ✗ 错误
for i := 0; i < 5; i++ {
    go func() {
        fmt.Println(i)  // 不是预期值
    }()
}

// ✓ 正确：显式传参
for i := 0; i < 5; i++ {
    go func(j int) {
        fmt.Println(j)
    }(i)
}
```

### 3.2 【规则】禁止并发写 Map，须加锁保护

并发写 Map 会导致程序崩溃（`fatal error: concurrent map writes`）。使用 `sync.Mutex`、`sync.RWMutex` 或 `sync.Map` 保护。

### 3.3 【规则】通过同步锁共享内存

任何 `Lock()` / `RLock()` 均须有对应的 `Unlock()` / `RUnlock()`，推荐使用 `defer` 确保释放。

### 3.4 【规则】使用 `sync/atomic` 执行原子操作

对简单计数器等场景，原子操作比互斥锁性能更好。

### 3.5 【规则】Map 和 Slice 作为参数或返回值时注意深拷贝

Map 和 Slice 是引用类型，函数内外共享同一底层数据。须根据场景决定是否进行深拷贝。

```go
// ✓ 深拷贝防止外部修改影响内部状态
func (d *Driver) SetTrips(trips []Trip) {
    d.trips = make([]Trip, len(trips))
    copy(d.trips, trips)
}
```

### 3.6 【规则】不再使用的 `time.Ticker` 须调用 `Stop()` 释放

`time.Timer` 会被 GC 回收，但 `time.Ticker` 不会，须手动停止。

---

## 4 SQL 操作

### 4.1 【规则】使用参数化查询，禁止拼接 SQL

```go
// ✗ 错误
q := fmt.Sprintf("SELECT * FROM product WHERE category='%s'",
    req.URL.Query()["category"])
db.Query(q)

// ✓ 正确
q := "SELECT * FROM product WHERE category=?"
db.Query(q, req.URL.Query()["category"])
```

---

## 5 文件操作

### 5.1 【规则】路径穿越检查

对外部传入的文件路径须验证是否包含 `../` 等路径遍历字符，防止任意文件读取/写入。

```go
// ✓ 检查压缩文件名防止路径穿越
for _, f := range r.File {
    if strings.Contains(f.Name, "..") {
        return false  // 拒绝
    }
    p, _ := filepath.Abs(f.Name)
    ioutil.WriteFile(p, data, 0640)
}
```

### 5.2 【规则】创建文件须设置访问权限

```go
// 设置合理的文件权限
ioutil.WriteFile(path, data, 0640)  // -rw-r-----
```

---

## 6 系统命令

### 6.1 【规则】`exec.Command` 的 path 参数须白名单限定

直接使用外部输入作为可执行命令路径时，必须限定可执行命令的白名单范围。

### 6.2 【规则】通过 shell 执行命令时须过滤恶意字符

通过 `sh -c` 拼接外部输入时，须过滤 `\n`、`$`、`&`、`;`、`|`、`'`、`"`、`` ` ``、`(`、`)` 等危险字符。

```go
func checkIllegal(cmd string) bool {
    dangerous := []string{"&", "|", ";", "$", "'", "`", "(", ")", "\""}
    for _, ch := range dangerous {
        if strings.Contains(cmd, ch) {
            return true
        }
    }
    return false
}
```

---

## 7 敏感数据保护

### 7.1 【规则】实施访问控制

系统默认须进行身份认证，仅通过白名单放开不需要认证的接口。按照最小权限原则设置不同级别的资源访问权限。

### 7.2 【规则】敏感数据输出原则

- 仅输出必要的最小数据集
- 禁止在日志中保存密码（明文/密文）和密钥
- 必须输出的敏感信息须脱敏展示
- 避免通过 GET 参数、代码注释、缓存泄露敏感信息

### 7.3 【规则】敏感数据存储须加密

使用 SHA-256、RSA、AES 等算法加密存储。包含敏感信息的临时文件和缓存不再需要时须立刻删除。

### 7.4 【规则】禁止硬编码密码/密钥

```go
// ✗ 错误
const password = "s3cretp4ssword"

// ✓ 正确：通过配置或密钥管理系统获取
password := os.Getenv("DB_PASSWORD")
```

### 7.5 【建议】禁止使用弱加密算法

禁用 `crypto/des`、`crypto/md5`、`crypto/sha1`、`crypto/rc4`。推荐使用 `crypto/aes`、`crypto/rsa`。

---

## 8 通信安全

### 8.1 【规则】会话管理

- 用户登录时须重新生成 Session
- 退出登录后须清理 Session
- Cookie 须设置 `HttpOnly`、`Secure`、`Expires` 属性

### 8.2 【规则】涉及敏感操作的接口须添加 CSRF Token

### 8.3 【规则】XML 解析须防止 XXE 攻击

使用标准库 `encoding/xml`（不支持外部实体引用，天然防御 XXE）。

### 8.4 【规则】外部输入参数须使用 Validator 校验

推荐使用 `go-playground/validator` 进行白名单校验，校验数据长度、范围、类型与格式。

### 8.5 【建议】无法白名单校验的须进行 HTML 转义

使用 `html.EscapeString`、`text/template` 或 `bluemonday` 过滤 `<`、`>`、`&`、`'`、`"` 等字符。

### 8.6 【规则】响应头 Content-Type 须与实际内容一致

### 8.7 【建议】添加安全响应头

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY / SAMEORIGIN`

### 8.8 【建议】外部通信须使用 TLS

推荐 TLS 1.3。须启用证书验证，禁止 `InsecureSkipVerify: true`。

```go
// ✗ 错误
TLSClientConfig: &tls.Config{InsecureSkipVerify: true}

// ✓ 正确
TLSClientConfig: &tls.Config{InsecureSkipVerify: false}
```

### 8.9 【规则】CORS 须严格限制请求来源

```go
cors.New(cors.Options{
    AllowedOrigins:   []string{"https://example.com"},
    AllowCredentials: true,
})
```

---

## 9 错误处理

### 9.1 【规则】函数返回的 `error` 必须检查

禁止使用 `_` 丢弃任何 `error`。不处理则须向上层 return 或记录日志。

### 9.2 【规则】尽早 return err

遇到错误立即返回，减少正常逻辑的嵌套深度。

```go
// ✓ 推荐
if err != nil {
    return err
}
// normal code

// ✗ 不推荐
if err != nil {
    // error handling
} else {
    // normal code
}
```

### 9.3 【规则】禁止将 `panic` 用于正常错误处理

`panic` 仅用于不可恢复的致命错误（如无法打开数据库连接导致程序无法运行）。

### 9.4 【规则】类型断言须使用 "comma, ok" 模式

```go
str, ok := value.(string)
if !ok {
    // 处理类型不匹配
}
```

### 9.5 【规则】检查切片是否为空用 `len(s) == 0`，而非 `s == nil`

---

## 10 单元测试

### 10.1 【规则】单元测试覆盖率须达到 80% 以上

### 10.2 【规则】测试文件与业务代码同目录，以 `_test.go` 为后缀

### 10.3 【规则】每个重要函数须同步编写测试用例，随业务代码一同提交

---

## 参考文献

- Effective Go (https://golang.org/doc/effective_go.html)
- Go Code Review Comments (https://github.com/golang/go/wiki/codereviewcomments)
- 腾讯 Go 安全指南
