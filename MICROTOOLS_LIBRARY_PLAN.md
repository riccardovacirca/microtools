# Microtools Library - Planning Document

## Executive Summary

Transform `/workspace/.prototype/install/api/common` into `microtools` - a support library for FastAPI applications that provides the same role as `microtools.a` for C++ microservices. This library serves as a homogenization layer between underlying frameworks (SQLAlchemy, PyJWT, etc.) and applications, imposing a uniform application style across all API modules.

## Naming Convention

**All public functions follow the pattern: `mt_<file>_<function>`**

Examples:
- File `mt_db.py` → functions: `mt_db_cursor()`, `mt_db_transaction()`, `mt_db_query()`
- File `mt_jwt.py` → functions: `mt_jwt_create_access()`, `mt_jwt_verify_access()`
- File `mt_password.py` → functions: `mt_password_hash()`, `mt_password_verify()`

**Rationale:**
- Prevents namespace conflicts between modules
- Immediately identifies function source/module
- Consistent and predictable naming
- `mt_` prefix clearly identifies microtools library functions

## Current State Analysis

### Existing Structure
```
/workspace/.prototype/install/api/common/
├── __init__.py          # Basic module initialization
├── db.py                # SQLAlchemy connection pooling (447 lines)
├── jwt.py               # JWT token utilities (73 lines)
└── password.py          # Password hashing utilities (52 lines)
```

### Current Usage (mod_contatti)
```python
from ...common.db import db_cursor, db_transaction
```

**Features in use:**
- `db_cursor()` → will become `mt_db_cursor()`
- `db_transaction()` → will become `mt_db_transaction()`

**Features available but not yet used:**
- `db_connection()` → will become `mt_db_connection()`
- `helper_get_pool_config()` → will become `mt_db_pool_config()`
- `helper_get_engine()` → will become `mt_db_engine()`
- `helper_get_pool_status()` → will become `mt_db_pool_status()`
- `helper_dispose_all_pools()` → will become `mt_db_pool_dispose()`
- `get_db_connection()` → will become `mt_db_get_connection()` (legacy)
- JWT functions → will use `mt_jwt_*()` naming
- Password functions → will use `mt_password_*()` naming

## Transformation Goals

### 1. Rename and Restructure
**From:** `/workspace/.prototype/install/api/common/`
**To:** `/workspace/.prototype/install/api/microtools/`

### 2. Library Philosophy
- **Homogenization Layer**: Abstract underlying libraries (SQLAlchemy, PyJWT) with simple wrappers
- **Zero Overhead**: Direct delegation to underlying libraries, no unnecessary abstraction
- **Uniform Style**: Impose consistent coding patterns across all API modules
- **DSL Compliance**: All functions follow Microtools DSL (helper functions with single exit point)

### 3. Scope (Phase 1 - mod_contatti requirements)
Focus on features currently required by `mod_contatti`:
- Database connection pooling
- Context managers for cursor and transaction management
- Pool monitoring and lifecycle management

Future phases will add:
- JWT authentication utilities
- Password hashing utilities
- HTTP client wrappers
- Logging utilities
- Configuration management

## Detailed Implementation Plan

### Phase 1: Rename and Package Structure

#### 1.1 Directory and File Rename
```bash
# Template directory
mv /workspace/.prototype/install/api/common \
   /workspace/.prototype/install/api/microtools

# Active workspace
mv /workspace/api/common \
   /workspace/api/microtools

# Rename files to follow mt_ convention
cd /workspace/.prototype/install/api/microtools
mv db.py mt_db.py
mv jwt.py mt_jwt.py
mv password.py mt_password.py

cd /workspace/api/microtools
mv db.py mt_db.py
mv jwt.py mt_jwt.py
mv password.py mt_password.py
```

#### 1.2 Update __init__.py
Create proper package initialization with explicit exports following `mt_*` naming:

