# JavaScript/TypeScript Code Review Checklist

Comprehensive checklist for reviewing JavaScript and TypeScript code.

## Security Issues

### 1. XSS Vulnerabilities
```javascript
// ❌ WRONG - XSS vulnerability
element.innerHTML = userInput;
document.write(untrustedData);
eval(userInput);

// ✅ CORRECT - Safe alternatives
element.textContent = userInput;
element.innerText = userInput;
// React automatically escapes
<div>{userInput}</div>

// ✅ CORRECT - Sanitize if HTML needed
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

### 2. Prototype Pollution
```javascript
// ❌ WRONG - Prototype pollution risk
function merge(target, source) {
    for (let key in source) {
        target[key] = source[key]; // Can pollute __proto__
    }
}

// ✅ CORRECT - Check for prototype properties
function merge(target, source) {
    for (let key in source) {
        if (source.hasOwnProperty(key) && key !== '__proto__') {
            target[key] = source[key];
        }
    }
}

// ✅ BETTER - Use Object.assign or spread
const merged = { ...target, ...source };
```

### 3. Insecure Random
```javascript
// ❌ WRONG - Predictable for security
const token = Math.random().toString(36);

// ✅ CORRECT - Cryptographically secure
const crypto = require('crypto');
const token = crypto.randomBytes(32).toString('hex');

// Browser:
const array = new Uint8Array(32);
crypto.getRandomValues(array);
```

### 4. SQL Injection (Node.js)
```javascript
// ❌ WRONG
const query = `SELECT * FROM users WHERE id = ${userId}`;
db.query(query);

// ✅ CORRECT - Parameterized query
db.query('SELECT * FROM users WHERE id = ?', [userId]);

// ✅ CORRECT - ORM (Sequelize, TypeORM)
await User.findByPk(userId);
```

## Common Pitfalls

### 1. var vs let/const
```javascript
// ❌ WRONG - Function scoped, hoisted
for (var i = 0; i < 5; i++) {
    setTimeout(() => console.log(i), 100);
}
// Prints: 5, 5, 5, 5, 5

// ✅ CORRECT - Block scoped
for (let i = 0; i < 5; i++) {
    setTimeout(() => console.log(i), 100);
}
// Prints: 0, 1, 2, 3, 4

// ✅ BEST - Use const when possible
const items = [1, 2, 3];
```

### 2. == vs ===
```javascript
// ❌ WRONG - Type coercion
if (value == null) { }
if (count == '5') { }

// ✅ CORRECT - Strict equality
if (value === null || value === undefined) { }
if (count === 5) { }

// ✅ ACCEPTABLE - Only for null/undefined check
if (value == null) { } // Checks both null and undefined
```

### 3. Array Iteration
```javascript
// ❌ WRONG - for...in iterates over properties
for (let i in array) {
    console.log(array[i]); // i is a string!
}

// ✅ CORRECT - for...of
for (let item of array) {
    console.log(item);
}

// ✅ CORRECT - forEach
array.forEach(item => console.log(item));

// ✅ CORRECT - map for transformation
const doubled = array.map(x => x * 2);
```

### 4. this Binding
```javascript
// ❌ WRONG - Lost this context
class Counter {
    constructor() {
        this.count = 0;
    }
    increment() {
        this.count++;
    }
}
const counter = new Counter();
setTimeout(counter.increment, 1000); // this is undefined!

// ✅ CORRECT - Arrow function
setTimeout(() => counter.increment(), 1000);

// ✅ CORRECT - Bind
setTimeout(counter.increment.bind(counter), 1000);

// ✅ BEST - Class field with arrow function
class Counter {
    count = 0;
    increment = () => {
        this.count++;
    };
}
```

### 5. Callback Hell
```javascript
// ❌ WRONG - Pyramid of doom
getData(function(a) {
    getMoreData(a, function(b) {
        getEvenMoreData(b, function(c) {
            console.log(c);
        });
    });
});

