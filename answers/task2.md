# Technical Assignment Solutions

## Python Internals

### Q1. Python Memory Management

Python uses a combination of reference counting and cyclic garbage collection for memory management:

- **Reference Counting**: Each object maintains a count of references. When count reaches zero, object is deallocated immediately
- **Cyclic Garbage Collector**: Handles reference cycles (A→B→A) that reference counting cannot break

```python
import sys
import gc

# Reference counting example
a = []
b = a
print(sys.getrefcount(a))  # 3 (a, b, +1 temporary for getrefcount)
del b
# Object deallocated when refcount reaches 0

# Cyclic GC handles cycles
class Node:
    def __init__(self):
        self.ref = None

a = Node()
b = Node()
a.ref = b
b.ref = a  # Cycle created
# gc.collect() will find and collect these eventually
```

**Time Complexity**: O(1) for reference counting operations, O(n) for garbage collection where n is number of objects in cycles.

---

### Q2. Global Interpreter Lock (GIL)

The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecode simultaneously.

```python
import threading
import time

def cpu_bound_task(n):
    return sum(i*i for i in range(n))

# These run sequentially due to GIL, not in parallel
t1 = threading.Thread(target=cpu_bound_task, args=(1000000,))
t2 = threading.Thread(target=cpu_bound_task, args=(1000000,))
t1.start(); t2.start()  # Not true parallelism for CPU-bound tasks
```

**Impact**:
- Limits multi-core CPU usage for CPU-bound Python code
- I/O-bound operations release GIL, allowing parallelism
- Use `multiprocessing` for CPU-bound tasks

---

### Q3. `__new__` vs `__init__`

- **`__new__`**: Static method that creates and returns the instance (before `__init__`)
- **`__init__`**: Instance method that initializes the already-created instance

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.initialized = True

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True
```

Use `__new__` for:
- Factory patterns, singletons, immutable types (int, str, tuple)
- Customizing instance creation

---

### Q4. Custom Context Manager

Context managers enable `with` statement support for resource management:

```python
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self, connection_string):
        self.conn_str = connection_string
        self.connection = None
    
    def __enter__(self):
        self.connection = connect(self.conn_str)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
        return False  # Don't suppress exceptions

# Alternative using decorator
@contextmanager
def database_connection(connection_string):
    conn = connect(connection_string)
    try:
        yield conn
    finally:
        conn.close()
```

---

### Q5. Descriptors

Descriptors are objects that define `__get__`, `__set__`, or `__delete__` methods, controlling attribute access:

```python
class Typed:
    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type
    
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        obj.__dict__[self.name] = value

class Person:
    age = Typed('age', int)
    name = Typed('name', str)

p = Person()
p.age = 25  # Works
p.age = "hello"  # Raises TypeError
```

---

### Q6. Retry Decorator

```python
import time
import functools

def retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt == max_attempts:
                        raise
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1)
def api_call():
    # Simulate flaky API
    pass
```

---

### Q7. Generators vs Iterators

- **Iterator**: Any object implementing `__iter__` and `__next__`
- **Generator**: Iterator created using `function + yield`

```python
# Iterator class
class CountDown:
    def __init__(self, n):
        self.n = n
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n

# Generator (more concise)
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# Use
cd = CountDown(5)
gen = countdown(5)  # gen is iterator, countdown is generator function
```

**Complexity**: O(1) memory for both, but generators are lazy and more memory-efficient for large datasets.

---

## Data Structures & Algorithms

### Q8. LRU Cache

Least Recently Used cache evicts least recently accessed items when full:

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Using built-in
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_function(n):
    return n * n
```

**Time Complexity**: O(1) for get/put. **Space Complexity**: O(capacity).

---

### Q9. Trie (Prefix Tree)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word: str) -> bool:
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
    
    def startsWith(self, prefix: str) -> bool:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
```

**Time Complexity**: O(m) for insert/search where m is word length. **Space Complexity**: O(m × alphabet_size × n_words).

---

### Q10. Heap

```python
import heapq

