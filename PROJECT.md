# Microtools

Microtools è un framework per lo sviluppo di applicazioni modulari basate su
una architettura a 5 livelli: Gateway, GUI, API , Microservice, Database.
Il Gateway e implementato mediante Nginx, la GUI è implementata in Vite/Svelte,
la API in python/FastAPI (Uvicorn/Gunicorn), i Microservice in C++ e il
database supporta i server SQLite3, MariaDB, PostgreSQL a cui si aggiunge il
server Redis.

Il livello Gateway (Nginx) riceve le richieste dai client HTTP e le inoltra al
livello API.

Il livello API è organizzato in moduli Python che implementano una
logica basata su cinque entità applicative: Router, Model, Service, Adapter e
Repository. Il Router implementa il routing delle richieste, i Model la
validazione dei parametri della richiesta mediante Pydantic, i Service
implementano la logica applicativa del modulo, i Repository definiscono la
connessione con il database e gli Adapter implementano una interfaccia con il
livello dei Microservice.

Un modulo del livello API può gestire direttamente la richiesta del client
oppure proxarla mediante un Adapter a un Microservice.

I Microservice sono sviluppati in C++ e sono in esecuzione per tutto il ciclo di
vita dell'applicazione. L'ambiente di sviluppo dei Microservice è basato sul
compilatore gcc e utilizza Cmake. Il framework comprende una libreria di
supporto per lo sviluppo dei Microservice nella cartella lib. Lo scopo di questa
libreria è anche quello di basare lo sviluppo dei Microservice su una logica
comune e semplificata. L'organizzazione del codice dei componenti della libreria
è basata su un DSL che definisce un insieme di vincoli sintattici che enfatizzano
chiarezza e semplicità.

Il sistema è containerizzato e lo stato dei servizzi è gestito mediante S6 il
cui scopo è garantire persistenza in caso di riavvio del container.

## Progetti

Un progetto applicativo basato su Microtools ha la seguente struttura:

- bin: Cartella degli script Bash di gestione del progetto
- logs: Cartella dei logs
- conf: Cartella dei file di configurazione dei servizi
- api: Cartella dei moduli Python che espongono l'API del progetto
- data: Cartella dati. Può contenere il database SQLite3
- database: Cartella dei moduli SQL del progetto
- gui: Cartella dei moduli del frontend Vite/Svelte
- services: Cartella dei Microservice del progetto
- .env: File di configurazione centralizzato

A questi si aggiungono:

- .prototype: Cartella relativa al progetto originale git
- install: Link simbolico alla cartella di installazione del framework
- install.sh e setup.sh: Link simbolici agli script di installazione del framework

La root del progetto e la cartella .prototype hanno un repository .git individuale
per gestire gli aggiornamenti a livello del framework (che vengono condivisi tra
tutte le installazioni) e gli aggiornamenti a livello della singola istanza del
progetto.

La gestione di un progetto applicativo con Microtools avviene mediante l'uso
dello script sh bin/mt. Questo script può essere utilizzato per:

- Start/Stop/Restart di un servizio di sistema o di un microservizio
- Build di un microservizio C++ o del frontend Vite/Svelte
- Verifica/Monitoraggio dello stato di un servizio di sistema o di un microservizio
- Installazione di un modulo SQL di database
- Sincronizzazione dei repository git della webapp e del framework

## Moduli

Il modulo mod_status è un esempio di come i file e le cartelle di un modulo sono
organizzate nel progetto.

Il livello più alto è rappresentato dalla API (Python) che fornisce il routing e
la validazione dell'input. I componenti Database, GUI e Services sono opzionali.

### API

L'entità API di un modulo ha la seguente struttura. La logica è definita nei
services. routes.py, repositories, adapters e models sono di supporto ai
services. Per questo motivo i nomi di queste ultime entità fanno riferimento a
qualcuno dei services definiti. Se richiesto il proxy verso un microservizio C++
questo avviene attraverso un service e mediante un adapter.