// ✅ CORRECT - Promises
getData()
    .then(a => getMoreData(a))
    .then(b => getEvenMoreData(b))
    .then(c => console.log(c))
    .catch(error => console.error(error));

// ✅ BEST - async/await
try {
    const a = await getData();
    const b = await getMoreData(a);
    const c = await getEvenMoreData(b);
    console.log(c);
} catch (error) {
    console.error(error);
}
```

## Performance

### 1. DOM Manipulation
```javascript
// ❌ SLOW - Multiple reflows
for (let i = 0; i < 1000; i++) {
    const div = document.createElement('div');
    div.textContent = i;
    container.appendChild(div); // Reflow each time
}

// ✅ FAST - Batch DOM updates
const fragment = document.createDocumentFragment();
for (let i = 0; i < 1000; i++) {
    const div = document.createElement('div');
    div.textContent = i;
    fragment.appendChild(div);
}
container.appendChild(fragment); // Single reflow
```

### 2. Event Listeners
```javascript
// ❌ WRONG - Memory leak
element.addEventListener('click', function handler() {
    // Never removed
});

// ✅ CORRECT - Remove when done
const handler = () => { };
element.addEventListener('click', handler);
// Later:
element.removeEventListener('click', handler);

// ✅ CORRECT - AbortController
const controller = new AbortController();
element.addEventListener('click', handler, { signal: controller.signal });
// Later:
controller.abort(); // Removes all listeners
```

### 3. Debouncing/Throttling
```javascript
// ❌ WRONG - Too many calls
window.addEventListener('scroll', () => {
    updateUI(); // Called hundreds of times
});

// ✅ CORRECT - Debounce
import { debounce } from 'lodash';
window.addEventListener('scroll', debounce(updateUI, 200));

// ✅ CORRECT - Throttle
import { throttle } from 'lodash';
window.addEventListener('scroll', throttle(updateUI, 200));
```

### 4. Array Operations
```javascript
// ❌ SLOW - Multiple iterations
const result = items
    .filter(x => x > 0)
    .map(x => x * 2)
    .filter(x => x < 100);

// ✅ FASTER - Single iteration with reduce
const result = items.reduce((acc, x) => {
    if (x > 0) {
        const doubled = x * 2;
        if (doubled < 100) {
            acc.push(doubled);
        }
    }
    return acc;
}, []);

// Note: Readability vs performance tradeoff
```

## Async/Await

### 1. Error Handling
```javascript
// ❌ WRONG - Unhandled rejection
async function fetchData() {
    const data = await fetch(url); // No error handling
    return data.json();
}

// ✅ CORRECT - Try/catch
async function fetchData() {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch failed:', error);
        throw error;
    }
}
```

### 2. Promise.all vs Sequential
```javascript
// ❌ SLOW - Sequential execution
const user = await getUser(id);
const posts = await getPosts(id);
const comments = await getComments(id);

// ✅ FAST - Parallel execution
const [user, posts, comments] = await Promise.all([
    getUser(id),
    getPosts(id),
    getComments(id)
]);

// ✅ CORRECT - Promise.allSettled for partial failures
const results = await Promise.allSettled([
    fetchUser(),
    fetchPosts(),
    fetchComments()
]);
```

### 3. Forgotten await
```javascript
// ❌ WRONG - Forgot await
async function processData() {
    const data = fetchData(); // Returns Promise, not data!
    return data.length; // undefined.length
}

// ✅ CORRECT
async function processData() {
    const data = await fetchData();
    return data.length;
}

// ESLint rule: @typescript-eslint/no-floating-promises
```

## TypeScript Specific

### 1. Type Safety
```typescript
// ❌ WRONG - any defeats TypeScript
function process(data: any) {
    return data.value; // No type checking
}

// ✅ CORRECT - Proper types
interface Data {
    value: string;
}
function process(data: Data): string {
    return data.value;
}

// ✅ CORRECT - Generic for flexibility
function process<T extends { value: string }>(data: T): string {
    return data.value;
}
```

### 2. Non-null Assertions
```typescript
// ❌ WRONG - Unsafe non-null assertion
function getUser(id: string) {
    return users.find(u => u.id === id)!; // Runtime error if not found
}