# Min heap
heap = []
for num in [5, 3, 7, 1]:
    heapq.heappush(heap, num)

print(heapq.heappop(heap))  # 1

# Max heap (negate values)
max_heap = []
for num in [5, 3, 7, 1]:
    heapq.heappush(max_heap, -num)

print(-heapq.heappop(max_heap))  # 7

# Heapify existing list
arr = [5, 3, 7, 1]
heapq.heapify(arr)  # O(n)
```

**Time Complexity**: 
- heapify: O(n)
- push/pop: O(log n)

---

### Q11. Insert/Delete/getRandom O(1)

Using hash map + array:

```python
import random

class RandomizedSet:
    def __init__(self):
        self.val_to_index = {}
        self.nums = []
    
    def insert(self, val: int) -> bool:
        if val in self.val_to_index:
            return False
        self.nums.append(val)
        self.val_to_index[val] = len(self.nums) - 1
        return True
    
    def remove(self, val: int) -> bool:
        if val not in self.val_to_index:
            return False
        index = self.val_to_index[val]
        last_val = self.nums[-1]
        self.nums[index] = last_val
        self.val_to_index[last_val] = index
        self.nums.pop()
        del self.val_to_index[val]
        return True
    
    def getRandom(self) -> int:
        return random.choice(self.nums)
```

**Time Complexity**: O(1) for all operations. **Space Complexity**: O(n).

---

### Q12. Immutability

Immutable objects cannot be modified after creation:

```python
# Built-in immutable types
t = (1, 2, 3)  # tuple
s = "hello"     # str

# Using named tuple for custom immutable
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)

# Frozen dataclass (Python 3.7+)
from dataclasses import dataclass
@dataclass(frozen=True)
class Person:
    name: str
    age: int

p = Person("Alice", 30)
# p.age = 31  # Raises FrozenInstanceError
```

Benefits: thread-safety, hashability, predictable behavior.

---

### Q13. Consistent Hashing

Distributes keys across nodes with minimal redistribution on node changes:

```python
import hashlib
import bisect

class ConsistentHasher:
    def __init__(self, nodes=None, replicas=100):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        for node in nodes or []:
            self.add_node(node)
    
    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)
    
    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            idx = bisect.bisect_left(self.sorted_keys, key)
            self.sorted_keys.pop(idx)
    
    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
```

---

## Algorithms

### Q14. Kth Largest Element

Using heap approach:

```python
import heapq

def findKthLargest(nums, k):
    return heapq.nlargest(k, nums)[-1]

# Or using min-heap of size k
def findKthLargest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]
```

**Time Complexity**: O(n log k). **Space Complexity**: O(k).

---

### Q15. Quick Sort

```python
def quicksort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

# Average: O(n log n), Worst: O(n²) when already sorted and poor pivot choice
# Space: O(log n) for recursion stack
```

---

### Q16. Longest Substring Without Repeating Characters

```python
def lengthOfLongestSubstring(s):
    char_index = {}
    start = max_length = 0
    
    for i, char in enumerate(s):
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        char_index[char] = i
        max_length = max(max_length, i - start + 1)
    
    return max_length
```

**Time Complexity**: O(n). **Space Complexity**: O(min(n, m)) where m is alphabet size.

---

### Q17. Cycle Detection

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

**Time Complexity**: O(n). **Space Complexity**: O(1).

---

### Q18. Topological Sorting

```python
from collections import defaultdict, deque