```python
"""Microtools - Support library for FastAPI applications.

This library provides a homogenization layer between underlying frameworks
(SQLAlchemy, PyJWT, etc.) and FastAPI applications, imposing a uniform
application style across all API modules.

Naming Convention:
    All public functions follow the pattern: mt_<file>_<function>

    Examples:
        mt_db_cursor()      - from mt_db.py
        mt_jwt_verify()     - from mt_jwt.py
        mt_password_hash()  - from mt_password.py

Architecture:
    - Zero overhead wrappers around underlying libraries
    - DSL-compliant helper functions (single exit point + exceptions)
    - Connection pooling for optimal performance
    - Context managers for resource management

Similar to microtools.a for C++ microservices, this library standardizes
how FastAPI applications interact with databases, authentication, and
other common services.
"""

# Database pooling and connection management
from .mt_db import (
    # Context managers (primary API)
    mt_db_cursor,
    mt_db_transaction,
    mt_db_connection,

    # Pool lifecycle management
    mt_db_pool_dispose,
    mt_db_pool_status,

    # Engine and configuration
    mt_db_engine,
    mt_db_pool_config,

    # Driver utilities
    mt_db_enabled_drivers,

    # Legacy compatibility (deprecated)
    mt_db_get_connection,
)

# JWT authentication (future phase)
# from .mt_jwt import (
#     mt_jwt_create_access,
#     mt_jwt_create_refresh,
#     mt_jwt_verify_access,
# )

# Password utilities (future phase)
# from .mt_password import (
#     mt_password_hash,
#     mt_password_verify,
# )

__version__ = "1.0.0"
__all__ = [
    # Database
    "mt_db_cursor",
    "mt_db_transaction",
    "mt_db_connection",
    "mt_db_pool_dispose",
    "mt_db_pool_status",
    "mt_db_engine",
    "mt_db_pool_config",
    "mt_db_enabled_drivers",
    "mt_db_get_connection",
]
```

### Phase 2: Refactor Function Names

#### 2.1 Rename All Functions in mt_db.py
Apply `mt_db_*` naming convention to all public functions:

**Function Name Mapping:**
| Old Name | New Name | Notes |
|----------|----------|-------|
| `db_cursor()` | `mt_db_cursor()` | Primary API |
| `db_transaction()` | `mt_db_transaction()` | Primary API |
| `db_connection()` | `mt_db_connection()` | Primary API |
| `helper_get_engine()` | `mt_db_engine()` | Simplified name |
| `helper_get_pool_config()` | `mt_db_pool_config()` | Simplified name |
| `helper_get_pool_status()` | `mt_db_pool_status()` | Simplified name |
| `helper_dispose_all_pools()` | `mt_db_pool_dispose()` | Simplified name |
| `get_enabled_drivers()` | `mt_db_enabled_drivers()` | Simplified name |
| `get_db_connection()` | `mt_db_get_connection()` | Legacy API |
| `get_env()` | `_get_env()` | Private helper |
| `parse_connection_string()` | `_parse_connection_string()` | Private helper |

**Private helpers** (prefixed with `_`) are not exported in `__init__.py` and are for internal use only.

#### 2.2 Rename Functions in mt_jwt.py
**Function Name Mapping:**
| Old Name | New Name | Notes |
|----------|----------|-------|
| `create_access_token()` | `mt_jwt_create_access()` | Shortened |
| `create_refresh_token()` | `mt_jwt_create_refresh()` | Shortened |
| `verify_access_token()` | `mt_jwt_verify_access()` | Shortened |

#### 2.3 Rename Functions in mt_password.py
**Function Name Mapping:**
| Old Name | New Name | Notes |
|----------|----------|-------|
| `hash_password()` | `mt_password_hash()` | |
| `verify_password()` | `mt_password_verify()` | |

### Phase 3: Update Import Paths

#### 3.1 Update mod_contatti Repository
**File:** `/workspace/api/mod_contatti/repositories/contatti_repository.py`

**Before:**
```python
from ...common.db import db_cursor, db_transaction
```

**After:**
```python
from api.microtools import mt_db_cursor, mt_db_transaction
```

**Usage changes:**
```python
# Before
with db_cursor() as cursor:
    cursor.execute("SELECT * FROM contatti")

# After
with mt_db_cursor() as cursor:
    cursor.execute("SELECT * FROM contatti")
```

**Rationale:** Use absolute imports for library-like packages to make them more portable and explicit.

#### 3.2 Update Template
**File:** `/workspace/.prototype/install/api/mod_contatti/repositories/contatti_repository.py`

Apply same import and usage changes to template.

### Phase 4: Documentation Enhancement

#### 4.1 Add README.md
Create `/workspace/.prototype/install/api/microtools/README.md`:

```markdown
# Microtools - FastAPI Support Library

Microtools is a support library for FastAPI applications, providing the same role as `microtools.a` for C++ microservices. It serves as a homogenization layer between underlying frameworks and applications.

## Naming Convention

All public functions follow the pattern: **`mt_<file>_<function>`**

- File `mt_db.py` → functions: `mt_db_cursor()`, `mt_db_transaction()`, `mt_db_query()`
- File `mt_jwt.py` → functions: `mt_jwt_create_access()`, `mt_jwt_verify_access()`
- File `mt_password.py` → functions: `mt_password_hash()`, `mt_password_verify()`

This naming prevents namespace conflicts and makes function origin immediately clear.

## Features

### Database Connection Pooling (mt_db)
- SQLAlchemy Engine with QueuePool (PostgreSQL, MySQL/MariaDB)
- StaticPool for SQLite
- Context managers for automatic resource management
- Pool monitoring and lifecycle management

### Design Principles
1. **Zero Overhead**: Direct delegation to underlying libraries
2. **DSL Compliance**: All helper functions follow Microtools DSL
3. **Single Exit Point**: One return statement per function
4. **Exception-Based Errors**: Raise ValueError for business logic errors
5. **Type Safety**: Full type hints throughout
6. **Consistent Naming**: `mt_<file>_<function>` pattern throughout

## Usage Examples

### Basic Query (Auto-commit)
```python
from api.microtools import mt_db_cursor

with mt_db_cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    rows = cursor.fetchall()
```

### Read-Only Query (No Commit)
```python
from api.microtools import mt_db_cursor

with mt_db_cursor(autocommit=False) as cursor:
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
```

### Atomic Transaction
```python
from api.microtools import mt_db_transaction

with mt_db_transaction() as (conn, cursor):
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100, 1))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100, 2))
    # Both operations commit atomically or both rollback on error
```

### Pool Monitoring
```python
from api.microtools import mt_db_pool_status

status = mt_db_pool_status()
# {
#     "pool_size": 5,
#     "checked_out": 2,
#     "checked_in": 3,
#     "overflow": 0,
#     "total": 5
# }
```

### Application Shutdown
```python
from fastapi import FastAPI
from api.microtools import mt_db_pool_dispose

app = FastAPI()

@app.on_event("shutdown")
async def shutdown_event():
    mt_db_pool_dispose()
```

## Configuration

Add to `.env`:
```bash
# Database connection pool (SQLAlchemy)
DB_POOL_SIZE=5
DB_POOL_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_POOL_ECHO=false
```

## Architecture

### Homogenization Layer
Microtools abstracts underlying libraries without overhead:

```
┌─────────────────────────────────────┐
│   FastAPI Application Modules       │
│   (mod_contatti, mod_users, etc.)   │
└──────────────┬──────────────────────┘
               │
               │ Uniform API
               │
┌──────────────▼──────────────────────┐
│        Microtools Library            │
│  - db.py (connection pooling)        │
│  - jwt.py (authentication)           │
│  - password.py (hashing)             │
└──────────────┬──────────────────────┘
               │
               │ Thin wrappers
               │
┌──────────────▼──────────────────────┐
│    Underlying Frameworks             │
│  - SQLAlchemy Engine                 │
│  - PyJWT                             │
│  - hashlib                           │
└──────────────────────────────────────┘
```

### Benefits
1. **Consistency**: All modules use same patterns
2. **Maintainability**: Update underlying libraries in one place
3. **Testing**: Mock microtools instead of underlying frameworks
4. **Documentation**: Single source of truth for common operations
5. **Portability**: Move between projects easily

## Roadmap

### Phase 1 (Current)
- ✅ Database connection pooling
- ✅ Context managers for cursor/transaction
- ✅ Pool monitoring and lifecycle

### Phase 2 (Future)
- JWT authentication utilities
- Password hashing utilities
- HTTP client wrappers
- Logging utilities
- Configuration management

## Contributing

All code must follow Microtools DSL:
- Helper functions: Single exit point + exceptions
- Type hints on all parameters and returns
- Docstrings with Args/Returns/Raises
- ValueError for business logic errors
```

#### 3.2 Add Module Docstrings
Enhance docstrings in all modules to reference microtools role.

### Phase 4: Testing Strategy

#### 4.1 Unit Tests
Create `/workspace/.prototype/install/api/microtools/tests/`:

```
microtools/tests/
├── __init__.py
├── test_db.py           # Database pooling tests
├── test_jwt.py          # JWT utilities tests (future)
└── test_password.py     # Password utilities tests (future)
```

#### 4.2 Integration Tests
Test microtools with actual mod_contatti operations:
- Verify imports work correctly
- Ensure connection pooling performs as expected
- Validate transaction atomicity

### Phase 5: Update PROJECT.md

Add section documenting microtools library:

```markdown
## Microtools Library

### Purpose
Microtools is a support library for FastAPI applications (Python) serving the same role as `microtools.a` for C++ microservices. It provides a homogenization layer between underlying frameworks (SQLAlchemy, PyJWT, etc.) and application code.

### Location
- **Template:** `/workspace/.prototype/install/api/microtools/`
- **Active workspace:** `/workspace/api/microtools/`

### Naming Convention
All public functions follow the pattern: **`mt_<file>_<function>`**

### Import Pattern
All API modules should import from microtools using absolute imports:

```python
from api.microtools import mt_db_cursor, mt_db_transaction
```

### Modules

#### mt_db.py - Database Connection Pooling
SQLAlchemy Engine-based connection pooling with zero overhead wrappers.

**Primary API:**
- `mt_db_cursor(driver, autocommit)` - Context manager for cursor with auto-commit
- `mt_db_transaction(driver)` - Context manager for atomic transactions
- `mt_db_connection(driver)` - Context manager for raw connection

**Lifecycle Management:**
- `mt_db_pool_dispose()` - Cleanup on shutdown
- `mt_db_pool_status(driver)` - Monitor pool health

**Configuration:**
All pool parameters configurable via environment variables (DB_POOL_SIZE, etc.)

#### mt_jwt.py - JWT Authentication (Future)
JWT token creation and verification utilities.

**API:**
- `mt_jwt_create_access()` - Create access token
- `mt_jwt_create_refresh()` - Create refresh token
- `mt_jwt_verify_access()` - Verify and decode access token

#### mt_password.py - Password Security (Future)
Secure password hashing and verification.

**API:**
- `mt_password_hash()` - Hash password
- `mt_password_verify()` - Verify password against hash

### Design Principles
1. **Zero Overhead**: Direct delegation to underlying libraries
2. **DSL Compliance**: Helper functions follow single exit point pattern
3. **Uniform Style**: Impose consistent patterns across all modules
4. **Type Safety**: Full type hints throughout
5. **Exception-Based**: Raise ValueError for business logic errors
6. **Consistent Naming**: `mt_<file>_<function>` pattern
```

## Migration Path

### Step 1: Rename Directories
```bash
# Template
mv /workspace/.prototype/install/api/common \
   /workspace/.prototype/install/api/microtools

# Active workspace
mv /workspace/api/common \
   /workspace/api/microtools
```

### Step 2: Rename Files
```bash
# Template
cd /workspace/.prototype/install/api/microtools
mv db.py mt_db.py
mv jwt.py mt_jwt.py
mv password.py mt_password.py

# Active workspace
cd /workspace/api/microtools
mv db.py mt_db.py
mv jwt.py mt_jwt.py
mv password.py mt_password.py
```

### Step 3: Refactor Function Names
Update all function names in each module to follow `mt_<file>_<function>` pattern:
- In `mt_db.py`: Rename all functions (see Phase 2.1 for mapping)
- In `mt_jwt.py`: Rename all functions (see Phase 2.2 for mapping)
- In `mt_password.py`: Rename all functions (see Phase 2.3 for mapping)

### Step 4: Update __init__.py
Write new package initialization with explicit exports using new function names.

### Step 5: Update Imports
Change all imports in application modules:
- Update `/workspace/api/mod_contatti/repositories/contatti_repository.py`
- Update `/workspace/.prototype/install/api/mod_contatti/repositories/contatti_repository.py`

**From:**
```python
from ...common.db import db_cursor, db_transaction

with db_cursor() as cursor:
    ...
```

**To:**
```python
from api.microtools import mt_db_cursor, mt_db_transaction

with mt_db_cursor() as cursor:
    ...
```

### Step 6: Add Documentation
- Create README.md in microtools directory
- Update PROJECT.md with microtools section

### Step 7: Test
- Verify imports resolve correctly
- Run existing mod_contatti operations
- Test connection pooling performance
- Verify all renamed functions work correctly

### Step 8: Future Modules
As new API modules are created, they should import from microtools:
```python
from api.microtools import mt_db_cursor, mt_db_transaction
```

## Success Criteria

### Functional Requirements
- ✅ All imports resolve correctly with new package name
- ✅ mod_contatti continues to work without changes (except imports)
- ✅ Connection pooling provides same performance
- ✅ Pool monitoring and lifecycle management functional

### Non-Functional Requirements
- ✅ Zero overhead - no performance degradation
- ✅ Clear documentation in README.md
- ✅ Updated PROJECT.md with microtools section
- ✅ Consistent import patterns across all modules

### Quality Requirements
- ✅ All functions follow DSL (single exit point + exceptions)
- ✅ Complete type hints throughout
- ✅ Comprehensive docstrings with examples
- ✅ Error handling via ValueError

## Risk Assessment

