"""JSON encoding/decoding utilities.

This module provides JSON utilities with automatic handling of datetime,
Pydantic models, and Enum types.

Functions follow naming convention: mt_json_<functionality>()
"""

import json
from datetime import datetime, date
from typing import Any, Dict, Type
from enum import Enum


class _DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime, date, and Enum objects."""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, 'model_dump'):  # Pydantic v2
            return obj.model_dump()
        if hasattr(obj, 'dict'):  # Pydantic v1
            return obj.dict()
        return super().default(obj)


def mt_json_encode(obj: Any, pretty: bool = False) -> str:
    """Serialize object to JSON with automatic handling of datetime, Pydantic models, Enum.

    Args:
        obj: Object to serialize
        pretty: If True, format with indentation for readability

    Returns:
        JSON string

    Example:
        >>> data = {"created_at": datetime.now(), "status": StatusEnum.ACTIVE}
        >>> json_str = mt_json_encode(data)

        >>> # Pretty print
        >>> json_str = mt_json_encode(data, pretty=True)
    """
    if pretty:
        return json.dumps(obj, cls=_DateTimeEncoder, indent=2, ensure_ascii=False)
    return json.dumps(obj, cls=_DateTimeEncoder, ensure_ascii=False)


def mt_json_decode(json_str: str) -> Any:
    """Deserialize JSON string to Python object.

    Args:
        json_str: JSON string to deserialize

    Returns:
        Python object

    Raises:
        ValueError: If JSON is invalid

    Example:
        >>> json_str = '{"name": "John", "age": 30}'
        >>> data = mt_json_decode(json_str)
        >>> print(data['name'])  # John
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")


def mt_json_encode_response(obj: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create standardized response dictionary with data and status.

    Args:
        obj: Object to include in response
        status_code: HTTP status code

    Returns:
        Dictionary with 'data' and 'status_code' keys

    Example:
        >>> response = mt_json_encode_response({"id": 1, "name": "John"}, 200)
        >>> # Returns: {"data": {"id": 1, "name": "John"}, "status_code": 200}
    """
    return {
        "data": obj,
        "status_code": status_code
    }


def mt_json_to_pydantic(json_data: Dict | str, model: Type) -> Any:
    """Convert JSON to Pydantic model with validation.

    Args:
        json_data: JSON string or dict
        model: Pydantic model class

    Returns:
        Validated Pydantic model instance

    Raises:
        ValueError: If validation fails

    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        >>>     name: str
        >>>     age: int
        >>>
        >>> user = mt_json_to_pydantic({"name": "John", "age": 30}, User)
        >>> print(user.name)  # John
    """
    if isinstance(json_data, str):
        json_data = mt_json_decode(json_data)

    try:
        return model(**json_data)
    except Exception as e:
        raise ValueError(f"Validation failed: {str(e)}")


def mt_json_from_pydantic(model: Any, exclude_none: bool = True) -> Dict[str, Any]:
    """Convert Pydantic model to dict/JSON.

    Args:
        model: Pydantic model instance
        exclude_none: If True, exclude None values from output

    Returns:
        Dictionary representation

    Example:
        >>> user = User(name="John", age=30, email=None)
        >>> data = mt_json_from_pydantic(user, exclude_none=True)
        >>> # Returns: {"name": "John", "age": 30} (email excluded)
    """
    if hasattr(model, 'model_dump'):  # Pydantic v2
        return model.model_dump(exclude_none=exclude_none)
    elif hasattr(model, 'dict'):  # Pydantic v1
        return model.dict(exclude_none=exclude_none)
    else:
        raise TypeError(f"Object type {type(model)} is not a Pydantic model")


def mt_json_safe_decode(json_str: str, default: Any = None) -> Any:
    """Deserialize JSON with fallback to default if invalid.

    Args:
        json_str: JSON string to deserialize
        default: Default value to return if JSON is invalid

    Returns:
        Python object or default value

    Example:
        >>> data = mt_json_safe_decode('{"name": "John"}')  # Returns dict
        >>> data = mt_json_safe_decode('invalid json', default={})  # Returns {}
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default
