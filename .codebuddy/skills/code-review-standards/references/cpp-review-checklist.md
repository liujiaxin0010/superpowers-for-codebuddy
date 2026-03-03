# C/C++ Code Review Checklist

Comprehensive checklist for reviewing C and C++ code, covering memory management, security, performance, and modern C++ best practices.

## Memory Management

### 1. Memory Leaks
```cpp
// ❌ WRONG - Memory leak
void process() {
    int* data = new int[100];
    if (error_condition) {
        return; // Memory leaked!
    }
    delete[] data;
}

// ✅ CORRECT - RAII with smart pointers
void process() {
    auto data = std::make_unique<int[]>(100);
    if (error_condition) {
        return; // Automatically freed
    }
}
```

### 2. Double Free
```cpp
// ❌ WRONG - Double free
void process() {
    int* ptr = new int(42);
    delete ptr;
    // ... more code ...
    delete ptr; // Undefined behavior!
}

// ✅ CORRECT - Set to nullptr after delete
void process() {
    int* ptr = new int(42);
    delete ptr;
    ptr = nullptr;
}

// ✅ BETTER - Use smart pointers
void process() {
    auto ptr = std::make_unique<int>(42);
    ptr.reset(); // Safe, can call multiple times
}
```

### 3. Use After Free
```cpp
// ❌ WRONG - Use after free
int* getData() {
    int* data = new int[10];
    delete[] data;
    return data; // Dangling pointer!
}

// ✅ CORRECT - Return smart pointer
std::unique_ptr<int[]> getData() {
    return std::make_unique<int[]>(10);
}
```

## Buffer Overflow

### 1. Array Bounds
```cpp
// ❌ WRONG - Buffer overflow
void copy(char* dest, const char* src) {
    strcpy(dest, src); // No bounds checking!
}

// ✅ CORRECT - Use safe functions
void copy(char* dest, size_t destSize, const char* src) {
    strncpy(dest, src, destSize - 1);
    dest[destSize - 1] = '\0';
}

// ✅ BETTER - Use std::string
void copy(std::string& dest, const std::string& src) {
    dest = src;
}
```

### 2. Format String Vulnerabilities
```cpp
// ❌ WRONG - Format string attack
void log(const char* userInput) {
    printf(userInput); // User can inject %s, %n
}

// ✅ CORRECT - Use format specifier
void log(const char* userInput) {
    printf("%s", userInput);
}
```

### 3. Integer Overflow
```cpp
// ❌ WRONG - Integer overflow
size_t allocSize = count * sizeof(int); // Can overflow!
int* arr = (int*)malloc(allocSize);

// ✅ CORRECT - Check for overflow
if (count > SIZE_MAX / sizeof(int)) {
    return nullptr; // Would overflow
}
size_t allocSize = count * sizeof(int);
int* arr = (int*)malloc(allocSize);
```

## Modern C++ (C++11/14/17/20)

### 1. Smart Pointers
```cpp
// ❌ WRONG - Raw pointers
class Container {
    Resource* resource;
public:
    Container() : resource(new Resource()) {}
    ~Container() { delete resource; }
};

// ✅ CORRECT - unique_ptr for exclusive ownership
class Container {
    std::unique_ptr<Resource> resource;
public:
    Container() : resource(std::make_unique<Resource>()) {}
    // Destructor automatically handles cleanup
};

// ✅ CORRECT - shared_ptr for shared ownership
class Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> parent; // Avoid circular reference
};
```

### 2. Move Semantics
```cpp
// ❌ WRONG - Unnecessary copy
std::vector<int> createVector() {
    std::vector<int> v = {1, 2, 3};
    return v; // Copy (pre-C++11)
}

// ✅ CORRECT - Move semantics
std::vector<int> createVector() {
    std::vector<int> v = {1, 2, 3};
    return v; // Move (C++11+, NRVO)
}

// ✅ CORRECT - Explicit move
void transfer(std::vector<int>& dest, std::vector<int>& src) {
    dest = std::move(src); // src is now empty
}
```

### 3. Range-based For
```cpp
// ❌ WRONG - Index-based iteration
for (size_t i = 0; i < vec.size(); ++i) {
    process(vec[i]);
}

// ✅ CORRECT - Range-based for
for (const auto& item : vec) {
    process(item);
}

// ✅ CORRECT - With structured bindings (C++17)
for (const auto& [key, value] : map) {
    process(key, value);
}
```

## Concurrency

### 1. Data Races
```cpp
// ❌ WRONG - Data race
int counter = 0;
void increment() {
    counter++; // Not thread-safe
}

// ✅ CORRECT - Mutex
std::mutex mtx;
int counter = 0;
void increment() {
    std::lock_guard<std::mutex> lock(mtx);
    counter++;
}

// ✅ BETTER - Atomic
std::atomic<int> counter{0};
void increment() {
    counter++;
}
```

### 2. Deadlock Prevention
```cpp
// ❌ WRONG - Potential deadlock
void transfer(Account& a, Account& b, int amount) {
    std::lock_guard<std::mutex> lockA(a.mutex);
    std::lock_guard<std::mutex> lockB(b.mutex);
    // If another thread calls transfer(b, a, x) - deadlock!
}

// ✅ CORRECT - std::scoped_lock (C++17)
void transfer(Account& a, Account& b, int amount) {
    std::scoped_lock lock(a.mutex, b.mutex);
    a.balance -= amount;
    b.balance += amount;
}
```

## Resource Management (RAII)

### 1. File Handling
```cpp
// ❌ WRONG - Manual resource management
void readFile(const char* path) {
    FILE* f = fopen(path, "r");
    if (!f) return;
    // ... read file ...
    if (error) return; // File not closed!
    fclose(f);
}

// ✅ CORRECT - RAII with fstream
void readFile(const std::string& path) {
    std::ifstream file(path);
    if (!file) return;
    // File automatically closed when out of scope
}
```

## Performance

### 1. Pass by Reference
```cpp
// ❌ WRONG - Unnecessary copy
void process(std::vector<int> data) { // Copies entire vector
    // ...
}

// ✅ CORRECT - Pass by const reference
void process(const std::vector<int>& data) {
    // ...
}

// ✅ CORRECT - Pass by value for sink parameters
void store(std::string name) { // Will be moved
    this->name = std::move(name);
}
```

### 2. Reserve Capacity
```cpp
// ❌ WRONG - Multiple reallocations
std::vector<int> v;
for (int i = 0; i < 10000; ++i) {
    v.push_back(i);
}

// ✅ CORRECT - Reserve capacity
std::vector<int> v;
v.reserve(10000);
for (int i = 0; i < 10000; ++i) {
    v.push_back(i);
}
```

## Static Analysis Tools

Recommended tools:
- **clang-tidy**: Modern C++ linting
- **cppcheck**: Static analysis
- **Valgrind**: Memory error detection
- **AddressSanitizer**: Runtime memory checking
- **ThreadSanitizer**: Data race detection
- **UndefinedBehaviorSanitizer**: UB detection

Compiler flags:
```bash
# GCC/Clang warnings
-Wall -Wextra -Wpedantic -Werror

# Sanitizers
-fsanitize=address,undefined
```
