"""Configuration management utilities.

This module provides utilities for loading and validating configuration
from environment variables with type casting and schema validation.

Functions follow naming convention: mt_config_<functionality>()
"""

import os
from typing import Any, Dict, List, Type


def mt_config_load_env(env_file: str = ".env", override: bool = False) -> None:
    """Load variables from .env file.

    Uses python-dotenv to load environment variables from file.

    Args:
        env_file: Path to .env file (default: ".env")
        override: If True, override existing environment variables

    Example:
        >>> mt_config_load_env(".env")
        >>> mt_config_load_env("/path/to/.env", override=True)
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file, override=override)
    except ImportError:
        pass  # python-dotenv not installed, skip


def mt_config_get(key: str, default: Any = None, cast: Type | None = None) -> Any:
    """Get environment variable with optional type casting and quote stripping.

    Args:
        key: Environment variable name
        default: Default value if not found
        cast: Optional type to cast to (int, float, bool, str)

    Returns:
        Environment variable value (type-casted if specified)

    Example:
        >>> db_host = mt_config_get("DB_HOST", default="localhost")
        >>> db_port = mt_config_get("DB_PORT", default=5432, cast=int)
        >>> debug = mt_config_get("DEBUG", default=False, cast=bool)
    """
    value = os.getenv(key)

    if value is None:
        return default

    # Strip quotes if present
    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    # Cast to specified type
    if cast is not None:
        if cast == bool:
            return value.lower() in ('true', '1', 'yes', 'y', 'on')
        elif cast == int:
            return int(value)
        elif cast == float:
            return float(value)
        elif cast == str:
            return str(value)

    return value


def mt_config_get_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Integer value

    Example:
        >>> port = mt_config_get_int("PORT", default=8000)
    """
    return mt_config_get(key, default=default, cast=int)


def mt_config_get_bool(key: str, default: bool = False) -> bool:
    """Get environment variable as boolean.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Boolean value (true/1/yes/y/on = True, others = False)

    Example:
        >>> debug = mt_config_get_bool("DEBUG", default=False)
        >>> enabled = mt_config_get_bool("FEATURE_ENABLED", default=True)
    """
    return mt_config_get(key, default=default, cast=bool)


def mt_config_get_list(key: str, separator: str = ",", default: List | None = None) -> List[str]:
    """Get environment variable as list of strings.

    Args:
        key: Environment variable name
        separator: List item separator (default: ",")
        default: Default value if not found

    Returns:
        List of strings

    Example:
        >>> allowed_hosts = mt_config_get_list("ALLOWED_HOSTS", default=["localhost"])
        >>> # ALLOWED_HOSTS="host1,host2,host3" -> ["host1", "host2", "host3"]
    """
    value = mt_config_get(key, default=None)

    if value is None:
        return default if default is not None else []

    if isinstance(value, list):
        return value

    # Split by separator and strip whitespace
    return [item.strip() for item in value.split(separator) if item.strip()]


def mt_config_require(key: str, cast: Type | None = None) -> Any:
    """Get required environment variable (raises if missing).

    Args:
        key: Environment variable name
        cast: Optional type to cast to

    Returns:
        Environment variable value

    Raises:
        ValueError: If environment variable is not set

    Example:
        >>> db_url = mt_config_require("DATABASE_URL")
        >>> api_port = mt_config_require("API_PORT", cast=int)
    """
    value = mt_config_get(key, default=None, cast=cast)

    if value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")

    return value


def mt_config_validate_schema(schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Validate configuration against schema.

    Args:
        schema: Configuration schema dictionary

    Returns:
        Dictionary of validated configuration values

    Raises:
        ValueError: If validation fails

    Example:
        >>> schema = {
        ...     "DB_HOST": {"type": str, "required": True},
        ...     "DB_PORT": {"type": int, "required": True, "default": 5432},
        ...     "DEBUG": {"type": bool, "required": False, "default": False}
        ... }
        >>> config = mt_config_validate_schema(schema)
        >>> # Returns: {"DB_HOST": "localhost", "DB_PORT": 5432, "DEBUG": False}
    """
    validated = {}

    for key, rules in schema.items():
        required = rules.get("required", False)
        default = rules.get("default", None)
        cast_type = rules.get("type", str)

        if required:
            validated[key] = mt_config_require(key, cast=cast_type)
        else:
            validated[key] = mt_config_get(key, default=default, cast=cast_type)

    return validated


def mt_config_get_all(prefix: str = "") -> Dict[str, str]:
    """Get all environment variables with optional prefix filter.

    Args:
        prefix: Optional prefix filter (e.g., "DB_")

    Returns:
        Dictionary of environment variables

    Example:
        >>> db_config = mt_config_get_all(prefix="DB_")
        >>> # Returns: {"DB_HOST": "localhost", "DB_PORT": "5432", ...}

        >>> all_config = mt_config_get_all()
        >>> # Returns all environment variables
    """
    if prefix:
        return {k: v for k, v in os.environ.items() if k.startswith(prefix)}
    return dict(os.environ)
