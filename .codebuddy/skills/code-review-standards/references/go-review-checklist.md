# Go Code Review Checklist

Comprehensive checklist for reviewing Go code, covering common pitfalls, best practices, and idiomatic patterns.

## Concurrency Issues

### 1. Goroutine Loop Variable Capture
```go
// ❌ WRONG - All goroutines reference the same variable
for _, item := range items {
    go func() {
        process(item) // Bug: 'item' is captured by reference
    }()
}

// ✅ CORRECT - Pass as parameter
for _, item := range items {
    go func(i Item) {
        process(i)
    }(item)
}

// ✅ CORRECT - Create local copy
for _, item := range items {
    item := item
    go func() {
        process(item)
    }()
}
```

### 2. Race Conditions
```go
// ❌ WRONG - Data race
type Counter struct {
    count int
}
func (c *Counter) Inc() { c.count++ }

// ✅ CORRECT - Use mutex
type Counter struct {
    mu    sync.Mutex
    count int
}
func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

// ✅ BETTER - Use atomic operations
type Counter struct {
    count atomic.Int64
}
func (c *Counter) Inc() { c.count.Add(1) }
```

### 3. Channel Deadlocks
```go
// ❌ WRONG - Unbuffered channel can deadlock
ch := make(chan int)
ch <- 1 // Blocks forever if no receiver

// ✅ CORRECT - Use buffered channel or goroutine
ch := make(chan int, 1)
ch <- 1

// ✅ CORRECT - Send in goroutine
ch := make(chan int)
go func() { ch <- 1 }()
```

### 4. WaitGroup Misuse
```go
// ❌ WRONG - Copying WaitGroup
func process(wg sync.WaitGroup) { // Pass by value copies the WaitGroup
    defer wg.Done()
}

// ✅ CORRECT - Pass by pointer
func process(wg *sync.WaitGroup) {
    defer wg.Done()
}
```

### 5. Context Cancellation
```go
// ❌ WRONG - Not respecting context cancellation
func worker(ctx context.Context) {
    for {
        doWork() // Ignores ctx.Done()
    }
}

// ✅ CORRECT - Check context
func worker(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        default:
            doWork()
        }
    }
}
```

## Error Handling

### 1. Ignoring Errors
```go
// ❌ WRONG
data, _ := ioutil.ReadFile("file.txt")
json.Unmarshal(data, &v)

// ✅ CORRECT
data, err := ioutil.ReadFile("file.txt")
if err != nil {
    return fmt.Errorf("read file: %w", err)
}
if err := json.Unmarshal(data, &v); err != nil {
    return fmt.Errorf("unmarshal: %w", err)
}
```

### 2. Error Wrapping
```go
// ❌ WRONG - Loses error context
if err != nil {
    return errors.New("failed to process")
}

// ✅ CORRECT - Wrap with context
if err != nil {
    return fmt.Errorf("process user %d: %w", userID, err)
}
```

### 3. Panic Recovery
```go
// ✅ CORRECT - Recover in deferred function
func safeExecute() (err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic recovered: %v", r)
        }
    }()
    
    riskyOperation()
    return nil
}
```

## Resource Management

### 1. Deferred Resource Cleanup
```go
// ❌ WRONG - Resource leak if error occurs
file, err := os.Open("file.txt")
data, err := ioutil.ReadAll(file)
file.Close()

// ✅ CORRECT - Use defer
file, err := os.Open("file.txt")
if err != nil {
    return err
}
defer file.Close()

data, err := ioutil.ReadAll(file)
```

### 2. Database Connections
```go
// ❌ WRONG - Connection leak
rows, _ := db.Query("SELECT * FROM users")
for rows.Next() {
    // process
}

// ✅ CORRECT - Always close
rows, err := db.Query("SELECT * FROM users")
if err != nil {
    return err
}
defer rows.Close()

for rows.Next() {
    // process
}
if err := rows.Err(); err != nil {
    return err
}
```

### 3. HTTP Response Body
```go
// ❌ WRONG - Body not closed
resp, _ := http.Get(url)
body, _ := ioutil.ReadAll(resp.Body)

// ✅ CORRECT
resp, err := http.Get(url)
if err != nil {
    return err
}
defer resp.Body.Close()

body, err := ioutil.ReadAll(resp.Body)
```

## Performance

### 1. Unnecessary String Concatenation
```go
// ❌ WRONG - O(n²) with multiple allocations
var result string
for _, s := range strings {
    result += s // Creates new string each iteration
}

// ✅ CORRECT - Use strings.Builder
var builder strings.Builder
for _, s := range strings {
    builder.WriteString(s)
}
result := builder.String()

// ✅ CORRECT - Use strings.Join
result := strings.Join(strings, "")
```

### 2. Slice Preallocation
```go
// ❌ WRONG - Multiple reallocations
var result []int
for i := 0; i < 1000; i++ {
    result = append(result, i)
}

// ✅ CORRECT - Preallocate capacity
result := make([]int, 0, 1000)
for i := 0; i < 1000; i++ {
    result = append(result, i)
}
```

