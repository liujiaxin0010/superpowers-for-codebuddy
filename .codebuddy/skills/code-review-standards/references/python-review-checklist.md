# Python Code Review Checklist

Comprehensive checklist for reviewing Python code, covering best practices, common pitfalls, and Pythonic patterns.

## Security Issues

### 1. SQL Injection
```python
# ❌ WRONG - SQL injection vulnerability
username = request.form['username']
query = f"SELECT * FROM users WHERE name = '{username}'"
cursor.execute(query)

# ✅ CORRECT - Parameterized query
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (username,))

# ✅ CORRECT - ORM (Django/SQLAlchemy)
User.objects.filter(name=username)
```

### 2. Command Injection
```python
# ❌ WRONG - Shell injection
filename = request.args.get('file')
os.system(f'cat {filename}')

# ✅ CORRECT - Use subprocess with list
import subprocess
subprocess.run(['cat', filename], check=True)

# ✅ BETTER - Avoid shell commands entirely
with open(filename, 'r') as f:
    content = f.read()
```

### 3. Path Traversal
```python
# ❌ WRONG - Directory traversal vulnerability
filepath = os.path.join('/uploads', request.args['filename'])
with open(filepath) as f:
    return f.read()

# ✅ CORRECT - Validate path
from pathlib import Path

base_dir = Path('/uploads')
filepath = (base_dir / request.args['filename']).resolve()
if not filepath.is_relative_to(base_dir):
    raise ValueError("Invalid path")
```

### 4. Pickle Security
```python
# ❌ WRONG - Arbitrary code execution risk
data = pickle.loads(untrusted_data)

# ✅ CORRECT - Use safe serialization
import json
data = json.loads(untrusted_data)
```

### 5. Hardcoded Secrets
```python
# ❌ WRONG
API_KEY = "sk_live_abc123def456"
DATABASE_PASSWORD = "MyP@ssw0rd"

# ✅ CORRECT - Environment variables
import os
API_KEY = os.environ.get('API_KEY')
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD')

# ✅ BETTER - Secret management
from secretsmanager import get_secret
credentials = get_secret('prod/database')
```

## Performance

### 1. List Comprehensions vs. Loops
```python
# ❌ SLOW
result = []
for item in items:
    if item > 0:
        result.append(item * 2)

# ✅ FASTER - List comprehension
result = [item * 2 for item in items if item > 0]

# ✅ BEST - Generator for large datasets
result = (item * 2 for item in items if item > 0)
```

### 2. String Concatenation
```python
# ❌ WRONG - O(n²) complexity
result = ""
for s in strings:
    result += s  # Creates new string each time

# ✅ CORRECT - O(n) complexity
result = "".join(strings)

# ✅ CORRECT - For formatted strings
result = ", ".join(strings)
```

### 3. Dictionary Lookups
```python
# ❌ SLOW - Multiple lookups
if key in dict:
    value = dict[key]
else:
    value = default

# ✅ FASTER - Single lookup
value = dict.get(key, default)

# ✅ BEST - setdefault for mutable defaults
dict.setdefault(key, []).append(item)
```

### 4. Function Call Overhead
```python
# ❌ SLOW - Repeated function calls
for i in range(len(items)):
    process(items[i])

# ✅ FASTER - Direct iteration
for item in items:
    process(item)

# ✅ FASTER - Enumerate when index needed
for i, item in enumerate(items):
    process(i, item)
```

### 5. Unnecessary Copies
```python
# ❌ WRONG - Creates copy
sorted_items = items.sort()  # Returns None, items modified

# ✅ CORRECT - In-place sort
items.sort()

# ✅ CORRECT - Return new sorted list
sorted_items = sorted(items)
```

## Code Quality

### 1. Exception Handling
```python
# ❌ WRONG - Bare except
try:
    risky_operation()
except:
    pass

# ✅ CORRECT - Specific exceptions
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except IOError as e:
    logger.error(f"IO error: {e}")

# ✅ CORRECT - Re-raise if needed
try:
    process_data()
except Exception as e:
    logger.error(f"Error processing: {e}")
    raise
```

### 2. Context Managers
```python
# ❌ WRONG - Manual resource management
f = open('file.txt')
data = f.read()
f.close()

# ✅ CORRECT - Context manager
with open('file.txt') as f:
    data = f.read()

# ✅ CORRECT - Multiple context managers
with open('input.txt') as fin, open('output.txt', 'w') as fout:
    fout.write(fin.read())
```

### 3. Default Mutable Arguments
```python
# ❌ WRONG - Mutable default shared across calls
def append_to(item, target=[]):
    target.append(item)
    return target

# ✅ CORRECT - Use None
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

### 4. Type Hints
```python
# ❌ MISSING - No type information
def calculate(a, b):
    return a + b

# ✅ CORRECT - Clear type hints
def calculate(a: int, b: int) -> int:
    return a + b

# ✅ CORRECT - Complex types
from typing import List, Dict, Optional

def process_users(
    users: List[Dict[str, str]]
) -> Optional[Dict[str, int]]:
    pass
```

### 5. Docstrings
```python
# ❌ MISSING - No documentation
def calculate_discount(price, percentage):
    return price * (1 - percentage / 100)

# ✅ CORRECT - Google style docstring
def calculate_discount(price: float, percentage: float) -> float:
    """Calculate discounted price.
    
    Args:
        price: Original price
        percentage: Discount percentage (0-100)
        
    Returns:
        Discounted price
        
    Raises:
        ValueError: If percentage is not in valid range
    """
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be 0-100")
    return price * (1 - percentage / 100)
