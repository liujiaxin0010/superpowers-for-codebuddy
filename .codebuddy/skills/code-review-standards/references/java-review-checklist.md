# Java Code Review Checklist

Comprehensive checklist for reviewing Java code, covering best practices and common pitfalls.

## Concurrency Issues

### 1. Race Conditions
```java
// ❌ WRONG - Not thread-safe
public class Counter {
    private int count = 0;
    
    public void increment() {
        count++; // Read-modify-write race condition
    }
}

// ✅ CORRECT - Synchronized
public class Counter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
}

// ✅ BETTER - AtomicInteger
public class Counter {
    private final AtomicInteger count = new AtomicInteger(0);
    
    public void increment() {
        count.incrementAndGet();
    }
}
```

### 2. Double-Checked Locking
```java
// ❌ WRONG - Broken double-checked locking
public class Singleton {
    private static Singleton instance;
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton(); // Can be partially constructed
                }
            }
        }
        return instance;
    }
}

// ✅ CORRECT - Volatile keyword
public class Singleton {
    private static volatile Singleton instance;
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}

// ✅ BEST - Initialization-on-demand holder
public class Singleton {
    private Singleton() {}
    
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```

### 3. Thread Pool Management
```java
// ❌ WRONG - Unbounded thread pool
ExecutorService executor = Executors.newCachedThreadPool();
for (int i = 0; i < 10000; i++) {
    executor.submit(() -> doWork()); // Can exhaust memory
}

// ✅ CORRECT - Bounded thread pool
ExecutorService executor = new ThreadPoolExecutor(
    10, // core pool size
    50, // max pool size
    60L, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(1000) // bounded queue
);

// Don't forget to shutdown
executor.shutdown();
try {
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow();
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
}
```

## Resource Management

### 1. Try-with-Resources
```java
// ❌ WRONG - Resource leak
FileReader fr = new FileReader("file.txt");
BufferedReader br = new BufferedReader(fr);
String line = br.readLine();
br.close(); // What if readLine throws?

// ✅ CORRECT - Try-with-resources
try (FileReader fr = new FileReader("file.txt");
     BufferedReader br = new BufferedReader(fr)) {
    String line = br.readLine();
    // Automatically closed even if exception occurs
}

// ✅ CORRECT - Multiple resources
try (Connection conn = dataSource.getConnection();
     PreparedStatement stmt = conn.prepareStatement(sql);
     ResultSet rs = stmt.executeQuery()) {
    while (rs.next()) {
        // process
    }
}
```

### 2. Stream Closing
```java
// ❌ WRONG - Stream not closed
List<String> lines = Files.lines(Paths.get("file.txt"))
    .filter(line -> line.contains("error"))
    .collect(Collectors.toList());

// ✅ CORRECT
try (Stream<String> lines = Files.lines(Paths.get("file.txt"))) {
    List<String> errors = lines
        .filter(line -> line.contains("error"))
        .collect(Collectors.toList());
}
```

### 3. JDBC Connection Leaks
```java
// ❌ WRONG - Connection leak
Connection conn = dataSource.getConnection();
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);
// Connection never closed!

// ✅ CORRECT
try (Connection conn = dataSource.getConnection();
     Statement stmt = conn.createStatement();
     ResultSet rs = stmt.executeQuery(sql)) {
    while (rs.next()) {
        // process
    }
}
```

## Performance

### 1. String Concatenation
```java
// ❌ SLOW - O(n²) in loop
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i; // Creates new String each time
}

// ✅ FAST - StringBuilder
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);
}
String result = sb.toString();

// ✅ CORRECT - Use String.join for simple cases
String result = String.join(", ", items);
```

### 2. ArrayList Initialization
```java
// ❌ WRONG - Multiple reallocations
List<Integer> list = new ArrayList<>();
for (int i = 0; i < 10000; i++) {
    list.add(i);
}

// ✅ CORRECT - Preallocate capacity
List<Integer> list = new ArrayList<>(10000);
for (int i = 0; i < 10000; i++) {
    list.add(i);
}
```

### 3. Stream vs Loop
```java
// ❌ SLOW - Unnecessary stream overhead for simple operations
int sum = IntStream.range(0, 1000000)
    .map(i -> i * 2)
    .sum();

// ✅ FASTER - Simple loop for performance-critical code
int sum = 0;
for (int i = 0; i < 1000000; i++) {
    sum += i * 2;
}

// Note: Streams are better for readability and parallelism
// Use for complex operations or when parallelization helps
```

### 4. Unnecessary Object Creation
```java
// ❌ WRONG - Creates new Integer object
Integer count = new Integer(42);

// ✅ CORRECT - Use valueOf (cached)
Integer count = Integer.valueOf(42);

// ✅ BEST - Autoboxing
Integer count = 42;
```

## Exception Handling

### 1. Exception Swallowing
```java
// ❌ WRONG - Silent failure
try {
    riskyOperation();
} catch (Exception e) {
    // Swallowed
}

// ✅ CORRECT - Log the exception
try {
    riskyOperation();
} catch (Exception e) {
    logger.error("Operation failed", e);
    throw new ServiceException("Failed to process", e);
}
```