```
/workspace/api/mod_<MODULE_NAME>/
|-- adapters/
|   |-- <CPP_MICROSERVICE_NAME>_adapter.py
|   '-- ...
|-- models/
|   |-- <SERVICE_NAME>_models.py
|   '-- ...
|-- repositories/
|   |-- <SERVICE_NAME>_repository.py
|   '-- ...
|-- services/
|   |-- <SERVICE_NAME>_service.py
|   '-- ...
|-- routes.py
`-- workflow.md
```

#### Service

Questa entità applicativa usa due tipi di funzione: funzioni applicative e
funzioni helper.

Le funzioni applicative sono definite come segue:

```json
{
  "name": "application-function-python",
  "description": "Python application-layer functions with disciplined input/output validation via Pydantic, output dict pattern, bool return, and structured error handling.",
  "role": "Expert Python developer for service-layer code. Enforce structured approach with automatic input validation, output validation via BaseModel, output parameter for results, bool return for status, and no exception propagation.",
  "template": {
    "function_declaration": {
      "syntax": "@validate_arguments\ndef <function_name>(<input_params>, output: Dict[str, Any] = Field(...)) -> bool:",
      "constraints": {
        "decorator": "@validate_arguments from Pydantic for automatic input validation",
        "naming": "descriptive, application-level name",
        "parameters": "all input arguments must have type hints; scalar parameters use Field(...) constraints; output last parameter",
        "field_constraints": "inline Field(...) for scalar parameters, types like EmailStr allowed for implicit validation",
        "output_parameter": "output: Dict[str, Any] = Field(...) for storing validated results",
        "return_type": "always bool",
        "modern_syntax": "use | for unions instead of Optional",
        "multiline": "parameters can be multiline for readability"
      },
      "example": "@validate_arguments\ndef application_process_order(\n    order_data: OrderData,\n    user_email: EmailStr,\n    apply_discount: bool = Field(...),\n    output: Dict[str, Any] = Field(...)\n) -> bool:"
    },
    "input_policy": {
      "scalar_params": "use Field(...) with constraints for inline validation",
      "implicit_types": "EmailStr, constr, PositiveInt, conlist, etc. for implicit validation",
      "complex_models": "define BaseModel in models.py only if structure is nested/complex",
      "example": "user_email: EmailStr, age: int = Field(..., ge=18)"
    },
    "output_policy": {
      "model": "all function outputs validated via dedicated BaseModel",
      "pattern": "create instance of output model, call model.model_dump(), update output dict",
      "validation": "raises ValidationError if values are invalid",
      "error_handling": "caught in except block, sets output['error'], function returns False",
      "example": "class ResultModel(BaseModel): total: float = Field(..., ge=0); status: str = Field(..., min_length=1)\nresult = ResultModel(total=total, status=status); output.update(result.model_dump())"
    },
    "pydantic_integration": {
      "required": true,
      "imports": "from pydantic import validate_arguments, Field, BaseModel",
      "models_for_complex_structures": {
        "required": true,
        "location": "models.py",
        "import_syntax": "from models import ModelName",
        "example": "# In models.py\nclass OrderItem(BaseModel): quantity: int = Field(..., ge=1); price: float = Field(..., ge=0)\nclass OrderData(BaseModel): items: List[OrderItem] = Field(..., min_items=1); shipping_address: str = Field(..., min_length=10)"
      },
      "field_usage": {
        "required": true,
        "syntax": "param: Type = Field(..., <constraint>=<value>)",
        "location": "inline in function parameters",
        "examples": [
          "user_email: EmailStr",
          "age: int = Field(..., ge=18)",
          "apply_discount: bool = Field(...)",
          "output: Dict[str, Any] = Field(...)"
        ]
      }
    },
    "blocks": {
      "error_class": {
        "required": true,
        "syntax": "class Err: calculation: bool = False; enrichment: bool = False",
        "purpose": "track business logic errors, not validation"
      },
      "globals": {
        "required": true,
        "syntax": "retv: bool = False\nresult: Dict[str, Any] = {}\nerror: str | None = None"
      },
      "try_block": {
        "required": true,
        "input_validation": "automatic via Pydantic (@validate_arguments + Field or types like EmailStr)",
        "processing_logic": "set Err flags only for business logic errors; raise ValueError() WITHOUT message; populate result dict",
        "success_marker": "retv = True at end if processing succeeds"
      },
      "except_block": {
        "required": true,
        "syntax": "except Exception as e:\n    if Err.calculation: error = 'Calculation failed'\n    elif Err.enrichment: error = 'Enrichment failed'\n    else: error = str(e) or 'Unknown error'",
        "constraints": "handles validation and business errors, sets error variable only, no raise, no return"
      },
      "single_exit_point": {
        "required": true,
        "syntax": "if retv: output.update(result)\nelse: output['error'] = error\nreturn retv"
      }
    },
    "structural_constraints": {
      "mandatory_block_order": [
        "error_class",
        "globals",
        "try block",
        "except block",
        "single_exit_point"
      ],
      "forbidden_constructs": [
        "return inside try or except",
        "raise exceptions outside try block",
        "manual validation for parameters handled by Pydantic",
        "Err flags for validation errors",
        "BaseModel classes inline in function file",
        "import models from files other than models.py"
      ],
      "required_constructs": [
        "@validate_arguments decorator",
        "BaseModel classes in models.py for complex structures",
        "Field() inline for all scalar parameters",
        "output parameter as last argument",
        "bool return type",
        "Err class with class attributes only",
        "retv variable initialized to False",
        "Err flags only for business logic errors",
        "retv = True on success",
        "error variable assignment in except block",
        "conditional output population",
        "single return retv at end"
      ]
    },
    "type_system": {
      "constraints": {
        "all_parameters": "must have type hints",
        "output_parameter": "Dict[str, Any]",
        "return_type": "bool",
        "modern_syntax": "use | for unions",
        "no_type_aliases": "use Dict[str, Any] directly",
        "built_in_only": "Dict, List, int, str, bool, float"
      }
    },
    "error_handling_philosophy": {
      "validation_errors": "handled automatically via Pydantic; manual only for complex structures",
      "logical_errors": "Err flags + raise ValueError() without message, messages mapped in except block",
      "exception_handling": "all exceptions caught in except, populate output['error'], return single retv"
    },
    "semantic_notes": {
      "input_output_validation": "input validated inline via Field or implicit Pydantic types; output validated via BaseModel",
      "Err_class": "tracks only business logic errors, not validation",
      "retv_variable": "controls flow (False=failure, True=success)",
      "output_parameter": "dict populated after validation",
      "bool_return": "indicates success/failure",
      "single_exit": "one return at end; exceptions never escape"
    },
    "summary": [
      "@validate_arguments decorator for automatic input validation",
      "Scalar input parameters: Field() inline or implicit Pydantic types (EmailStr, etc.)",
      "Complex/nested input structures: BaseModel in models.py",
      "Output validated via dedicated BaseModel, updated in output dict",
      "Err class tracks business logic errors, not validation",
      "retv = True if processing succeeds",
      "except block sets output['error'], no return, no raise",
      "single return retv at end",
      "mirrors C-style application function pattern",
      "strong type safety, automatic validation, clear separation of concerns"
    ]
  }
}
```

Lo skeleton di una funzione applicativa basato sul DSL è il seguente:

```python
# application.py
from typing import Dict, Any
from pydantic import validate_arguments, Field
from models import OrderResult

