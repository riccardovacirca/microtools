REPOSITORY_STYLE explicit_db_repository

# FILE STRUCTURE

LOCATION: repositories/
NAMING: singular
PATTERN: <entity>_repository.py

EXAMPLES:
  repositories/
  ├── __init__.py
  ├── user_repository.py
  ├── order_repository.py
  └── product_repository.py

# NAMING CONVENTIONS

FUNCTIONS:
  - Simple verbs matching DB operations
  - insert (not create, save, add)
  - select (not get, find, fetch)
  - select_all (not get_all, find_all, list)
  - update (not modify, change)
  - delete (not remove, destroy)

NAMESPACE USAGE:
  ✓ user_repository.select(db, id)
  ✓ user_repository.insert(db, data)
  ✓ order_repository.select_all(db)

  ✗ user_repository.get_user(db, id)
  ✗ user_repository.find_by_id(db, id)
  ✗ user_repository.save_user(db, data)

# DATABASE CLASSES

REQUIRED IMPORTS:
  from api.utils.DB import DB, Record, Recordset
  from api.utils.DBConnPool import DBConnPool

DB CLASS OPERATIONS:
  - db.select(sql, params) -> Record
  - db.select_all(sql, params) -> Recordset
  - db.insert(sql, params) -> int (last_insert_id)
  - db.query(sql, params) -> int (rowcount for UPDATE/DELETE)

CONNECTION PATTERN:
  1. Service acquires: db.acquire(pool)
  2. Repository uses: db.select(sql, params)
  3. Service releases: db.release()

# FUNCTION SIGNATURES

RULE: NO default values in parameters - all parameters required and explicit

def select(db: DB, id: int) -> Record:
    """Select single record by ID."""
    sql = "SELECT * FROM users WHERE id = ?"
    return db.select(sql, (id,))

def select_all(db: DB) -> Recordset:
    """Select all records."""
    sql = "SELECT * FROM users"
    return db.select_all(sql)

def insert(db: DB, data: dict) -> int:
    """Insert record and return last_insert_id."""
    sql = "INSERT INTO users (name, email) VALUES (?, ?)"
    return db.insert(sql, (data["name"], data["email"]))

def update(db: DB, id: int, data: dict) -> int:
    """Update record and return affected rows."""
    sql = "UPDATE users SET name = ?, email = ? WHERE id = ?"
    return db.query(sql, (data["name"], data["email"], id))

def delete(db: DB, id: int) -> int:
    """Delete record and return affected rows."""
    sql = "DELETE FROM users WHERE id = ?"
    return db.query(sql, (id,))

# TRANSACTION PATTERN

For functions that execute multiple queries atomically:

NAMING: verb + _tx suffix
EXAMPLE: create_order_tx, transfer_funds_tx

def create_order_tx(db: DB, order: dict, items: list) -> int:
    """Create order with items in single transaction."""
    # Insert order
    order_sql = "INSERT INTO orders (user_id, total) VALUES (?, ?)"
    order_id = db.insert(order_sql, (order["user_id"], order["total"]))

    # Insert order items
    for item in items:
        item_sql = "INSERT INTO order_items (order_id, product_id, qty) VALUES (?, ?, ?)"
        db.insert(item_sql, (order_id, item["product_id"], item["qty"]))

    return order_id

TRANSACTION HANDLING:
  - DB class _get_cursor() handles commit/rollback automatically
  - All queries in function execute atomically
  - Exception triggers rollback

# RESPONSIBILITY

REPOSITORIES:
  - Execute SQL queries only
  - NO business logic
  - NO validation
  - NO response wrapping
  - Return raw DB results (Record, Recordset, int)

SERVICES HANDLE:
  - Connection acquisition/release
  - Business logic
  - Validation via models
  - Response wrapping via response_model

# LAYER RELATIONSHIPS

CALLED BY: services only
CALLS: DB class methods
NEVER IMPORTED BY: routes, adapters, models

EXAMPLE FLOW:
  service.get()
    -> db.acquire(pool)
    -> user_repository.select(db, id)
       -> db.select(sql, params)
    -> db.release()
    -> validate with model
    -> wrap with response_model

# CONNECTION MANAGEMENT

POOL INITIALIZATION:
  - Done in service layer or app init
  - pool = DBConnPool()

ACQUIRE/RELEASE:
  - Service responsibility
  - db = DB()
  - db.acquire(pool)
  - ... repository calls ...
  - db.release()

REPOSITORY RECEIVES:
  - Already acquired DB instance
  - Repository never manages connections
  - Repository only executes queries

# COMPLETE EXAMPLE

```python
# repositories/user_repository.py
from api.utils.DB import DB, Record, Recordset

def select(db: DB, id: int) -> Record:
    """Select user by ID."""
    sql = "SELECT * FROM users WHERE id = ?"
    return db.select(sql, (id,))

def select_all(db: DB) -> Recordset:
    """Select all users."""
    sql = "SELECT * FROM users"
    return db.select_all(sql)

def select_by_email(db: DB, email: str) -> Record:
    """Select user by email."""
    sql = "SELECT * FROM users WHERE email = ?"
    return db.select(sql, (email,))

def insert(db: DB, data: dict) -> int:
    """Insert user and return ID."""
    sql = "INSERT INTO users (name, email) VALUES (?, ?)"
    return db.insert(sql, (data["name"], data["email"]))

def update(db: DB, id: int, data: dict) -> int:
    """Update user and return affected rows."""
    sql = "UPDATE users SET name = ?, email = ? WHERE id = ?"
    return db.query(sql, (data["name"], data["email"], id))

def delete(db: DB, id: int) -> int:
    """Delete user and return affected rows."""
    sql = "DELETE FROM users WHERE id = ?"
    return db.query(sql, (id,))

def create_with_profile_tx(db: DB, user: dict, profile: dict) -> int:
    """Create user with profile in transaction."""
    # Insert user
    user_sql = "INSERT INTO users (name, email) VALUES (?, ?)"
    user_id = db.insert(user_sql, (user["name"], user["email"]))

    # Insert profile
    profile_sql = "INSERT INTO profiles (user_id, bio) VALUES (?, ?)"
    db.insert(profile_sql, (user_id, profile["bio"]))

    return user_id
```

```python
# services/user_service.py
from api.utils.DB import DB
from api.utils.DBConnPool import DBConnPool
from ..repositories import user_repository
from ..models import user_model, response_model

pool = DBConnPool()

async def get(user_id: int) -> dict:
    """Get user by ID."""
    db = DB()
    try:
        db.acquire(pool)

        # Get raw data from repository
        record = user_repository.select(db, user_id)

        if not record:
            return response_model.get(True, "User not found", None)

        # Validate with model
        validated = user_model.get(dict(record))

        return response_model.get(False, None, validated.model_dump())

    except Exception as e:
        return response_model.get(True, str(e), None)
    finally:
        db.release()
```

# FORBIDDEN

- response_model usage in repository
- Pydantic validation in repository
- Business logic in repository
- Connection pool management in repository
- Verbose names: get_user_by_id, find_user, save_user
- Importing repositories in routes
- Importing repositories in adapters