### 3. Map Initialization
```go
// ❌ WRONG - Multiple rehashes
m := make(map[string]int)
for i := 0; i < 1000; i++ {
    m[strconv.Itoa(i)] = i
}

// ✅ CORRECT - Preallocate size
m := make(map[string]int, 1000)
for i := 0; i < 1000; i++ {
    m[strconv.Itoa(i)] = i
}
```

### 4. Unnecessary Goroutines
```go
// ❌ WRONG - Goroutine overhead for simple tasks
for _, item := range smallList {
    go process(item) // Overhead > benefit for small tasks
}

// ✅ CORRECT - Sequential for small workloads
for _, item := range smallList {
    process(item)
}

// ✅ CORRECT - Worker pool for large workloads
const numWorkers = 10
jobs := make(chan Item, len(largeList))
var wg sync.WaitGroup

for i := 0; i < numWorkers; i++ {
    wg.Add(1)
    go worker(jobs, &wg)
}

for _, item := range largeList {
    jobs <- item
}
close(jobs)
wg.Wait()
```

## Code Quality

### 1. Interface Satisfaction
```go
// ✅ CORRECT - Compile-time interface check
var _ io.Reader = (*MyReader)(nil)
var _ io.Writer = (*MyWriter)(nil)
```

### 2. Named Return Values
```go
// ❌ WRONG - Naked return in long function
func calculate(a, b int) (result int, err error) {
    // ... 50 lines of code ...
    return // What are we returning?
}

// ✅ CORRECT - Explicit return or short function
func calculate(a, b int) (result int, err error) {
    result = a + b
    return result, nil
}
```

### 3. Function Length
```go
// ❌ WRONG - Function doing too much (>50 lines)
func ProcessOrder(order Order) error {
    // Validate
    // Calculate
    // Update database
    // Send email
    // Update cache
    // Log
    // ... 100+ lines
}

// ✅ CORRECT - Extract to smaller functions
func ProcessOrder(order Order) error {
    if err := validateOrder(order); err != nil {
        return err
    }
    if err := updateDatabase(order); err != nil {
        return err
    }
    notifyCustomer(order)
    return nil
}
```

## Security

### 1. SQL Injection Prevention
```go
// ❌ WRONG - SQL injection vulnerability
query := fmt.Sprintf("SELECT * FROM users WHERE name = '%s'", username)
rows, _ := db.Query(query)

// ✅ CORRECT - Parameterized query
rows, err := db.Query("SELECT * FROM users WHERE name = ?", username)
```

### 2. Sensitive Data in Logs
```go
// ❌ WRONG - Logging sensitive data
log.Printf("User login: password=%s", password)

// ✅ CORRECT - Redact sensitive data
log.Printf("User login: username=%s", username)
```

### 3. Cryptographic Randomness
```go
// ❌ WRONG - Predictable random for security
rand.Seed(time.Now().UnixNano())
token := rand.Int63()

// ✅ CORRECT - crypto/rand for security
token := make([]byte, 32)
if _, err := rand.Read(token); err != nil {
    return err
}
```

## Testing

### 1. Table-Driven Tests
```go
// ✅ CORRECT - Idiomatic Go testing
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", 
                    tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

### 2. Testify Assertions (if using)
```go
// ✅ CORRECT - Clear assertions
func TestUserService(t *testing.T) {
    user, err := service.GetUser(123)
    require.NoError(t, err)
    assert.Equal(t, "John", user.Name)
    assert.NotNil(t, user.CreatedAt)
}
```

## Common Anti-Patterns

### 1. Empty Interface Abuse
```go
// ❌ WRONG - Losing type safety
func process(data interface{}) {
    // Type assertions everywhere
}

// ✅ CORRECT - Use concrete types or generics (Go 1.18+)
func process[T any](data T) {
    // Type safe
}
```

### 2. Global Variables
```go
// ❌ WRONG - Hard to test, race conditions
var config Config

func Init() { config = loadConfig() }
func GetConfig() Config { return config }

// ✅ CORRECT - Dependency injection
type Service struct {
    config Config
}

func NewService(cfg Config) *Service {
    return &Service{config: cfg}
}
```

### 3. Init() Overuse
```go
// ❌ WRONG - Hidden initialization, hard to test
var db *sql.DB

func init() {
    db = connectDB() // Panic in init is bad
}

// ✅ CORRECT - Explicit initialization
func NewDatabase(connStr string) (*sql.DB, error) {
    return sql.Open("postgres", connStr)
}
```

## Idiomatic Patterns

### Accept Interfaces, Return Structs
```go
// ✅ CORRECT
func NewProcessor(r io.Reader) *Processor {
    return &Processor{reader: r}
}
```

### Error Sentinel Values
```go
// ✅ CORRECT
var (
    ErrNotFound = errors.New("not found")
    ErrInvalidInput = errors.New("invalid input")
)

if errors.Is(err, ErrNotFound) {
    // handle
}
```

### Functional Options Pattern
```go
// ✅ CORRECT
type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}

server := NewServer(
    WithTimeout(30*time.Second),
    WithMaxConns(100),
)
```

## Performance Profiling

Use built-in profiling tools:

```go
import _ "net/http/pprof"

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

Then access:
- CPU profile: http://localhost:6060/debug/pprof/profile
- Heap profile: http://localhost:6060/debug/pprof/heap
- Goroutines: http://localhost:6060/debug/pprof/goroutine