@validate_arguments
def application_process_order(
    order_id: int = Field(..., ge=1),
    user_email: str = Field(..., min_length=5),
    apply_discount: bool = Field(...),
    output: Dict[str, Any] = Field(...)
) -> bool:
    """Process an order, populating output dict and returning success status."""
    
    # Inner Err class for business logic errors
    class Err:
        calculation: bool = False
        enrichment: bool = False

    # Globals
    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        # === Business logic processing ===
        # Dummy logic for example
        subtotal = 100.0
        discount_amount = 10.0 if apply_discount else 0.0
        
        if discount_amount < 0 or discount_amount > subtotal:
            Err.calculation = True
            raise ValueError()  # no message

        total = subtotal - discount_amount
        item_count = 5
        status = "processed"

        # === Validate and populate output via Pydantic model ===
        result_model = OrderResult(total=total, item_count=item_count, status=status)
        result.update(result_model.model_dump())

        # Mark success
        retv = True

    except Exception as e:
        if Err.calculation:
            error = "Discount calculation error"
        elif Err.enrichment:
            error = "Data enrichment error"
        else:
            error = str(e) or "Unknown error"

    # Single exit point
    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv
```

Le funzione helper sono definite come segue:

```json
{
  "name": "dsl-helper-python",
  "description": "Create, review, or refactor Python helper functions. Utility-level, strongly typed, with single exit point and explicit exception handling.",
  "role": "Expert Python developer for service-layer or support code. Enforce minimal but disciplined DSL for helpers focused on type safety, validation, and predictable behavior.",
  "template": {
    "function_declaration": {
      "syntax": "@validate_arguments\ndef <helper_function_name>(<param>: <Type> = Field(...), ...) -> <ReturnType>:",
      "constraints": {
        "decorator": "@validate_arguments from pydantic for automatic validation",
        "naming": "descriptive helper name, prefixed with helper_ if desired",
        "type_hints": "mandatory for all parameters and return type",
        "field_constraints": "use Field(...) from pydantic for validation constraints",
        "no_optional_params": "all parameters required, use Field(...) to enforce",
        "modern_syntax": "use | for unions if needed"
      },
      "examples": {
        "with_constraints": "@validate_arguments\ndef helper_parse_integer(text: str = Field(..., min_length=1)) -> int:",
        "simple": "@validate_arguments\ndef helper_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:"
      }
    },
    "pydantic_integration": {
      "required": true,
      "imports": "from pydantic import validate_arguments, Field",
      "decorator": "@validate_arguments",
      "field_usage": {
        "syntax": "param: Type = Field(..., <constraint>=<value>)",
        "constraints": [
          "min_length: minimum string length",
          "max_length: maximum string length",
          "ge: greater than or equal (numbers)",
          "le: less than or equal (numbers)",
          "...: required field marker"
        ],
        "examples": [
          "text: str = Field(..., min_length=1)",
          "username: str = Field(..., min_length=3, max_length=50)",
          "age: int = Field(..., ge=0, le=150)"
        ]
      },
      "benefits": [
        "automatic validation of parameter types",
        "automatic validation of constraints",
        "clear error messages for invalid inputs",
        "reduces boilerplate validation code"
      ]
    },
    "return_semantics": {
      "pattern": "return typed value or raise exception",
      "constraints": {
        "specific_return_type": "return type must be specific (int, str, Dict, etc.)",
        "no_optional": "avoid Optional/None returns, use exceptions instead",
        "no_silent_failure": "failures are communicated via exceptions",
        "single_exit_point": "one return statement at end of function"
      },
      "exception_types": [
        "ValueError: for invalid values or failed validation",
        "TypeError: for type mismatches",
        "KeyError: for missing dictionary keys",
        "FileNotFoundError: for missing files",
        "specific exceptions appropriate to the failure"
      ]
    },
    "validation_and_logic": {
      "validation": {
        "approach": "raise exceptions for validation failures",
        "syntax": "if <invalid_condition>:\n    raise ValueError(\"descriptive message\")",
        "no_early_return": "don't use early returns, raise exception instead",
        "examples": [
          "if value < -2147483648 or value > 2147483647:\n    raise ValueError(\"Integer out of 32-bit range\")",
          "if not path.exists() or not path.is_file():\n    raise FileNotFoundError(f\"File not found: {file_path}\")"
        ]
      },
      "main_logic": {
        "syntax": "# local variables\n# processing\nreturn result",
        "constraints": {
          "minimal_scope": "declare variables close to usage",
          "atomic_operations": "operations should be atomic where possible",
          "single_exit": "one return statement at the end"
        }
      },
      "no_try_except": {
        "rule": "helpers should not catch exceptions internally",
        "rationale": "let exceptions propagate to caller",
        "exceptions_to_rule": "only when converting low-level exceptions to domain exceptions",
        "example_allowed": "try:\n    with open(path, 'r') as f:\n        data = json.load(f)\nexcept (OSError, json.JSONDecodeError) as e:\n    raise ValueError(f\"Failed to load JSON: {e}\")"
      }
    },
    "error_handling": {
      "philosophy": "explicit exceptions, no silent failures",
      "forbidden": [
        "returning None to indicate failure",
        "returning False to indicate failure",
        "catching and suppressing exceptions",
        "generic Exception() without message",
        "try/except for control flow"
      ],
      "allowed": [
        "raising specific exceptions (ValueError, TypeError, etc.)",
        "descriptive error messages",
        "exception chaining when converting low-level exceptions"
      ],
      "patterns": {
        "validation_failure": "raise ValueError(\"descriptive message\")",
        "type_error": "raise TypeError(\"expected type X, got Y\")",
        "missing_resource": "raise FileNotFoundError(f\"File not found: {path}\")",
        "key_missing": "raise KeyError(f\"Key '{key}' not found in data\")"
      }
    },
    "structure": {
      "single_exit_point": {
        "required": true,
        "description": "exactly one return statement at function end",
        "no_early_returns": "do not use early returns",
        "raise_for_errors": "use raise for error cases, not return"
      },
      "minimal_blocks": {
        "description": "keep helper logic concise and focused",
        "no_complex_flow": "avoid complex nested logic",
        "prefer_simple": "simple linear flow with validation then processing"
      }
    },
    "type_system": {
      "constraints": {
        "all_parameters": "must have type hints",
        "return_type": "must have return type hint",
        "modern_syntax": "use | for unions if needed (rare in helpers)",
        "specific_types": "use specific types (Dict[str, Any], not just dict)",
        "no_any_only": "avoid using Any alone, prefer Dict[str, Any], List[Any], etc."
      },
      "examples": {
        "correct": [
          "def helper_parse_integer(text: str) -> int:",
          "def helper_load_json(path: str) -> Dict[str, Any]:",
          "def helper_validate_email(email: str) -> bool:"
        ],
        "incorrect": [
          "def helper_parse(text):  # missing type hints",
          "def helper_load_json(path: str) -> dict:  # use Dict[str, Any]",
          "def helper_parse_integer(text: str) -> int | None:  # use exception not None"
        ]
      }
    },
    "forbidden_constructs": {
      "list": [
        "early returns (return before function end)",
        "multiple return points",
        "returning None to indicate failure",
        "returning False to indicate failure",
        "Optional return types (use exceptions)",
        "catching exceptions without re-raising or converting",
        "silent error suppression",
        "complex try/except blocks for control flow",
        "error flags or error state management"
      ]
    },
    "required_constructs": {
      "list": [
        "@validate_arguments decorator",
        "Field constraints for parameters where appropriate",
        "complete type hints for all parameters and return",
        "specific exception raising for failures",
        "descriptive error messages",
        "single return statement at end"
      ]
    },
    "key_principles": {
      "explicit_over_implicit": "failures are explicit via exceptions, not implicit via None/False",
      "type_safety": "strong typing with Pydantic validation",
      "single_exit": "predictable control flow with one return",
      "fail_fast": "validate early and raise exceptions immediately",
      "no_silent_failure": "all failures are communicated via exceptions",
      "minimal_structure": "helpers stay small and focused"
    },
    "common_use_cases": {
      "examples": [
        {
          "use_case": "parsing and validation",
          "pattern": "validate input -> parse -> validate result -> return",
          "exception": "ValueError for invalid input or parse failure"
        },
        {
          "use_case": "data conversion",
          "pattern": "check input type -> convert -> validate result -> return",
          "exception": "ValueError or TypeError for conversion failure"
        },
        {
          "use_case": "file operations",
          "pattern": "check file exists -> read -> validate content -> return",
          "exception": "FileNotFoundError, ValueError for invalid content"
        },
        {
          "use_case": "data extraction",
          "pattern": "validate data structure -> extract -> return",
          "exception": "KeyError for missing keys, ValueError for invalid structure"
        }
      ]
    },
    "difference_from_application_functions": {
      "helper_functions": {
        "error_class": false,
        "retv_variable": false,
        "error_variable": false,
        "try_except_wrapper": false,
        "error_flags": false,
        "single_exit_via_exception": true,
        "pydantic_validation": true,
        "direct_exceptions": true
      },
      "application_functions": {
        "error_class": true,
        "retv_variable": true,
        "error_variable": true,
        "try_except_wrapper": true,
        "error_flags": true,
        "single_exit_via_raise_and_return": true,
        "pydantic_validation": "optional",
        "centralized_error_mapping": true
      }
    },
    "complete_example": {
      "description": "Complete helper function example",
      "code": "@validate_arguments\ndef helper_parse_integer(text: str = Field(..., min_length=1)) -> int:\n    \"\"\"Parse string to 32-bit integer.\n    \n    Args:\n        text: String to parse\n        \n    Returns:\n        Parsed integer\n        \n    Raises:\n        ValueError: If text is not valid integer or out of range\n    \"\"\"\n    value = int(text)  # raises ValueError if invalid\n    if value < -2147483648 or value > 2147483647:\n        raise ValueError(\"Integer out of 32-bit range\")\n    return value"
    },
    "summary_for_ai_agents": [
      "Helper functions use @validate_arguments decorator",
      "All parameters use Field() with constraints",
      "Failures communicated via specific exceptions (ValueError, TypeError, etc.)",
      "No Optional return types - use exceptions instead",
      "Single return statement at function end",
      "No early returns, no multiple exit points",
      "Strong typing with complete type hints",
      "Minimal structure, focused logic",
      "No try/except unless converting low-level exceptions",
      "Deviation from these principles is non-compliant"
    ]
  }
}
```

Lo skeleton di una funzione helper basato sul DSL è il seguente:

```python
from typing import Dict, Any
from pydantic import validate_arguments, Field