### 2. Catching Generic Exception
```java
// ❌ WRONG - Too broad
try {
    processFile();
} catch (Exception e) {
    // Catches everything, even RuntimeExceptions
}

// ✅ CORRECT - Specific exceptions
try {
    processFile();
} catch (IOException e) {
    logger.error("IO error", e);
} catch (ParseException e) {
    logger.error("Parse error", e);
}
```

### 3. Finally Block
```java
// ❌ WRONG - Return in finally
try {
    return processData();
} finally {
    return defaultValue; // Swallows exception and overrides return!
}

// ✅ CORRECT - No return in finally
Resource resource = null;
try {
    resource = acquireResource();
    return processData(resource);
} finally {
    if (resource != null) {
        resource.close();
    }
}
```

## Security

### 1. SQL Injection
```java
// ❌ WRONG - SQL injection
String sql = "SELECT * FROM users WHERE name = '" + username + "'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);

// ✅ CORRECT - PreparedStatement
String sql = "SELECT * FROM users WHERE name = ?";
try (PreparedStatement stmt = conn.prepareStatement(sql)) {
    stmt.setString(1, username);
    try (ResultSet rs = stmt.executeQuery()) {
        // process
    }
}

// ✅ CORRECT - JPA/Hibernate
TypedQuery<User> query = em.createQuery(
    "SELECT u FROM User u WHERE u.name = :name", User.class);
query.setParameter("name", username);
List<User> users = query.getResultList();
```

### 2. Deserialization Vulnerabilities
```java
// ❌ WRONG - Arbitrary code execution risk
ObjectInputStream ois = new ObjectInputStream(untrustedInput);
Object obj = ois.readObject(); // Can execute arbitrary code!

// ✅ CORRECT - Validate class before deserializing
ObjectInputStream ois = new ObjectInputStream(untrustedInput) {
    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc)
            throws IOException, ClassNotFoundException {
        if (!desc.getName().equals("com.example.SafeClass")) {
            throw new InvalidClassException("Unauthorized class");
        }
        return super.resolveClass(desc);
    }
};

// ✅ BETTER - Use safe serialization (JSON)
ObjectMapper mapper = new ObjectMapper();
MyObject obj = mapper.readValue(json, MyObject.class);
```

### 3. Sensitive Data Logging
```java
// ❌ WRONG - Logging sensitive data
logger.info("User login: password=" + password);
logger.debug("Credit card: " + creditCard);

// ✅ CORRECT - Redact sensitive data
logger.info("User login: username=" + username);
logger.debug("Credit card: ****" + creditCard.substring(creditCard.length() - 4));
```

## Code Quality

### 1. Null Checks
```java
// ❌ WRONG - NullPointerException waiting to happen
public void process(User user) {
    String name = user.getName().toUpperCase();
}

// ✅ CORRECT - Defensive null checks
public void process(User user) {
    if (user == null || user.getName() == null) {
        throw new IllegalArgumentException("User and name required");
    }
    String name = user.getName().toUpperCase();
}

// ✅ BETTER - Use Optional
public void process(Optional<User> user) {
    String name = user
        .map(User::getName)
        .map(String::toUpperCase)
        .orElse("UNKNOWN");
}

// ✅ BEST - Use @NonNull annotations (Lombok, Checker Framework)
public void process(@NonNull User user) {
    String name = user.getName().toUpperCase();
}
```

### 2. equals() and hashCode()
```java
// ❌ WRONG - Inconsistent equals/hashCode
public class User {
    private Long id;
    private String name;
    
    @Override
    public boolean equals(Object o) {
        if (!(o instanceof User)) return false;
        User user = (User) o;
        return Objects.equals(id, user.id);
    }
    // Missing hashCode()!
}

// ✅ CORRECT - Both implemented
public class User {
    private Long id;
    private String name;
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User)) return false;
        User user = (User) o;
        return Objects.equals(id, user.id) &&
               Objects.equals(name, user.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id, name);
    }
}

// ✅ BEST - Use Lombok
@Data
public class User {
    private Long id;
    private String name;
}
```

### 3. Immutable Classes
```java
// ❌ WRONG - Mutable
public class Point {
    public int x, y;
    
    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

// ✅ CORRECT - Immutable
public final class Point {
    private final int x;
    private final int y;
    
    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
    
    public int getX() { return x; }
    public int getY() { return y; }
}

// ✅ BEST - Use record (Java 14+)
public record Point(int x, int y) {}
```

## Modern Java Features

### 1. Records (Java 14+)
```java
// ❌ OLD WAY - Boilerplate
public class User {
    private final String name;
    private final int age;
    
    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getAge() { return age; }
    
    @Override
    public boolean equals(Object o) { /* ... */ }
    @Override
    public int hashCode() { /* ... */ }
    @Override
    public String toString() { /* ... */ }
}

// ✅ MODERN - Record
public record User(String name, int age) {}
```

