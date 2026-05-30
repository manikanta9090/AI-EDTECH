# Task 2: Technical Questions

## Python Internals

### GIL (Global Interpreter Lock)
The GIL is a mutex preventing multiple threads from executing Python bytecode simultaneously. It protects internal state but limits true parallelism.

```python
# Example - threads run concurrently but not in parallel due to GIL
import threading
def cpu_task():
    sum(i*i for i in range(1000000))

t1 = threading.Thread(target=cpu_task)
t2 = threading.Thread(target=cpu_task)
```

### Memory Management
Python uses reference counting + cyclic garbage collector. Objects are freed when ref count reaches zero.

### Decorators
```python
def timing(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Execution time: {time.time() - start}")
        return result
    return wrapper

@timing
def process_query(question):
    pass
```

---

## Data Structures & Algorithms

| Operation | Time Complexity |
|-----------|---------------|
| Array access | O(1) |
| Hash table lookup | O(1) avg |
| Binary search | O(log n) |
| Quick sort | O(n log n) |

```python
# Binary search
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: left = mid + 1
        else: right = mid - 1
    return -1
```

---

## System Design

### Rate Limiting
Token bucket algorithm:
```python
class RateLimiter:
    def __init__(self, capacity=100, refill_rate=10):
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens=1):
        now = time.time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last_refill) * self.refill_rate)
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
```

### Caching
Use `@lru_cache` for memoization:
```python
from functools import lru_cache
@lru_cache(maxsize=100)
def cached_sql(question):
    return generate_sql(question)
```

---

## Concurrency

### Threading vs Asyncio

| | Threading | Asyncio |
|---|-----------|---------|
| Best for | I/O bound | I/O bound |
| Memory per task | Higher | Lower |

```python
# Async FastAPI endpoint
@app.get("/async")
async def async_endpoint():
    result = await some_io_operation()
    return {"result": result}
```

---

## Security Best Practices

1. Input validation
2. SQL injection prevention
3. Environment variable management
4. Error handling without exposing internals
5. Rate limiting