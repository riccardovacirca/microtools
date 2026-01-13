"""Microtools - Python API standardization library.

A thin wrapper around SQLAlchemy and other frameworks providing:
- Database connection pooling and context managers
- JWT token operations
- Password hashing/verification
- Cursor utilities (row-to-dict conversion)
- Pagination calculations
- Service layer patterns
- Query building helpers
- JSON encoding/decoding utilities
- HTTP/API response helpers
- Structured logging
- Configuration management

All functions follow the naming convention: mt_<module>_<functionality>()
"""

__version__ = "1.0.0"

# Database operations
from .mt_db import (
    mt_db_get_engine,
    mt_db_dispose_pools,
    mt_db_get_pool_status,
    mt_db_connection,
    mt_db_cursor,
    mt_db_transaction,
    mt_db_get_connection,
)

# JWT operations
from .mt_jwt import (
    mt_jwt_create_access_token,
    mt_jwt_create_refresh_token,
    mt_jwt_verify_access_token,
)

# Password operations
from .mt_password import (
    mt_password_hash,
    mt_password_verify,
)

# Cursor utilities
from .mt_cursor import (
    mt_cursor_row_to_dict,
    mt_cursor_rows_to_list,
    mt_cursor_to_recordset,
)

# Pagination utilities
from .mt_pagination import (
    mt_pagination_calculate_offset,
    mt_pagination_calculate_pages,
    mt_pagination_validate_params,
    mt_pagination_create_response,
)

# Service pattern utilities
from .mt_service import (
    mt_service_execute,
    mt_service_create_output,
)

# Query building utilities
from .mt_query import (
    mt_query_add_soft_delete_filter,
    mt_query_build_update_clause,
    mt_query_build_search_pattern,
    mt_query_build_multi_field_search,
)

# JSON utilities
from .mt_json import (
    mt_json_encode,
    mt_json_decode,
    mt_json_encode_response,
    mt_json_to_pydantic,
    mt_json_from_pydantic,
    mt_json_safe_decode,
)

# HTTP utilities
from .mt_http import (
    mt_http_success_response,
    mt_http_error_response,
    mt_http_paginated_response,
    mt_http_validate_query_params,
    mt_http_get_status_text,
    MT_HTTP_STATUS_OK,
    MT_HTTP_STATUS_CREATED,
    MT_HTTP_STATUS_BAD_REQUEST,
    MT_HTTP_STATUS_NOT_FOUND,
    MT_HTTP_STATUS_INTERNAL_ERROR,
)

# Logging utilities
from .mt_logging import (
    mt_logging_configure,
    mt_logging_get_logger,
    mt_logging_add_context,
    mt_logging_log_request,
    mt_logging_log_query,
    mt_logging_log_error,
)

# Configuration utilities
from .mt_config import (
    mt_config_load_env,
    mt_config_get,
    mt_config_get_int,
    mt_config_get_bool,
    mt_config_get_list,
    mt_config_require,
    mt_config_validate_schema,
    mt_config_get_all,
)

__all__ = [
    # Database
    "mt_db_get_engine",
    "mt_db_dispose_pools",
    "mt_db_get_pool_status",
    "mt_db_connection",
    "mt_db_cursor",
    "mt_db_transaction",
    "mt_db_get_connection",
    # JWT
    "mt_jwt_create_access_token",
    "mt_jwt_create_refresh_token",
    "mt_jwt_verify_access_token",
    # Password
    "mt_password_hash",
    "mt_password_verify",
    # Cursor
    "mt_cursor_row_to_dict",
    "mt_cursor_rows_to_list",
    "mt_cursor_to_recordset",
    # Pagination
    "mt_pagination_calculate_offset",
    "mt_pagination_calculate_pages",
    "mt_pagination_validate_params",
    "mt_pagination_create_response",
    # Service
    "mt_service_execute",
    "mt_service_create_output",
    # Query
    "mt_query_add_soft_delete_filter",
    "mt_query_build_update_clause",
    "mt_query_build_search_pattern",
    "mt_query_build_multi_field_search",
    # JSON
    "mt_json_encode",
    "mt_json_decode",
    "mt_json_encode_response",
    "mt_json_to_pydantic",
    "mt_json_from_pydantic",
    "mt_json_safe_decode",
    # HTTP
    "mt_http_success_response",
    "mt_http_error_response",
    "mt_http_paginated_response",
    "mt_http_validate_query_params",
    "mt_http_get_status_text",
    "MT_HTTP_STATUS_OK",
    "MT_HTTP_STATUS_CREATED",
    "MT_HTTP_STATUS_BAD_REQUEST",
    "MT_HTTP_STATUS_NOT_FOUND",
    "MT_HTTP_STATUS_INTERNAL_ERROR",
    # Logging
    "mt_logging_configure",
    "mt_logging_get_logger",
    "mt_logging_add_context",
    "mt_logging_log_request",
    "mt_logging_log_query",
    "mt_logging_log_error",
    # Config
    "mt_config_load_env",
    "mt_config_get",
    "mt_config_get_int",
    "mt_config_get_bool",
    "mt_config_get_list",
    "mt_config_require",
    "mt_config_validate_schema",
    "mt_config_get_all",
]