// ✅ CORRECT - Handle null case
function getUser(id: string): User | undefined {
    return users.find(u => u.id === id);
}

// ✅ CORRECT - Throw if required
function getUser(id: string): User {
    const user = users.find(u => u.id === id);
    if (!user) {
        throw new Error(`User ${id} not found`);
    }
    return user;
}
```

### 3. Enums vs Union Types
```typescript
// ❌ LESS FLEXIBLE - Enum
enum Status {
    Pending,
    Active,
    Closed
}

// ✅ MORE FLEXIBLE - Union type
type Status = 'pending' | 'active' | 'closed';

// ✅ BEST - Const assertion
const STATUS = {
    PENDING: 'pending',
    ACTIVE: 'active',
    CLOSED: 'closed'
} as const;

type Status = typeof STATUS[keyof typeof STATUS];
```

## React Specific

### 1. Key Prop
```jsx
// ❌ WRONG - Index as key (anti-pattern)
{items.map((item, index) => (
    <Item key={index} data={item} />
))}

// ✅ CORRECT - Unique stable identifier
{items.map(item => (
    <Item key={item.id} data={item} />
))}
```

### 2. useEffect Dependencies
```jsx
// ❌ WRONG - Missing dependencies
useEffect(() => {
    fetchData(userId); // userId not in deps
}, []);

// ✅ CORRECT - Complete dependencies
useEffect(() => {
    fetchData(userId);
}, [userId]);

// ✅ CORRECT - Callback in deps
const fetchData = useCallback(async () => {
    const data = await api.get(userId);
}, [userId]);

useEffect(() => {
    fetchData();
}, [fetchData]);
```

### 3. State Updates
```jsx
// ❌ WRONG - Stale state
const increment = () => {
    setCount(count + 1);
    setCount(count + 1); // Both use same count
};

// ✅ CORRECT - Functional update
const increment = () => {
    setCount(c => c + 1);
    setCount(c => c + 1);
};
```

## Code Smells

### 1. Magic Numbers/Strings
```javascript
// ❌ WRONG
if (status === 200) { }
if (role === 'admin') { }

// ✅ CORRECT
const HTTP_OK = 200;
const ROLE_ADMIN = 'admin';

if (status === HTTP_OK) { }
if (role === ROLE_ADMIN) { }
```

### 2. Long Functions
Break functions >50 lines into smaller, focused functions.

### 3. Nested Callbacks
Use async/await or Promise chains instead of deeply nested callbacks.

### 4. Console.log in Production
```javascript
// ❌ WRONG
console.log('Debug info', data);

// ✅ CORRECT - Use proper logging
import logger from './logger';
logger.debug('Debug info', { data });

// ✅ CORRECT - Remove or guard
if (process.env.NODE_ENV === 'development') {
    console.log('Debug info', data);
}
```

## Testing

### 1. Jest/Vitest Tests
```typescript
// ✅ CORRECT - Descriptive tests
describe('UserService', () => {
    it('should create user with valid data', async () => {
        const user = await service.createUser({
            name: 'John',
            email: 'john@example.com'
        });
        
        expect(user).toMatchObject({
            name: 'John',
            email: 'john@example.com'
        });
    });
    
    it('should throw error for invalid email', async () => {
        await expect(
            service.createUser({ name: 'John', email: 'invalid' })
        ).rejects.toThrow('Invalid email');
    });
});
```

### 2. React Testing Library
```jsx
// ✅ CORRECT - Test user behavior
import { render, screen, fireEvent } from '@testing-library/react';

test('increments counter on button click', () => {
    render(<Counter />);
    
    const button = screen.getByRole('button', { name: /increment/i });
    const count = screen.getByText(/count: 0/i);
    
    fireEvent.click(button);
    
    expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
});
```

## Tools

Recommended linting configuration (.eslintrc.json):
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "no-console": "warn",
    "eqeqeq": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```