```

## Common Pitfalls

### 1. Late Binding Closures
```python
# ❌ WRONG - All functions reference same 'i'
functions = [lambda: i for i in range(5)]
print([f() for f in functions])  # [4, 4, 4, 4, 4]

# ✅ CORRECT - Capture value
functions = [lambda i=i: i for i in range(5)]
print([f() for f in functions])  # [0, 1, 2, 3, 4]
```

### 2. Modifying List While Iterating
```python
# ❌ WRONG - Unpredictable behavior
for item in items:
    if condition(item):
        items.remove(item)

# ✅ CORRECT - List comprehension
items = [item for item in items if not condition(item)]

# ✅ CORRECT - Iterate over copy
for item in items[:]:
    if condition(item):
        items.remove(item)
```

### 3. Class Variables vs Instance Variables
```python
# ❌ WRONG - Class variable shared across instances
class Counter:
    count = 0  # Shared!
    
    def increment(self):
        self.count += 1

# ✅ CORRECT - Instance variable
class Counter:
    def __init__(self):
        self.count = 0
        
    def increment(self):
        self.count += 1
```

### 4. Import *
```python
# ❌ WRONG - Namespace pollution
from module import *

# ✅ CORRECT - Explicit imports
from module import function1, function2

# ✅ CORRECT - Import module
import module
module.function1()
```

## Database & ORM

### 1. N+1 Query Problem (Django)
```python
# ❌ WRONG - N+1 queries
posts = Post.objects.all()
for post in posts:
    print(post.author.name)  # Separate query per post

# ✅ CORRECT - select_related (foreign key)
posts = Post.objects.select_related('author').all()

# ✅ CORRECT - prefetch_related (many-to-many)
posts = Post.objects.prefetch_related('tags').all()
```

### 2. Bulk Operations
```python
# ❌ SLOW - Individual inserts
for user in users:
    User.objects.create(name=user['name'])

# ✅ FAST - Bulk create
User.objects.bulk_create([
    User(name=user['name']) for user in users
])
```

### 3. Raw SQL Safety
```python
# ❌ WRONG - SQL injection
User.objects.raw(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ CORRECT - Parameterized
User.objects.raw("SELECT * FROM users WHERE id = %s", [user_id])
```

## Async/Await

### 1. Blocking in Async Function
```python
# ❌ WRONG - Blocking call in async
async def fetch_data():
    data = requests.get(url)  # Blocks event loop!
    return data

# ✅ CORRECT - Use async library
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### 2. Not Awaiting Coroutines
```python
# ❌ WRONG - Coroutine not awaited
async def main():
    fetch_data()  # Does nothing!

# ✅ CORRECT
async def main():
    await fetch_data()

# ✅ CORRECT - Gather multiple
await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)
```

## Testing

### 1. Pytest Fixtures
```python
# ✅ CORRECT - Reusable fixtures
import pytest

@pytest.fixture
def database():
    db = setup_database()
    yield db
    db.cleanup()

def test_user_creation(database):
    user = database.create_user("test")
    assert user.name == "test"
```

### 2. Mocking
```python
# ✅ CORRECT - Mock external dependencies
from unittest.mock import Mock, patch

def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'data': 'test'}
        result = fetch_api_data()
        assert result == {'data': 'test'}
```

### 3. Parameterized Tests
```python
# ✅ CORRECT - Test multiple cases
import pytest

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert square(input) == expected
```

## Pythonic Patterns

### 1. EAFP vs LBYL
```python
# ❌ LBYL - Look Before You Leap
if key in dict:
    value = dict[key]
else:
    value = default

# ✅ EAFP - Easier to Ask for Forgiveness than Permission
try:
    value = dict[key]
except KeyError:
    value = default
```

### 2. Enumerate
```python
# ❌ WRONG
for i in range(len(items)):
    print(i, items[i])

# ✅ CORRECT
for i, item in enumerate(items):
    print(i, item)
```

### 3. Zip
```python
# ❌ WRONG
for i in range(len(names)):
    print(names[i], ages[i])

# ✅ CORRECT
for name, age in zip(names, ages):
    print(name, age)
```

### 4. Dictionary Methods
```python
# ✅ items()
for key, value in dict.items():
    print(key, value)

# ✅ get() with default
value = dict.get(key, default)

# ✅ setdefault()
dict.setdefault(key, []).append(item)
```

### 5. Comprehensions
```python
# ✅ List comprehension
squares = [x**2 for x in range(10)]

# ✅ Dict comprehension
word_lengths = {word: len(word) for word in words}

# ✅ Set comprehension
unique_lengths = {len(word) for word in words}
```

## Code Smells

### 1. Long Functions (>50 lines)
Extract to smaller functions with clear responsibilities.

### 2. Deep Nesting (>3 levels)
Use early returns or extract to functions.

### 3. Magic Numbers
```python
# ❌ WRONG
if status == 200:

# ✅ CORRECT
HTTP_OK = 200
if status == HTTP_OK:
```

### 4. Commented-Out Code
Delete it (use version control).

### 5. God Objects
Break into smaller, focused classes.

## Static Analysis Tools

Recommended tools:
- **pylint**: Comprehensive linting
- **flake8**: Style guide enforcement
- **mypy**: Type checking
- **bandit**: Security issues
- **black**: Code formatting
- **isort**: Import sorting
- **pytest**: Testing framework

Configuration example (.flake8):
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv
```