@validate_arguments
def helper_example(
    text: str = Field(..., min_length=1),
    limit: int = Field(..., ge=0)
) -> Dict[str, Any]:
    # validazione logica
    if limit == 0:
        raise ValueError("limit must be greater than zero")

    # logica principale
    result: Dict[str, Any] = {}

    # result["key"] = value

    return result
```

#### Models

I models Pydantic sono usati per la validazione dell'input e dell'output secondo
il seguente DSL:

```json
{
  "name": "pydantic-application-dsl",
  "description": "Regole per l'uso idiomatico di Pydantic nelle funzioni applicative Python.",
  "role": "Imporre validazione automatica di input e output per funzioni applicative, con output vincolato a un modello Pydantic.",
  "input_policy": {
    "parameters": "Tutti i parametri devono avere type hints",
    "validation": "Usare Field(...) per vincoli inline o tipi Pydantic specifici (EmailStr, constr, PositiveInt, ecc.)",
    "models": "Solo se necessario per ragioni di semplificazione, definire un modello BaseModel per input complessi",
    "example": "user_email: EmailStr, age: int = Field(..., ge=18)"
  },
  "output_policy": {
    "model": "Ogni funzione applicativa deve avere un modello BaseModel dedicato per l'output",
    "validation": "I valori dell'output vengono validati creando un'istanza del modello prima di aggiornare il dizionario output",
    "error_handling": "Se la validazione fallisce, l'errore viene registrato in output['error'] e la funzione ritorna False",
    "update_pattern": "output.update(result.model_dump())",
    "example": {
      "model": "class ResultModel(BaseModel): total: float = Field(..., ge=0); status: str = Field(..., min_length=1)",
      "usage_in_function": "result = ResultModel(total=total, status=status); output.update(result.model_dump())"
    }
  },
  "function_pattern": {
    "decorator": "@validate_arguments",
    "signature": "def <function_name>(<input_params>, output: Dict[str, Any] = Field(...)) -> bool",
    "structure": [
      "definire classe Err con attributi booleani per errori di business",
      "inizializzare retv=False, error=None",
      "try:",
      "    logica di business",
      "    validazione output tramite modello BaseModel",
      "    retv=True se tutto valido",
      "except ValidationError o Exception:",
      "    impostare error",
      "dopo try/except: se retv=True aggiornare output con dati validati, altrimenti output['error']=error",
      "return retv"
    ]
  },
  "principles": [
    "Input validati automaticamente con Pydantic",
    "Output validato sempre tramite modello BaseModel dedicato",
    "Eccezioni di validazione catturate e convertite in errori nell'output",
    "Funzione applicativa ha un singolo punto di ritorno (bool)",
    "Pattern applicativo isola logica, errori di business e validazione"
  ],
  "benefits": [
    "Separazione chiara tra input, logica e output",
    "Validazione consistente e tipizzata",
    "Riduzione di errori di runtime",
    "Output sempre conforme allo standard definito"
  ]
}
```

Ecco lo skeleton di un model di output:

```python
from pydantic import BaseModel, Field
from typing import List

