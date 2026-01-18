MODULE_STYLE layered_servlet_architecture

# ENTITY AUTONOMY

PRINCIPLE: Ogni entità applicativa del modulo deve essere autonoma e minimamente accoppiata.

DEFINITION: Un'entità è un insieme coeso di file (model, service, repository, adapter) che gestisce una specifica risorsa del dominio.

EXAMPLES: contatto, lista, campagna, user, order

RULES:
  - Ogni entità ha il proprio file model con la propria funzione response()
  - Nessun response_model.py centralizzato condiviso tra entità
  - Service di un'entità importa solo il model della propria entità
  - Cross-entity references solo quando strettamente necessario

RATIONALE: Minimo accoppiamento, massima coesione, facilità di manutenzione e testing

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
│   └── <entity>_model.py       # Singular: one entity per file (includes response())
└── repositories/                # Optional: for database access
    ├── __init__.py
    └── <entity>_repository.py  # Singular: one entity per file
```

NOTE: No response_model.py centralizzato. Ogni <entity>_model.py contiene la propria funzione response().

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
  - Imports: adapters, repositories, entity-specific models
  - Calls: contatto_adapter.get(), contatto_repository.select(db, id), contatto_model.ContattoOutput(**data), contatto_model.response()
  - Returns: entity_model.response() dict
  - Responsibility: orchestration + business logic + connection management
  - Entity isolation: ogni service importa solo il model della propria entità

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
  from .services import contatto_service, lista_service
  Usage: contatto_service.get()

Services (entity-specific):
  from ..adapters import contatto_adapter
  from ..repositories import contatto_repository
  from ..models import contatto_model
  Usage: contatto_adapter.get(), contatto_repository.select(db, id), contatto_model.response()

ENTITY ISOLATION:
  - Rule: ogni service importa solo il model della propria entità
  - Correct: contatto_service.py imports contatto_model only
  - Forbidden: contatto_service.py imports lista_model (cross-entity)

FORBIDDEN:
  - from .services.contatto_service import get
  - from ..adapters.contatto_adapter import *
  - from ..repositories import contatto_repository in routes
  - from ..models import response_model (centralizzato)
  - Direct adapter or repository import in routes
  - Cross-entity model imports (unless strictly necessary)

# DATA FLOW

REQUEST PATH (external HTTP):
  1. routes.contatto_handler() receives HTTP request
  2. calls contatto_service.get()
  3. service calls contatto_adapter.get() for raw external data
  4. service calls contatto_model.ContattoOutput(**data) for validation
  5. service calls contatto_model.response(err, log, out)
  6. routes returns JSONResponse(data, status_code)

REQUEST PATH (database):
  1. routes.contatto_handler() receives HTTP request
  2. calls contatto_service.get(id)
  3. service acquires DB: db.acquire(pool)
  4. service calls contatto_repository.select(db, id) for raw DB data
  5. service calls contatto_model.ContattoOutput(**dict(row)) for validation
  6. service calls contatto_model.response(False, None, output.model_dump())
  7. service releases DB: db.release()
  8. routes returns JSONResponse(data, status_code)

RESPONSE PATH:
  (external_system | database) -> (adapter | repository) -> service (validate via entity_model) -> service (wrap via entity_model.response) -> routes (HTTP)

VALIDATION POINT: services layer only
ERROR HANDLING: services layer only
CONNECTION MANAGEMENT: services layer only
ENTITY ISOLATION: each service uses only its own entity_model

# RESPONSE FUNCTION (per-entity)

MANDATORY: yes
LOCATION: models/<entity>_model.py (within each entity model file)
USAGE: each service returns its entity_model.response()

STRUCTURE:
  - err: bool (True if error, False if success)
  - log: str|None (error message or None)
  - out: Any|None (data or None)

SUCCESS: contatto_model.response(False, None, validated_data)
ERROR: contatto_model.response(True, "error message", None)

EXAMPLE (models/contatto_model.py):
```python
from typing import Any

def response(err: bool, log: str | None, out: Any | None) -> dict:
    """Costruisce risposta standardizzata per contatto."""
    return {"err": err, "log": log, "out": out}

class ContattoInput(BaseModel): ...
class ContattoOutput(BaseModel): ...
```

FORBIDDEN: models/response_model.py centralizzato condiviso tra entità

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

CENTRALIZED RESPONSE MODEL:
  - No models/response_model.py shared across entities
  - Each entity has its own response() function in its model file
  - Forbidden: from ..models import response_model

CROSS-ENTITY MODEL IMPORTS:
  - Services should not import models from other entities
  - Forbidden: contatto_service.py importing lista_model
  - Exception: only when strictly necessary for cross-entity operations

BYPASSING RESPONSE FUNCTION:
  - Services must never return raw data
  - Always wrap in entity_model.response()

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
mod_risorse/
├── routes.py
│   └── from .services import contatto_service, lista_service
│       └── contatto_service.get(id)
│
├── services/
│   └── contatto_service.py
│       └── from ..repositories import contatto_repository
│       └── from ..models import contatto_model  # entity-specific only!
│       └── from api.utils.DB import DB
│       └── from api.utils.DBConnPool import DBConnPool
│       └── async def get(pool, id):
│           db = DB()
│           db.acquire(pool)
│           row = contatto_repository.select(db, id)
│           output = contatto_model.ContattoOutput(**dict(row))
│           db.release()
│           return contatto_model.response(False, None, output.model_dump())
│
├── repositories/
│   └── contatto_repository.py
│       └── from api.utils.DB import DB, Record, Recordset
│       └── def select(db, id): return db.select(sql, (id,))
│       └── def insert(db, data): return db.insert(sql, params)
│
└── models/
    └── contatto_model.py  # includes response() + Input/Output models
        └── def response(err, log, out): return {"err": err, "log": log, "out": out}
        └── class ContattoInput(BaseModel): ...
        └── class ContattoOutput(BaseModel): ...
```

NOTE: No response_model.py! Each entity model (contatto_model.py, lista_model.py, etc.)
      contains its own response() function.

CALL CHAIN (database):
  routes.contatto_handler()
    -> contatto_service.get(pool, id)
      -> db.acquire(pool)
      -> contatto_repository.select(db, id) [raw Record]
      -> contatto_model.ContattoOutput(**dict(row)) [validated]
      -> contatto_model.response(False, None, output.model_dump()) [wrapped]
      -> db.release()
    -> JSONResponse(data, 200)

CALL CHAIN (external HTTP):
  routes.contatto_handler()
    -> contatto_service.get()
      -> contatto_adapter.get() [raw data from HTTP]
      -> contatto_model.ContattoOutput(**data) [validated]
      -> contatto_model.response(False, None, output.model_dump()) [wrapped]
    -> JSONResponse(data, 200)
