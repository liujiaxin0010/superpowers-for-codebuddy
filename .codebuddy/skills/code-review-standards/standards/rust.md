# Rust 安全编码规范

> **版本**：V1.0 &nbsp;|&nbsp; **适用范围**：所有基于 Rust 语言开发的产品
> **级别定义**：【规则】必须遵守的强制约定 ·【建议】应加以考虑的推荐约定

---

## 1 所有权与借用

### 1.1 【规则】优先借用而非克隆

不必要的 `clone()` 浪费内存和 CPU。

```rust
// ✗ 错误：不必要的克隆
fn process(data: &Vec<String>) {
    let copy = data.clone();
    for item in &copy { /* ... */ }
}

// ✓ 正确：直接借用
fn process(data: &[String]) {
    for item in data { /* ... */ }
}
```

### 1.2 【规则】函数参数优先使用切片引用而非 `&Vec<T>`

```rust
// ✗ 不推荐
fn sum(nums: &Vec<i32>) -> i32

// ✓ 推荐：更通用
fn sum(nums: &[i32]) -> i32
```

### 1.3 【规则】可变借用须最小化作用域

```rust
// ✗ 错误：可变借用范围过大
let mut data = vec![1, 2, 3];
let r = &mut data;
// ... 大量不需要 r 的代码 ...
r.push(4);

// ✓ 正确：缩小作用域
let mut data = vec![1, 2, 3];
data.push(4);
```

---

## 2 错误处理

### 2.1 【规则】生产代码禁止使用 `unwrap()` 和 `expect()`

```rust
// ✗ 错误：panic 风险
let value = map.get("key").unwrap();

// ✓ 正确：优雅处理
let value = map.get("key").ok_or(MyError::KeyNotFound)?;
```

### 2.2 【规则】自定义错误类型须实现 `std::error::Error`

推荐使用 `thiserror` 或 `anyhow` 简化错误处理。

```rust
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("数据库错误: {0}")]
    Database(#[from] sqlx::Error),
    #[error("未找到: {0}")]
    NotFound(String),
}
```

### 2.3 【规则】使用 `?` 操作符传播错误，避免嵌套 `match`

---

## 3 并发安全

### 3.1 【规则】跨线程共享可变状态须使用 `Arc<Mutex<T>>`

```rust
// ✓ 正确
let shared = Arc::new(Mutex::new(HashMap::new()));
let clone = Arc::clone(&shared);
thread::spawn(move || {
    let mut map = clone.lock().unwrap();
    map.insert("key", "value");
});
```

### 3.2 【规则】避免在持有锁时执行耗时操作

```rust
// ✗ 错误：持锁时间过长
let mut guard = mutex.lock().unwrap();
let result = expensive_network_call(); // 阻塞其他线程
guard.insert(key, result);

// ✓ 正确：先计算再加锁
let result = expensive_network_call();
let mut guard = mutex.lock().unwrap();
guard.insert(key, result);
```

### 3.3 【建议】无锁场景优先使用 `std::sync::atomic`

---

## 4 内存安全

### 4.1 【规则】禁止在 `unsafe` 块中进行未经验证的指针解引用

```rust
// ✗ 错误
unsafe { *ptr }

// ✓ 正确：先验证
if !ptr.is_null() {
    unsafe { *ptr }
}
```

### 4.2 【规则】最小化 `unsafe` 代码范围

`unsafe` 块须尽可能小，并附带安全性说明注释。

### 4.3 【规则】`Vec` 预分配容量避免频繁重新分配

```rust
// ✗ 不推荐
let mut v = Vec::new();
for i in 0..1000 { v.push(i); }

// ✓ 推荐
let mut v = Vec::with_capacity(1000);
for i in 0..1000 { v.push(i); }
```

---

## 5 性能

### 5.1 【建议】优先使用迭代器而非手动循环

```rust
// ✗ 不推荐
let mut sum = 0;
for i in &numbers { sum += i; }

// ✓ 推荐
let sum: i32 = numbers.iter().sum();
```

### 5.2 【建议】字符串拼接使用 `String::with_capacity` 或 `format!`

```rust
// ✗ 不推荐：多次重新分配
let mut s = String::new();
for item in items { s += &item.to_string(); }

// ✓ 推荐
let s: String = items.iter().map(|i| i.to_string()).collect();
```

### 5.3 【建议】使用 `Cow<str>` 避免不必要的字符串分配

---

## 6 安全性

### 6.1 【规则】SQL 查询须使用参数化绑定

```rust
// ✗ 错误
let q = format!("SELECT * FROM users WHERE name = '{}'", name);

// ✓ 正确（sqlx）
sqlx::query("SELECT * FROM users WHERE name = $1")
    .bind(&name)
    .fetch_one(&pool).await?;
```

### 6.2 【规则】禁止硬编码密钥和凭证

### 6.3 【规则】反序列化外部数据须设置大小限制

---

## 7 工程化

### 7.1 【规则】代码提交前须通过以下工具检查

| 工具 | 用途 |
|------|------|
| `cargo fmt` | 代码格式化 |
| `cargo clippy` | Lint 检查 |
| `cargo test` | 单元测试 |
| `cargo audit` | 依赖安全审计 |

### 7.2 【规则】公共 API 须编写文档注释（`///`）

### 7.3 【规则】使用 `#[must_use]` 标注不应忽略返回值的函数

---

## 参考文献

- Rust API Guidelines (https://rust-lang.github.io/api-guidelines/)
- Rust Clippy Lints (https://rust-lang.github.io/rust-clippy/)
