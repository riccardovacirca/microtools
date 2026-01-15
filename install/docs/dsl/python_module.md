MODULE_STYLE layered_servlet_architecture

# DIRECTORY STRUCTURE

```
mod_<name>/
├── routes.py                    # HTTP handlers
├── adapters/                    # Plural: contains multiple adapters
│   ├── __init__.py
│   └── <entity>_adapter.py     # Singular: one entity per file
├── services/                    # Plural: contains multiple services
│   ├── __init__.py
│   └── <entity>_service.py     # Singular: one entity per file
├── models/                      # Plural: contains multiple models
│   ├── __init__.py
│   ├── <entity>_model.py       # Singular: one entity per file
│   └── response_model.py       # Standard response wrapper
└── repositories/                # Optional: for database access
    ├── __init__.py
    └── <entity>_repository.py  # Singular: one entity per file
```

# NAMING CONVENTIONS

DIRECTORIES:
  - Always plural: adapters, services, models, repositories
  - Rationale: contains multiple files

FILES:
  - Always singular: info_adapter.py, user_service.py, data_model.py
  - Pattern: <entity>_<layer>.py
  - Rationale: one entity per file

FUNCTIONS:
  - Simple verbs: get, set, create, update, delete (services/adapters)
  - Database operations: select, select_all, insert, update, delete (repositories)
  - NO verbose names: get_user_data, fetch_info, retrieve_data, find_by_id, save_user
  - Rationale: namespace provides context

NAMESPACE USAGE:
  - Import module: from ..adapters import info_adapter
  - Call function: info_adapter.get()
  - Result: clear context from namespace
  - Example: info_service.get() vs get_info()
  - Benefit: info_service.get(), user_service.get() - same function name, different namespace

FUNCTION PARAMETERS:
  - NO default values in function signatures
  - All parameters must be explicit
  - Rationale: explicit over implicit, prevents arbitrary usage
  - Forbidden: def func(a, b=None, c=default)
  - Required: def func(a, b, c)

# LAYER RELATIONSHIPS

FLOW:
  routes -> services -> (adapters | repositories) + models

ROUTES:
  - Imports: services only
  - Calls: info_service.get()
  - Returns: JSONResponse with service output
  - Responsibility: HTTP layer

SERVICES:
  - Imports: adapters, repositories, models, response_model
  - Calls: info_adapter.get(), user_repository.select(db, id), info_model.get(data), response_model.get()
  - Returns: response_model dict
  - Responsibility: orchestration + business logic + connection management

ADAPTERS:
  - Imports: httpx, external libs
  - Calls: external HTTP services
  - Returns: raw dict from external system
  - Responsibility: I/O only (external HTTP)

REPOSITORIES:
  - Imports: DB, Record, Recordset
  - Calls: db.select(), db.insert(), db.query()
  - Returns: Record, Recordset, int
  - Responsibility: SQL execution only (database)

MODELS:
  - Imports: pydantic
  - Purpose: validation only
  - Returns: validated Pydantic model

# IMPORT PATTERNS

STYLE: namespace import

Routes:
  from .services import info_service
  Usage: info_service.get()

Services:
  from ..adapters import info_adapter
  from ..repositories import user_repository
  from ..models import info_model, response_model
  Usage: info_adapter.get(), user_repository.select(db, id), info_model.get(data), response_model.get()

FORBIDDEN:
  - from .services.info_service import get
  - from ..adapters.info_adapter import *
  - from ..repositories import user_repository in routes
  - Direct adapter or repository import in routes

# DATA FLOW

REQUEST PATH (external HTTP):
  1. routes.info_handler() receives HTTP request
  2. calls info_service.get()
  3. service calls info_adapter.get() for raw external data
  4. service calls info_model.get(data) for validation
  5. service calls response_model.get(err, log, out)
  6. routes returns JSONResponse(data, status_code)

REQUEST PATH (database):
  1. routes.user_handler() receives HTTP request
  2. calls user_service.get(id)
  3. service acquires DB: db.acquire(pool)
  4. service calls user_repository.select(db, id) for raw DB data
  5. service calls user_model.get(data) for validation
  6. service calls response_model.get(err, log, out)
  7. service releases DB: db.release()
  8. routes returns JSONResponse(data, status_code)

RESPONSE PATH:
  (external_system | database) -> (adapter | repository) -> service (validate) -> service (wrap) -> routes (HTTP)

VALIDATION POINT: services layer only
ERROR HANDLING: services layer only
CONNECTION MANAGEMENT: services layer only