### 2. Switch Expressions (Java 14+)
```java
// ❌ OLD WAY
String day;
switch (dayOfWeek) {
    case MONDAY:
    case FRIDAY:
        day = "Busy";
        break;
    case SATURDAY:
    case SUNDAY:
        day = "Relaxed";
        break;
    default:
        day = "Normal";
}

// ✅ MODERN - Switch expression
String day = switch (dayOfWeek) {
    case MONDAY, FRIDAY -> "Busy";
    case SATURDAY, SUNDAY -> "Relaxed";
    default -> "Normal";
};
```

### 3. Text Blocks (Java 15+)
```java
// ❌ OLD WAY - Escaped strings
String json = "{\n" +
              "  \"name\": \"John\",\n" +
              "  \"age\": 30\n" +
              "}";

// ✅ MODERN - Text block
String json = """
    {
      "name": "John",
      "age": 30
    }
    """;
```

### 4. Pattern Matching (Java 16+)
```java
// ❌ OLD WAY
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.toUpperCase());
}

// ✅ MODERN - Pattern matching
if (obj instanceof String s) {
    System.out.println(s.toUpperCase());
}
```

## Testing

### 1. JUnit 5
```java
// ✅ CORRECT - Modern JUnit 5
@Test
@DisplayName("Should calculate total price correctly")
void shouldCalculateTotalPrice() {
    // Given
    Order order = new Order();
    order.addItem(new Item("Book", 10.0), 2);
    order.addItem(new Item("Pen", 1.5), 5);
    
    // When
    double total = order.calculateTotal();
    
    // Then
    assertEquals(27.5, total, 0.01);
}

@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 5, 8})
void shouldAcceptValidQuantities(int quantity) {
    assertTrue(order.isValidQuantity(quantity));
}
```

### 2. Mockito
```java
// ✅ CORRECT - Proper mocking
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository repository;
    
    @InjectMocks
    private UserService service;
    
    @Test
    void shouldFindUserById() {
        // Given
        User user = new User("John", 30);
        when(repository.findById(1L)).thenReturn(Optional.of(user));
        
        // When
        Optional<User> result = service.findById(1L);
        
        // Then
        assertTrue(result.isPresent());
        assertEquals("John", result.get().getName());
        verify(repository).findById(1L);
    }
}
```

## Common Anti-Patterns

### 1. God Object
Break large classes (>500 lines) into smaller, focused classes.

### 2. Magic Numbers
```java
// ❌ WRONG
if (status == 200) { }

// ✅ CORRECT
private static final int HTTP_OK = 200;
if (status == HTTP_OK) { }
```

### 3. Utility Classes
```java
// ❌ WRONG - Can be instantiated
public class StringUtils {
    public static String reverse(String s) { }
}

// ✅ CORRECT - Private constructor
public class StringUtils {
    private StringUtils() {
        throw new AssertionError("Utility class");
    }
    
    public static String reverse(String s) { }
}
```

## Static Analysis Tools

Recommended tools:
- **SpotBugs**: Bug detection
- **PMD**: Code quality
- **Checkstyle**: Code style
- **SonarQube**: Comprehensive analysis
- **Error Prone**: Google's static analysis

## Logging Best Practices

### 1. Log Level Usage
```java
// ❌ WRONG - Wrong log level
logger.info("Debug: processing item " + item);
logger.error("User logged in"); // Not an error

// ✅ CORRECT - Appropriate levels
logger.debug("Processing item: {}", item);
logger.info("User {} logged in", username);
logger.warn("Retry attempt {} of {}", attempt, maxRetries);
logger.error("Failed to process order", exception);
```

### 2. Parameterized Logging
```java
// ❌ WRONG - String concatenation (always evaluated)
logger.debug("User " + user + " performed " + action);

// ✅ CORRECT - Parameterized (lazy evaluation)
logger.debug("User {} performed {}", user, action);
```

## API Design

### 1. Method Return Types
```java
// ❌ WRONG - Returning null
public User findUser(Long id) {
    return userMap.get(id); // Can return null
}

// ✅ CORRECT - Return Optional
public Optional<User> findUser(Long id) {
    return Optional.ofNullable(userMap.get(id));
}
```

### 2. Defensive Copying
```java
// ❌ WRONG - Exposing internal state
public class Order {
    private List<Item> items;

    public List<Item> getItems() {
        return items; // Caller can modify!
    }
}

// ✅ CORRECT - Return unmodifiable copy
public List<Item> getItems() {
    return Collections.unmodifiableList(items);
}
```

## Input Validation

### 1. Parameter Validation
```java
// ❌ WRONG - No validation
public void setAge(int age) {
    this.age = age;
}

// ✅ CORRECT - Validate input
public void setAge(int age) {
    if (age < 0 || age > 150) {
        throw new IllegalArgumentException("Age must be 0-150");
    }
    this.age = age;
}
```

### 2. Bean Validation
```java
// ✅ CORRECT - Use annotations
public class UserDTO {
    @NotNull(message = "Name is required")
    @Size(min = 2, max = 50)
    private String name;

    @Email(message = "Invalid email format")
    private String email;

    @Min(value = 0)
    @Max(value = 150)
    private Integer age;
}
```