class OrderResult(BaseModel):
    """Output model for application function processing an order."""
    total: float = Field(..., ge=0)                 # totale dell'ordine, >= 0
    item_count: int = Field(..., ge=0)             # numero di articoli, >= 0
    status: str = Field(..., min_length=1)         # stato dell'elaborazione
```

#### Routes

```
Da documentare...
```

#### Repositories

```
Da documentare...
```

#### Adapters

```
Da documentare...
```

#### Workflow

```
Da documentare...
```

### Database

```
/workspace/database/mod_status
|-- /workspace/database/mod_status/mariadb
|   |-- /workspace/database/mod_status/mariadb/data.sql
|   |-- /workspace/database/mod_status/mariadb/schema_install.sql
|   `-- /workspace/database/mod_status/mariadb/schema_uninstall.sql
|-- /workspace/database/mod_status/mariadb_install.sql
|-- /workspace/database/mod_status/mariadb_uninstall.sql
|-- /workspace/database/mod_status/postgres
|   |-- /workspace/database/mod_status/postgres/data.sql
|   |-- /workspace/database/mod_status/postgres/schema_install.sql
|   `-- /workspace/database/mod_status/postgres/schema_uninstall.sql
|-- /workspace/database/mod_status/postgres_install.sql
|-- /workspace/database/mod_status/postgres_uninstall.sql
|-- /workspace/database/mod_status/sqlite3
|   |-- /workspace/database/mod_status/sqlite3/data.sql
|   |-- /workspace/database/mod_status/sqlite3/schema_install.sql
|   `-- /workspace/database/mod_status/sqlite3/schema_uninstall.sql
|-- /workspace/database/mod_status/sqlite3_install.sql
`-- /workspace/database/mod_status/sqlite3_uninstall.sql
```

### GUI

```
/workspace/gui/src/mod_status
|-- /workspace/gui/src/mod_status/Info.svelte
|-- /workspace/gui/src/mod_status/Layout.svelte
`-- /workspace/gui/src/mod_status/index.html

/workspace/services/mod_status
|-- /workspace/services/mod_status/.env.example
|-- /workspace/services/mod_status/CMakeLists.txt
`-- /workspace/services/mod_status/src
    `-- /workspace/services/mod_status/src/main.cpp
```