def topological_sort(graph, num_nodes):
    in_degree = [0] * num_nodes
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1
    
    queue = deque([i for i in range(num_nodes) if in_degree[i] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == num_nodes else []
```

**Time Complexity**: O(V + E). **Space Complexity**: O(V).

---

### Q19. Number of Islands

```python
def numIslands(grid):
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    visited = set()
    
    def dfs(r, c):
        if (r < 0 or c < 0 or r >= rows or c >= cols or
            (r, c) in visited or grid[r][c] == '0'):
            return
        visited.add((r, c))
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    
    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r, c) not in visited:
                islands += 1
                dfs(r, c)
    
    return islands
```

**Time Complexity**: O(m × n). **Space Complexity**: O(m × n) for visited set or O(1) with in-place modification.

---

### Q20. Coin Change DP

```python
def coinChange(coins, amount):
    dp = [amount + 1] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if i - coin >= 0:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != amount + 1 else -1
```

**Time Complexity**: O(amount × coins). **Space Complexity**: O(amount).

---

## Concurrency

### Q21. Threading vs Multiprocessing vs Asyncio

| Aspect | Threading | Multiprocessing | Asyncio |
|--------|-----------|-----------------|---------|
| Best for | I/O-bound | CPU-bound | I/O-bound (high concurrency) |
| Memory per task | Low | High | Low |
| Performance | Limited by GIL | True parallelism | Single-threaded async |
| Communication | Shared memory | IPC/pipes | Async queues |

```python
# Threading
import threading
t = threading.Thread(target=worker)

# Multiprocessing  
import multiprocessing
p = multiprocessing.Process(target=worker)

# Asyncio
import asyncio
async def worker():
    await asyncio.sleep(1)
```

---

### Q22. Asyncio Outperforming Threading

Asyncio excels when:
- Thousands of concurrent I/O operations (web scraping, API calls)
- High wait time relative to CPU time
- Single-threaded event loop avoids context switching overhead

```python
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

# vs threading: asyncio handles 10k+ connections efficiently
# threading: limited by OS thread limits (~1k-4k practical)
```

---

### Q23. Profiling and Optimization

```python
import cProfile
import pstats
from functools import wraps

# cProfile
profiler = cProfile.Profile()
profiler.enable()
# ... code to profile
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)

# Line profiler for line-by-line
# pip install line_profiler
@profile
def function_to_profile():
    pass

# Time-based measurement
import time
start = time.perf_counter()
result = expensive_operation()
elapsed = time.perf_counter() - start
```

Optimization techniques:
- Use built-in functions and libraries
- Avoid unnecessary allocations
- Use appropriate data structures (dict for lookups, set for uniqueness)
- Consider caching/memoization

---

## System Design

### Q24. URL Shortener Design

```
Components:
- API Gateway (REST endpoints: POST /shorten, GET /{code})
- Application Server (business logic)
- Database (hash → URL mapping)
- Cache (Redis for hot URLs)

Architecture:
Client → Load Balancer → API Server → Cache/DB

Database Schema:
urls {
  id: BIGINT PRIMARY KEY (auto-increment)
  long_url: VARCHAR
  short_code: VARCHAR UNIQUE
  created_at: TIMESTAMP
  expires_at: TIMESTAMP
}

ID Generation Strategies:
1. Base62 encoding of auto-increment ID: O(1)
2. Hash long_url (MD5, SHA) + collision handling
3. Snowflake-like distributed ID generation

Caching:
- Redis LRU: short_code → long_url
- TTL for expired URLs
```

**Scalability**: 
- Use consistent hashing for distributed cache
- Horizontal partitioning by short_code prefix
- CDN for redirecting popular URLs

---

### Q25. High-Throughput Log Analytics System

```
Architecture:

[Log Sources] → [Message Queue (Kafka)] → [Log Processor] → [Storage (Elasticsearch/S3)]
                                    ↓
                              [Real-time Analyzer] → [Alerting/Monitoring]

Components:
1. Ingestion Layer: Kafka cluster for buffering
2. Processing Layer: Spark/Flink for real-time aggregation
3. Storage Layer: 
   - Hot data: Elasticsearch for search
   - Cold data: S3 with Parquet/ORC
4. Query Layer: API for metrics/dashboards
5. Alerting: Webhook/email/slack notifications

Key Design Decisions:
- Partitioning: By log source/time
- Indexing: Time-based indices in Elasticsearch
- Aggregation: Pre-compute metrics every minute
- Sampling: For high-volume debug logs
```

**Scalability**:
- Kafka partitions for parallel processing
- Elasticsearch sharding for search
- Auto-scaling processors based on queue depth
- Tiered storage for cost optimization