# RESPONSE MODEL

MANDATORY: yes
LOCATION: models/response_model.py
USAGE: all services must return response_model.get()

STRUCTURE:
  - err: bool (True if error, False if success)
  - log: str|None (error message or None)
  - out: Any|None (data or None)

SUCCESS: response_model.get(False, None, validated_data)
ERROR: response_model.get(True, "error message", None)

# FUNCTION NAMING

CRUD OPERATIONS (services/adapters):
  - Create: create (not create_user)
  - Read: get (not get_data, fetch_info)
  - Update: update (not update_record)
  - Delete: delete (not remove_item)

CRUD OPERATIONS (repositories):
  - Create: insert (not save, add, create)
  - Read one: select (not get, find)
  - Read all: select_all (not get_all, find_all)
  - Update: update (not modify, change)
  - Delete: delete (not remove, destroy)
  - Transactions: verb + _tx suffix (create_order_tx, transfer_funds_tx)

NAMESPACE EXAMPLES:
  ✓ user_service.get()                    (clear: getting user via service)
  ✗ user_service.get_user()               (redundant: user already in namespace)

  ✓ cache_adapter.set()                   (clear: setting cache via adapter)
  ✗ cache_adapter.set_value()             (redundant: value implied by cache context)

  ✓ user_repository.select(db, id)        (clear: selecting user from DB)
  ✗ user_repository.get_user(db, id)      (wrong: use select for DB operations)

  ✓ user_repository.insert(db, data)      (clear: inserting user to DB)
  ✗ user_repository.save_user(db, data)   (wrong: use insert for DB operations)

  ✓ order_repository.create_order_tx(db, order, items)  (clear: transactional)
  ✗ order_repository.create_order(db, order, items)     (missing _tx suffix)

BENEFITS:
  - Consistent naming across modules
  - info_service.get(), user_service.get(), data_service.get()
  - user_repository.select(), order_repository.select()
  - Easy to remember: entity + layer + action
  - Namespace provides full context

# FORBIDDEN PATTERNS

CIRCULAR IMPORTS:
  - Adapters cannot import services
  - Repositories cannot import services
  - Models cannot import adapters or repositories
  - Maintain strict hierarchy

DIRECT ACCESS FROM ROUTES:
  - Routes must never import adapters
  - Routes must never import repositories
  - All data access via services only

BYPASSING RESPONSE MODEL:
  - Services must never return raw data
  - Always wrap in response_model.get()

CONNECTION MANAGEMENT IN REPOSITORY:
  - Repositories must never manage DB connections
  - Repositories only receive DB instance
  - Services handle acquire/release

VERBOSE NAMING:
  - No get_user_by_id (use get with id parameter)
  - No fetch_all_users (use get or list)
  - No create_new_user (use create)
  - No find_by_email (use select with email parameter)
  - No save_user (use insert for repositories)

# EXAMPLE MODULE (with database)

```
mod_users/
├── routes.py
│   └── from .services import user_service
│       └── user_service.get(id)
│
├── services/
│   └── user_service.py
│       └── from ..repositories import user_repository
│       └── from ..models import user_model, response_model
│       └── from api.utils.DB import DB
│       └── from api.utils.DBConnPool import DBConnPool
│       └── def get(id):
│           db = DB()
│           db.acquire(pool)
│           ... user_repository.select(db, id)
│           db.release()
│           return response_model.get(...)
│
├── repositories/
│   └── user_repository.py
│       └── from api.utils.DB import DB, Record, Recordset
│       └── def select(db, id): return db.select(sql, (id,))
│       └── def insert(db, data): return db.insert(sql, params)
│
└── models/
    ├── user_model.py
    │   └── def get(data): return UserModel(**data)
    └── response_model.py
        └── def get(err, log, out): return {...}
```

CALL CHAIN (database):
  routes.user_handler()
    -> user_service.get(id)
      -> db.acquire(pool)
      -> user_repository.select(db, id) [raw Record]
      -> user_model.get(dict(record)) [validated]
      -> response_model.get(False, None, validated) [wrapped]
      -> db.release()
    -> JSONResponse(data, 200)

CALL CHAIN (external HTTP):
  routes.info_handler()
    -> info_service.get()
      -> info_adapter.get() [raw data from HTTP]
      -> info_model.get(data) [validated]
      -> response_model.get(False, None, validated) [wrapped]
    -> JSONResponse(data, 200)