### Microservices

I microservices di supporto all'applicazione rispettano il seguente DSL:

```json
{
  "dsl_name": "microtools_cpp_style",
  "version": "1.4",
  "description": "DSL per definire lo stile di codifica C++98 potenziato con sintassi esplicita",
  
  "language_profile": {
    "base_standard": "C++98",
    "allowed_modern_features": [
      {
        "feature": "std::unique_ptr",
        "standard": "C++11",
        "reason": "Gestione memoria automatica e sicura - OBBLIGATORIO per allocazione heap",
        "usage": "SEMPRE per allocazione dinamica, mai raw pointers"
      },
      {
        "feature": "std::variant",
        "standard": "C++17",
        "reason": "Type-safe union per valori eterogenei",
        "usage": "Per rappresentare valori di tipi diversi"
      },
      {
        "feature": "#pragma once",
        "standard": "compiler extension",
        "reason": "Header guard più pulito e conciso",
        "usage": "Preferito rispetto a #ifndef/#define tradizionale"
      },
      {
        "feature": "auto keyword",
        "standard": "C++11",
        "reason": "EVITATO - preferire tipi espliciti",
        "usage": "Non usare, sempre esplicito"
      }
    ]
  },
  
  "syntax_rules": {
    "explicitness": {
      "principle": "Sintassi totalmente esplicita - no costrutti impliciti",
      "rules": [
        {
          "rule": "constructor_initialization",
          "style": "explicit_body_assignment",
          "forbidden": "Constructor() : member_(value) {}",
          "required": "Constructor() {\n  member_ = value;\n}",
          "reason": "Assegnamento visibile nel corpo"
        },
        {
          "rule": "type_declaration",
          "style": "explicit_types",
          "forbidden": "auto value = getValue();",
          "required": "std::string value = getValue();",
          "reason": "Tipo sempre dichiarato esplicitamente"
        }
      ]
    },
    
    "formatting": {
      "style": "compact_readable",
      "rules": [
        {
          "rule": "indentation",
          "style": "2_spaces",
          "example": "void method() {\n  if (condition) {\n    doSomething();\n  }\n}",
          "forbidden": "tabs, 4 spaces",
          "reason": "Indentazione a 2 spazi"
        },
        {
          "rule": "no_blank_lines_in_function_body",
          "style": "compact",
          "forbidden": "void method() {\n  int x = 5;\n\n  return x * 2;\n}",
          "required": "void method() {\n  int x = 5;\n  return x * 2;\n}",
          "reason": "Corpo funzione compatto senza righe vuote"
        },
        {
          "rule": "empty_functions",
          "style": "single_line",
          "example": "Constructor() {}",
          "reason": "Funzioni vuote su una riga"
        },
        {
          "rule": "simple_methods",
          "style": "single_line_when_trivial",
          "example": "void clear() { buffer_->clear(); }",
          "reason": "Metodi semplici compatti"
        },
        {
          "rule": "braces",
          "style": "egyptian",
          "example": "if (condition) {\n  code;\n}",
          "reason": "Graffa apertura su stessa riga"
        },
        {
          "rule": "reference_symbol_placement",
          "style": "llvm",
          "required": "const std::string &name",
          "forbidden": "const std::string& name",
          "reason": "Simbolo & accanto alla variabile (stile LLVM), non al tipo"
        }
      ]
    },
    
    "documentation": {
      "principle": "Ogni funzione pubblica nei file .h DEVE essere documentata con Doxygen",
      "rules": [
        {
          "rule": "mandatory_doxygen_comments",
          "scope": "header files (.h)",
          "target": "all public methods and functions",
          "style": "doxygen_javadoc",
          "required_tags": ["@brief", "@param (se presenti parametri)", "@return (se non void)"],
          "example": "/**\n * @brief Connects to database\n * @param connection_string DSN connection string\n */\nvoid connect(const std::string& connection_string);",
          "reason": "Documentazione chiara e generabile automaticamente"
        },
        {
          "rule": "no_implementation_comments",
          "scope": "implementation files (.cpp)",
          "principle": "Niente commenti nei file .cpp, solo codice",
          "reason": "Documentazione solo nei file .h, codice autoesplicativo"
        }
      ]
    },
    
    "naming_conventions": {
      "classes": {
        "style": "PascalCase",
        "example": "DB, File, Logger"
      },
      "methods": {
        "style": "snake_case",
        "example": "connect(), cursor_open()"
      },
      "private_members": {
        "style": "snake_case_with_trailing_underscore",
        "example": "connection_, cursor_"
      },
      "namespaces": {
        "style": "lowercase_short",
        "example": "mt"
      }
    }
  },
  
  "design_principles": {
    "simplicity_first": {
      "prefer_typedef_over_wrapper": "typedef quando classe base ha già tutti i metodi",
      "wrapper_only_when_needed": "classe wrapper solo per logica custom o RAII"
    },
    
    "memory_management": {
      "mandatory_unique_ptr": {
        "principle": "OBBLIGATORIO unique_ptr per allocazione heap",
        "forbidden": "Type* ptr = new Type();",
        "required": "std::unique_ptr<Type> ptr = std::make_unique<Type>();"
      },
      "no_manual_delete": "Mai delete esplicito, unique_ptr gestisce tutto",
      "explicit_assignment": "Assegnamento nel corpo costruttore: ptr_ = std::make_unique<T>();"
    },
    
    "parameter_passing": {
      "default": "const reference per oggetti: const Type&",
      "output": "reference per output: Type&",
      "primitives": "by value per int, bool, char",
      "forbidden": "by value per std::string, containers, oggetti"
    }
  },
  
  "anti_patterns": {
    "avoid": [
      {
        "pattern": "initialization_list",
        "forbidden": "Class() : ptr_(value) {}",
        "reason": "Assegnamento nascosto"
      },
      {
        "pattern": "auto_keyword",
        "forbidden": "auto value = func();",
        "reason": "Tipo non esplicito"
      },
      {
        "pattern": "raw_pointers_ownership",
        "forbidden": "Type* owned_;",
        "reason": "Usare unique_ptr"
      },
      {
        "pattern": "pass_by_value_objects",
        "forbidden": "void func(std::string s)",
        "reason": "Usare const reference"
      },
      {
        "pattern": "blank_lines_in_functions",
        "forbidden": "void f() {\n  x = 1;\n\n  return x;\n}",
        "reason": "Corpo compatto senza righe vuote"
      },
      {
        "pattern": "undocumented_public_methods",
        "forbidden": "void connect(const std::string &dsn);",
        "required": "/**\n * @brief Connects to database\n * @param dsn Connection string\n */\nvoid connect(const std::string &dsn);",
        "reason": "Doxygen obbligatorio nei file .h"
      },
      {
        "pattern": "wrong_reference_symbol_placement",
        "forbidden": "void func(const Type& arg)",
        "required": "void func(const Type &arg)",
        "reason": "Stile LLVM: & accanto alla variabile"
      }
    ]
  },
  
  "examples": {
    "documented_header": {
      "file": "File.h",
      "code": "#pragma once\n\n#include <string>\n\nnamespace mt {\n\n/**\n * @brief File I/O handler\n */\nclass File {\npublic:\n  /**\n   * @brief Constructor\n   * @param path File path\n   */\n  File(const std::string& path);\n  \n  /**\n   * @brief Opens the file\n   */\n  void open();\n  \n  /**\n   * @brief Reads entire file content\n   * @return File content as string\n   */\n  std::string read();\n  \nprivate:\n  std::string path_;\n};\n\n}  // namespace mt"
    },
    
    "compact_implementation": {
      "file": "File.cpp",
      "code": "#include \"File.h\"\n#include <fstream>\n\nnamespace mt {\n\nFile::File(const std::string& path) {\n  path_ = path;\n}\n\nvoid File::open() {\n  stream_ = std::make_unique<std::fstream>();\n  stream_->open(path_.c_str());\n  if (!stream_->is_open()) {\n    throw std::runtime_error(\"Cannot open: \" + path_);\n  }\n}\n\nstd::string File::read() {\n  std::ostringstream buffer;\n  buffer << stream_->rdbuf();\n  return buffer.str();\n}\n\n}  // namespace mt"
    }
  }
}
```

### Gestione dei moduli

I moduli possono essere esportati e importati tramite archivi compressi:

- `mt module export -n <nome_modulo>`: Esporta un modulo in un archivio tar.gz
  contenente i componenti api, database, gui e service. L'archivio include un
  file module.json con i metadati e le dipendenze Python del modulo. L'archivio
  viene salvato in /workspace/dist/modules/.

- `mt module import -n <nome_modulo> [--force]`: Importa un modulo da un archivio
  tar.gz. Il comando blocca l'import se il modulo esiste già in /workspace/api,
  a meno che non venga usata l'opzione --force. Al termine dell'import vengono
  suggerite le operazioni di setup necessarie (installazione dipendenze Python,
  build del microservizio C++, installazione schema database).
