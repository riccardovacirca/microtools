PYTHON_CLASS_STYLE microtools_python_class

# NAMING CONVENTIONS

CLASSES:
  - PascalCase: DB, DBConnPool, Env, Record, Recordset
  - Clear, descriptive names

METHODS:
  - camelCase: connect(), cursorOpen(), selectAll(), isConnected()
  - Simple verbs for operations
  - Exception: __init__, __enter__, __exit__ (Python special methods)

ATTRIBUTES:
  - Public: camelCase (connection, cursor, pool, cursorResult)
  - Private: _camelCase (_cursorResult, _currentRowIndex, _lastRowcount)

# FORMATTING

INDENTATION:
  - 2 spaces for ALL Python code (classes, functions, modules)
  - No tabs
  - Mandatory across entire codebase

BLANK LINES:
  - 1 blank line between methods
  - 2 blank lines between classes
  - NO blank lines inside method bodies (compact style)

DOCSTRINGS:
  - Mandatory for classes and public methods
  - Google style format
  - Single line for simple methods: """Brief description."""
  - Multi-line for complex methods with Args and Returns

# TYPE HINTS

MANDATORY:
  - All parameters must have type hints
  - All return types must be specified
  - Use typing module: Dict, List, Optional, Any
  - Modern syntax: use | for unions (Python 3.10+) or Optional

EXAMPLES:
  ✓ def query(self, sql: str, params: Optional[tuple]) -> int:
  ✓ def selectAll(self, sql: str, params: Optional[tuple]) -> Recordset:
  ✗ def query(self, sql, params):  # missing type hints
  ✗ def select_all(self, ...):  # wrong: snake_case instead of camelCase

# FUNCTION PARAMETERS

RULE: NO default values in method parameters

FORBIDDEN:
  ✗ def query(self, sql: str, params: Optional[tuple] = None)
  ✗ def __init__(self, driver: str = None)
  ✗ def get(self, key: str, default: str = '')
  ✗ def cursor_open(self, ...):  # wrong: snake_case

REQUIRED:
  ✓ def query(self, sql: str, params: Optional[tuple])
  ✓ def __init__(self, driver: Optional[str])
  ✓ def get(self, key: str, default: str)
  ✓ def cursorOpen(self, ...):  # correct: camelCase

RATIONALE:
  - Explicit over implicit
  - Prevents arbitrary usage patterns
  - Callers must explicitly pass all parameters

EXCEPTION:
  - __init__ can have no parameters if initialization is empty
  - Example: def __init__(self): (no params OK)

# CONSTRUCTOR PATTERN

```python
def __init__(self):
  """Initialize DB handler."""
  self.connection = None
  self.cursor = None
  self.pool = None
```

RULES:
  - Explicit assignment in body
  - No initialization list shortcuts
  - All attributes initialized explicitly

# CONTEXT MANAGERS

Use @contextmanager decorator for simple patterns:

```python
@contextmanager
def _get_cursor(self):
  """Context manager for cursor operations."""
  cursor = self.connection.cursor()
  try:
    yield cursor
    self.connection.commit()
  except Exception:
    self.connection.rollback()
    raise
  finally:
    cursor.close()
```

Use __enter__/__exit__ for RAII patterns:

```python
def __enter__(self):
  return self

def __exit__(self, exc_type, exc_val, exc_tb):
  self.release()
```

# ERROR HANDLING

EXCEPTIONS:
  - Raise specific exceptions (RuntimeError, ValueError, TypeError)
  - Descriptive error messages
  - No silent failures

VALIDATION:
  - Validate early
  - Fail fast
  - Check state before operations

EXAMPLES:
```python
if not self.isConnected():
  raise RuntimeError("Not connected to database")

if not sql:
  raise ValueError("sql cannot be empty")
```

# PRIVATE METHODS

NAMING:
  - Prefix with single underscore
  - camelCase: _getCursor(), _rowToDict(), _parseConnectionString()

PURPOSE:
  - Internal implementation details
  - Not part of public API

# CLASS DESIGN PRINCIPLES

SINGLE RESPONSIBILITY:
  - Each class has one clear purpose
  - DB: database operations
  - DBConnPool: connection pooling
  - Env: environment variable management

ENCAPSULATION:
  - Hide implementation details
  - Use private attributes and methods
  - Expose clean public API

COMPOSABILITY:
  - Prefer composition over inheritance
  - Utility classes should be standalone

# IMPORTS

STRUCTURE:
```python
# Standard library
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

# Third party
import redis
import httpx

# Local imports
from .DBConnPool import DBConnPool
```

TYPING MODULE:
  - Always import typing types used
  - Dict, List, Optional, Any are most common

# COMPLETE EXAMPLE

```python
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

class Record(Dict[str, Any]):
  """Wrapper for single database record."""
  pass

class DB:
  """Database connection and query handler with connection pool support."""

  def __init__(self):
    """Initialize DB handler."""
    self.connection = None
    self.cursor = None
    self.pool = None
    self._cursor_result = None
    self._current_row_index = 0

  def acquire(self, pool):
    """Acquire connection from pool.

    Args:
      pool: DBConnPool instance
    """
    if self.connection is not None:
      raise RuntimeError("Already connected")
    self.pool = pool
    self.connection = pool.acquire()

  def query(self, sql: str, params: Optional[tuple]) -> int:
    """Execute SQL query that modifies data.

    Args:
      sql: SQL query (INSERT, UPDATE, DELETE)
      params: Query parameters

    Returns:
      Number of affected rows
    """
    if not self.isConnected():
      raise RuntimeError("Not connected to database")
    with self._getCursor() as cursor:
      if params:
        cursor.execute(sql, params)
      else:
        cursor.execute(sql)
      return cursor.rowcount

  def isConnected(self) -> bool:
    """Check if connected to database."""
    return self.connection is not None and self.pool is not None

  @contextmanager
  def _getCursor(self):
    """Context manager for cursor operations."""
    cursor = self.connection.cursor()
    try:
      yield cursor
      self.connection.commit()
    except Exception:
      self.connection.rollback()
      raise
    finally:
      cursor.close()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.release()
```

# FORBIDDEN PATTERNS

- default_parameter_values (def func(param=value))
- mutable_default_arguments (def func(lst=[]))
- blank_lines_inside_methods
- missing_type_hints
- undocumented_public_methods
- implicit_any_types
- catch_all_exceptions_without_reraising
- snake_case_methods (use camelCase instead)
- verbose_method_names (getUserById instead of get(userId))

# REQUIRED PATTERNS

- complete_type_hints for all parameters and returns
- explicit_parameters (no defaults)
- docstrings_for_public_api
- specific_exceptions with descriptive messages
- compact_method_bodies (no blank lines)
- private_attributes_with_underscore
- context_managers for resource management
- early_validation and fail_fast
