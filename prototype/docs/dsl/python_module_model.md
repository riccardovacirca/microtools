MODEL_STYLE pydantic_validation

INTERFACE:
  - base class: pydantic.BaseModel
  - function return type: Dict[str, Any]
  - no framework-specific types

ARCHITECTURE:
  - models handle validation and serialization only
  - no business logic
  - no data transformation

FUNCTION NAMING:
  - get: for INPUT models (validate incoming data)
  - set: for OUTPUT models (construct outgoing data)

  INPUT (get):
  - data from DB, cache, request body, adapter response
  - examples: model.get(row), model.getCreate(data), model.getUpdate(data)

  OUTPUT (set):
  - data going back to caller (response)
  - examples: response_model.set(err, log, out)

STRUCTURE:

  Model class:
  - naming: <Entity>Model (PascalCase)
  - inheritance: BaseModel
  - docstring: required
  - fields: field_name: type = Field(..., constraints)
  - constraints: ge, le, min_length, max_length, pattern
  - config: extra = "allow" | "forbid" | "ignore"

  get function (INPUT):
  - purpose: validate input and return serialized dict
  - signature: def get(data: Dict[str, Any]) -> Dict[str, Any]
  - docstring: required
  - body: return <Model>(**data).model_dump()
  - raises: ValidationError on invalid data

  set function (OUTPUT):
  - purpose: construct output and return serialized dict
  - signature: def set(...params) -> Dict[str, Any]
  - docstring: required
  - body: retv = <Model>(...params); return retv.model_dump()

MODEL_TYPES:

  Entity model (INPUT):
  - purpose: validate domain entities
  - naming: <Entity>Model
  - function: get
  - examples: InfoModel, ContattoModel, ListaModel

  Response model (OUTPUT):
  - purpose: standardize service responses
  - naming: ResponseModel
  - function: set
  - fields: err (bool), log (str|None), out (Any|None)
  - location: models/response_model.py (one per module)
  - set signature: def set(err: bool, log: str | None, out: Any | None) -> Dict[str, Any]

FIELD_TYPES:
  - primitive: int, str, bool, float
  - optional: type | None
  - complex: List[type], Dict[str, Any]

FUNCTION_PARAMETERS:
  - NO default values allowed
  - all parameters explicit
  - forbidden: def get(data=None)
  - required: def get(data)

FORBIDDEN:
  - business logic in model
  - data transformation
  - external calls (HTTP, DB, cache)
  - default parameter values
  - returning model instance (always return dict)

EXAMPLES:

Entity model - INPUT (info_model.py):

```python
from pydantic import BaseModel, Field
from typing import Dict, Any

class InfoModel(BaseModel):
    """Dati status applicazione."""
    id: int = Field(..., ge=1)
    version: str = Field(..., min_length=1)
    created_at: str = Field(..., min_length=1)
    updated_at: str = Field(..., min_length=1)

    class Config:
        extra = "allow"

def get(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida e restituisce InfoModel."""
    return InfoModel(**data).model_dump()
```

Response model - OUTPUT (response_model.py):

```python
from pydantic import BaseModel
from typing import Dict, Any

class ResponseModel(BaseModel):
    """Response standard per tutti i service: {err, log, out}."""
    err: bool
    log: str | None
    out: Any | None

def set(err: bool, log: str | None, out: Any | None) -> Dict[str, Any]:
    """Costruisce e serializza ResponseModel."""
    retv = ResponseModel(err=err, log=log, out=out)
    return retv.model_dump()
```
