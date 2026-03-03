# Rust Code Review Checklist

Comprehensive checklist for reviewing Rust code, covering ownership, lifetimes, error handling, and idiomatic patterns.

## Ownership and Borrowing

### 1. Unnecessary Cloning
```rust
// ❌ WRONG - Unnecessary clone
fn process(data: &Vec<String>) {
    let owned = data.clone(); // Expensive!
    for item in owned {
        println!("{}", item);
    }
}

// ✅ CORRECT - Borrow instead
fn process(data: &[String]) {
    for item in data {
        println!("{}", item);
    }
}
```

### 2. Ownership Transfer
```rust
// ❌ WRONG - Taking ownership when not needed
fn print_length(s: String) {
    println!("{}", s.len());
} // s is dropped, caller loses access

// ✅ CORRECT - Borrow instead
fn print_length(s: &str) {
    println!("{}", s.len());
}
```

### 3. Mutable Borrows
```rust
// ❌ WRONG - Multiple mutable borrows
fn process(data: &mut Vec<i32>) {
    let first = &mut data[0];
    let second = &mut data[1]; // Error!
    *first += *second;
}

// ✅ CORRECT - Split borrow or use indices
fn process(data: &mut Vec<i32>) {
    let second_val = data[1];
    data[0] += second_val;
}
```

## Error Handling

### 1. Unwrap and Expect
```rust
// ❌ WRONG - Panic in production code
fn read_config() -> Config {
    let content = fs::read_to_string("config.toml").unwrap();
    toml::from_str(&content).unwrap()
}

// ✅ CORRECT - Propagate errors
fn read_config() -> Result<Config, Box<dyn Error>> {
    let content = fs::read_to_string("config.toml")?;
    let config = toml::from_str(&content)?;
    Ok(config)
}

// ✅ CORRECT - Use expect with context
fn read_config() -> Config {
    let content = fs::read_to_string("config.toml")
        .expect("config.toml must exist in current directory");
    toml::from_str(&content)
        .expect("config.toml must be valid TOML")
}
```

### 2. Custom Error Types
```rust
// ✅ CORRECT - Using thiserror
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Parse error: {0}")]
    Parse(#[from] serde_json::Error),
    #[error("Invalid input: {message}")]
    InvalidInput { message: String },
}
```

## Concurrency

### 1. Data Races
```rust
// ❌ WRONG - Shared mutable state
use std::thread;

let mut counter = 0;
let handles: Vec<_> = (0..10).map(|_| {
    thread::spawn(|| {
        counter += 1; // Error: cannot borrow
    })
}).collect();

// ✅ CORRECT - Arc + Mutex
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let handles: Vec<_> = (0..10).map(|_| {
    let counter = Arc::clone(&counter);
    thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    })
}).collect();

// ✅ BETTER - Atomic for simple counters
use std::sync::atomic::{AtomicUsize, Ordering};

let counter = Arc::new(AtomicUsize::new(0));
```

### 2. Deadlock Prevention
```rust
// ❌ WRONG - Potential deadlock
fn transfer(a: &Mutex<i32>, b: &Mutex<i32>) {
    let _guard_a = a.lock().unwrap();
    let _guard_b = b.lock().unwrap();
}

// ✅ CORRECT - Consistent lock ordering
fn transfer(a: &Mutex<i32>, b: &Mutex<i32>) {
    let (first, second) = if ptr::addr_of!(a) < ptr::addr_of!(b) {
        (a, b)
    } else {
        (b, a)
    };
    let _guard1 = first.lock().unwrap();
    let _guard2 = second.lock().unwrap();
}
```

## Performance

### 1. Iterator vs Loop
```rust
// ❌ WRONG - Manual loop
let mut sum = 0;
for i in 0..data.len() {
    sum += data[i];
}

// ✅ CORRECT - Iterator (often faster)
let sum: i32 = data.iter().sum();

// ✅ CORRECT - Chained iterators
let result: Vec<_> = data.iter()
    .filter(|x| **x > 0)
    .map(|x| x * 2)
    .collect();
```

### 2. String Operations
```rust
// ❌ WRONG - Multiple allocations
let mut s = String::new();
for word in words {
    s = s + &word + " ";
}

// ✅ CORRECT - Use push_str
let mut s = String::with_capacity(estimated_size);
for word in words {
    s.push_str(&word);
    s.push(' ');
}

// ✅ BETTER - Use join
let s = words.join(" ");
```

## Static Analysis Tools

Recommended tools:
- **clippy**: Linting and best practices
- **rustfmt**: Code formatting
- **cargo-audit**: Security vulnerability scanning
- **miri**: Undefined behavior detection

Commands:
```bash
cargo clippy -- -W clippy::all
cargo fmt --check
cargo audit
```
