MODEL_STYLE pydantic_validation

INTERFACE:
  - base class: pydantic.BaseModel
  - function return type: Dict[str, Any]
  - no framework-specific types

ARCHITECTURE:
  - models handle validation and serialization only
  - no business logic
  - no data transformation

STRUCTURE:

  Model class:
  - naming: <Entity>Model (PascalCase)
  - inheritance: BaseModel
  - docstring: required
  - fields: field_name: type = Field(..., constraints)
  - constraints: ge, le, min_length, max_length, pattern
  - config: extra = "allow" | "forbid" | "ignore"

  get function:
  - purpose: validate input and return serialized dict
  - signature: def get(data: Dict[str, Any]) -> Dict[str, Any]
  - docstring: required
  - body: return <Model>(**data).model_dump()
  - raises: ValidationError on invalid data

MODEL_TYPES:

  Entity model:
  - purpose: validate domain entities
  - naming: <Entity>Model
  - examples: InfoModel, UserModel, OrderModel

  Response model:
  - purpose: standardize service responses
  - naming: ResponseModel
  - fields: err (bool), log (str|None), out (Any|None)
  - location: models/response_model.py (one per module)
  - get signature: def get(err: bool, log: str | None, out: Any | None) -> Dict[str, Any]

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

Entity model (info_model.py):

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

Response model (response_model.py):

```python
from pydantic import BaseModel
from typing import Dict, Any

class ResponseModel(BaseModel):
    """Response standard per tutti i service: {err, log, out}."""
    err: bool
    log: str | None
    out: Any | None

def get(err: bool, log: str | None, out: Any | None) -> Dict[str, Any]:
    """Serializza ResponseModel in dict."""
    retv = ResponseModel(err=err, log=log, out=out)
    return retv.model_dump()
```