### Low Risk
- Directory rename (straightforward filesystem operation)
- Import path updates (localized changes)
- Documentation additions (non-breaking)

### Medium Risk
- Absolute vs relative imports (could affect module resolution)
  - **Mitigation:** Test imports immediately after changes
  - **Fallback:** Keep relative imports if absolute cause issues

### No Risk
- Core functionality unchanged (db.py remains identical)
- Connection pooling behavior preserved
- No API changes to existing functions

## Timeline Estimate

| Task | Effort | Dependencies |
|------|--------|--------------|
| 1. Rename directories | 5 min | None |
| 2. Rename files (db.py → mt_db.py, etc.) | 5 min | Task 1 |
| 3. Refactor function names in mt_db.py | 30 min | Task 2 |
| 4. Refactor function names in mt_jwt.py | 10 min | Task 2 |
| 5. Refactor function names in mt_password.py | 10 min | Task 2 |
| 6. Update __init__.py | 15 min | Tasks 3-5 |
| 7. Update imports (mod_contatti) | 15 min | Task 6 |
| 8. Create README.md | 30 min | Task 6 |
| 9. Update PROJECT.md | 20 min | Task 8 |
| 10. Testing | 30 min | Tasks 1-7 |
| **Total** | **~170 min** | |

## Post-Migration

### Immediate Next Steps
1. Create `mod_users` or similar module using microtools
2. Validate that new modules can easily adopt microtools patterns
3. Monitor connection pool performance in production

### Future Enhancements
1. Add JWT utilities to microtools (jwt.py)
2. Add password utilities to microtools (password.py)
3. Create HTTP client wrappers for inter-service communication
4. Add logging utilities with structured logging
5. Create configuration management helpers

### Maintenance
- Keep microtools documentation up to date
- Add new utilities as common patterns emerge
- Deprecate utilities that prove unnecessary
- Monitor performance of wrappers

## Appendix A: Current Database Functions

### Context Managers (Primary API)
```python
@contextmanager
def db_cursor(driver: str | None = None, autocommit: bool = True)
    """Context manager for database cursor with pooled connection."""

@contextmanager
def db_transaction(driver: str | None = None)
    """Context manager for atomic transaction with pooled connection."""

@contextmanager
def db_connection(driver: str | None = None)
    """Context manager for raw database connection from pool."""
```

### Pool Management
```python
def helper_get_pool_config() -> Dict[str, Any]
    """Get connection pool configuration from environment."""

def helper_get_engine(driver: str | None = None) -> Engine
    """Get cached SQLAlchemy engine with connection pool."""

def helper_dispose_all_pools()
    """Dispose all connection pools (cleanup on shutdown)."""

def helper_get_pool_status(driver: str | None = None) -> Dict[str, Any]
    """Get connection pool status for monitoring."""
```

### Configuration Utilities
```python
def get_env(key: str, default: str = "") -> str
    """Get environment variable and strip quotes if present."""

def get_enabled_drivers() -> List[str]
    """Get list of enabled database drivers."""

def parse_connection_string(conn_str: str) -> Dict[str, str]
    """Parse database connection string."""
```

### Legacy API
```python
def get_db_connection(driver: str | None = None) -> tuple[Any, str]
    """Get database connection from pool (legacy API compatibility)."""
```

## Appendix B: Import Examples

### Before (common)
```python
# Relative imports
from ...common.db import db_cursor, db_transaction

# Absolute imports
from api.common.db import db_cursor, db_transaction
```

### After (microtools)
```python
# Preferred: Absolute imports from package
from api.microtools import db_cursor, db_transaction

# Also valid: Import from specific module
from api.microtools.db import db_cursor, db_transaction
```

## Appendix C: Package Structure

```
api/
├── microtools/                    # Support library
│   ├── __init__.py                # Package initialization with exports
│   ├── README.md                  # Library documentation
│   ├── db.py                      # Database connection pooling (447 lines)
│   ├── jwt.py                     # JWT utilities (73 lines)
│   ├── password.py                # Password utilities (52 lines)
│   └── tests/                     # Unit tests (future)
│       ├── __init__.py
│       ├── test_db.py
│       ├── test_jwt.py
│       └── test_password.py
│
├── mod_contatti/                  # Application module
│   ├── __init__.py
│   ├── models/
│   ├── repositories/              # Uses microtools.db
│   ├── services/
│   └── routes/
│
├── mod_users/                     # Future application module
│   └── ...                        # Will use microtools
│
└── main.py                        # FastAPI application entry
```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-13
**Author:** Microtools Development Team
**Status:** Ready for Implementation
