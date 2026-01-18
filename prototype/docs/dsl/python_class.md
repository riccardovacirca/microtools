PYTHON_CLASS_STYLE microtools_python_class v2.0

# NAMING CONVENTIONS

CLASSES:
  - PascalCase: DB, DBConnPool, Env, Redis

METHODS:
  - Public: camelCase - acquire(), release(), hasConnection(), cursorOpen()
  - Private: _camelCase - _detectDriver(), _buildConfig(), _createEngine()

ATTRIBUTES:
  - ALL private with underscore: _connection, _pool, _cursor, _client
  - NO public attributes

LOCAL VARIABLES:
  - camelCase: retv, connStr, dbPath, poolSize, checkedOut

# FORMATTING

INDENTATION:
  - 4 spaces (PEP8 standard)

BLANK LINES:
  - 1 between methods
  - 2 between classes
  - Minimal inside method bodies

DOCSTRINGS:
  - Single line ONLY: """Brief description."""
  - Mandatory for classes and ALL methods

# TYPE HINTS

MANDATORY for all parameters and returns.

SYNTAX:
  - Modern union: int | None, str | None
  - Collections: List[Dict[str, Any]], Dict[str, str]

EXAMPLES:
  ✓ def query(self, sql: str, params: tuple = None) -> int | None:
  ✓ def select(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
  ✓ def hasConnection(self) -> bool:

# CONTROL FLOW

SINGLE EXIT POINT:
  - Mandatory for all methods with return value
  - Use retv variable initialized at start
  - Single return statement at end

TRADITIONAL STYLE:
  - NO list comprehensions
  - NO dict comprehensions
  - NO ternary expressions (x if cond else y)
  - Use explicit for loops with append()
  - Use explicit if/else blocks

EXAMPLE:
```python
def cursorHasNext(self) -> bool:
    """Check if cursor has more rows."""
    retv = False
    if self._cursorResult is not None:
        retv = self._cursorIndex < len(self._cursorResult)
    return retv
```

# CONSTRUCTOR PATTERN

```python
def __init__(self):
    """Initialize DB handler."""
    self._connection = None
    self._pool = None
    self._cursor = None
    self._cursorResult = None
    self._cursorIndex = 0
    self._columns = []
```

RULES:
  - Single line docstring
  - All attributes private (_prefix)
  - Explicit initialization

# METHOD STRUCTURE

```python
def select(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute SELECT query and return list of dict."""
    if not self.hasConnection():
        raise RuntimeError("Not connected")
    retv = []
    cursor = self._connection.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        if rows:
            cols = []
            for col in cursor.description:
                cols.append(col[0])
            for row in rows:
                record = {}
                for i in range(len(cols)):
                    record[cols[i]] = row[i]
                retv.append(record)
    finally:
        cursor.close()
    return retv
```

STRUCTURE:
  1. Single line docstring
  2. Preconditions (guard clauses with raise)
  3. Initialize retv
  4. Main logic (traditional style)
  5. Single return

# CONTEXT MANAGERS

```python
def __enter__(self):
    """Context manager entry."""
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit."""
    self.release()
```

# ERROR HANDLING

PRECONDITIONS:
  - Guard clauses at method start
  - raise RuntimeError/ValueError

TRY/EXCEPT:
  - Single level (no nesting)
  - catch Exception, not bare except
  - Use try/finally for resource cleanup

EXAMPLE:
```python
def query(self, sql: str, params: tuple = None) -> int | None:
    """Execute INSERT, UPDATE, DELETE query."""
    if not self.hasConnection():
        raise RuntimeError("Not connected")
    retv = None
    cursor = self._connection.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        self._connection.commit()
        retv = cursor.rowcount
    except Exception:
        self._connection.rollback()
    finally:
        cursor.close()
    return retv
```

# IMPORTS

```python
from typing import Dict, List, Any
from contextlib import contextmanager

import redis as redisLib

from .DBConnPool import DBConnPool
```

ORDER:
  1. Standard library
  2. Third party
  3. Local imports

ALIAS: Use when name conflicts (redis as redisLib)

# FORBIDDEN PATTERNS

- list_comprehensions: [x for x in items]
- dict_comprehensions: {k: v for k, v in items}
- ternary_expressions: x if cond else y
- multiple_return_statements
- public_attributes (self.attr without _)
- multi_line_docstrings
- nested_try_except
- bare_except (except: without Exception)

# REQUIRED PATTERNS

- single_exit_point with retv variable
- traditional_for_loops with append()
- private_attributes_only (_prefix)
- single_line_docstrings
- camelCase_methods
- guard_clauses_with_raise at method start
- explicit_if_else blocks

# COMPLETE EXAMPLE

```python
from typing import Dict, List, Any

class Redis:
    """Redis client wrapper."""

    def __init__(self):
        """Initialize Redis handler."""
        self._client = None

    def connect(self):
        """Connect to Redis server."""
        if self._client is not None:
            raise RuntimeError("Already connected")
        host = os.getenv("REDIS_HOST")
        port = os.getenv("REDIS_PORT")
        if not host:
            raise RuntimeError("REDIS_HOST not set")
        if not port:
            raise RuntimeError("REDIS_PORT not set")
        self._client = redisLib.Redis(
            host=host,
            port=int(port),
            decode_responses=True
        )

    def disconnect(self):
        """Disconnect from Redis server."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def hasConnection(self) -> bool:
        """Check if connected to Redis."""
        return self._client is not None

    def getKeys(self, pattern: str) -> List[str]:
        """Get all keys matching pattern."""
        retv = []
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        keys = self._client.keys(pattern)
        for key in keys:
            retv.append(key)
        return retv

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, excType, excVal, excTb):
        """Context manager exit."""
        self.disconnect()
```
