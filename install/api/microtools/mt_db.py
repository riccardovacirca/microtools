"""Database connection helpers with SQLAlchemy connection pooling.

This module provides database connection utilities with robust connection pooling
using SQLAlchemy Engine. All connections are managed through a connection pool.
"""
import os
from typing import Dict, Any, List
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool


# ==============================================================================
# Environment Configuration
# ==============================================================================


def __get_env(key: str, default: str = "") -> str:
    """Get environment variable and strip quotes if present.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value with quotes stripped
    """
    value = os.getenv(key, default)
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def _get_enabled_drivers() -> List[str]:
    """Get list of enabled database drivers.

    Returns:
        List of enabled driver names
    """
    drivers = []
    if _get_env("SQLITE3_ENABLED") == "y":
        drivers.append("sqlite3")
    if _get_env("MARIADB_ENABLED") == "y":
        drivers.append("mariadb")
    if _get_env("PGSQL_ENABLED") == "y":
        drivers.append("pgsql")
    return drivers


def __parse_connection_string(conn_str: str) -> Dict[str, str]:
    """Parse database connection string.

    Args:
        conn_str: Connection string (e.g., "host=localhost,port=5432,user=admin")

    Returns:
        Dictionary of connection parameters
    """
    params = {}
    parts = conn_str.split(",") if "," in conn_str else conn_str.split()
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            params[key.strip()] = value.strip()
    return params


# ==============================================================================
# Connection Pool Configuration
# ==============================================================================

_engines: Dict[str, Engine] = {}  # Cache engines per driver


def _get_pool_config() -> Dict[str, Any]:
    """Get connection pool configuration from environment.

    Returns:
        Dictionary with pool configuration parameters

    Environment Variables:
        DB_POOL_SIZE: Number of permanent connections (default: 5)
        DB_POOL_MAX_OVERFLOW: Additional temporary connections (default: 10)
        DB_POOL_TIMEOUT: Timeout in seconds when pool exhausted (default: 30)
        DB_POOL_RECYCLE: Recycle connections after N seconds (default: 3600)
        DB_POOL_PRE_PING: Test connection before use (default: true)
        DB_POOL_ECHO: Log pool operations (default: false)
    """
    return {
        "pool_size": int(_get_env("DB_POOL_SIZE", "5")),
        "max_overflow": int(_get_env("DB_POOL_MAX_OVERFLOW", "10")),
        "pool_timeout": int(_get_env("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(_get_env("DB_POOL_RECYCLE", "3600")),
        "pool_pre_ping": _get_env("DB_POOL_PRE_PING", "true").lower() == "true",
        "echo_pool": _get_env("DB_POOL_ECHO", "false").lower() == "true"
    }


def _create_engine(driver: str) -> Engine:
    """Create SQLAlchemy engine with connection pooling.

    Args:
        driver: Database driver (sqlite3|mariadb|pgsql)

    Returns:
        SQLAlchemy Engine with configured connection pool

    Raises:
        ValueError: If driver unsupported or configuration invalid
    """
    pool_config = _get_pool_config()

    if driver == "sqlite3":
        db_path = _get_env("SQLITE3_CONNECTION", "").replace("file:", "")
        if not db_path:
            raise ValueError("SQLITE3_CONNECTION not set")

        # SQLite: StaticPool ensures single shared connection
        engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo_pool=pool_config["echo_pool"]
        )

        # Enable foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

    elif driver == "pgsql":
        conn_str = _get_env("PGSQL_CONNECTION")
        if not conn_str:
            raise ValueError("PGSQL_CONNECTION not set")

        params = _parse_connection_string(conn_str)
        url = (
            f"postgresql+psycopg2://{params.get('user', '')}:{params.get('password', '')}"
            f"@{params.get('host', 'localhost')}:{params.get('port', '5432')}"
            f"/{params.get('dbname', '')}"
        )

        # PostgreSQL: QueuePool (thread-safe connection pool)
        engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=pool_config["pool_size"],
            max_overflow=pool_config["max_overflow"],
            pool_timeout=pool_config["pool_timeout"],
            pool_recycle=pool_config["pool_recycle"],
            pool_pre_ping=pool_config["pool_pre_ping"],
            echo_pool=pool_config["echo_pool"]
        )

        return engine

    elif driver == "mariadb":
        conn_str = _get_env("MARIADB_CONNECTION")
        if not conn_str:
            raise ValueError("MARIADB_CONNECTION not set")

        params = _parse_connection_string(conn_str)
        url = (
            f"mysql+pymysql://{params.get('user', '')}:{params.get('pass', '')}"
            f"@{params.get('host', 'localhost')}:{params.get('port', '3306')}"
            f"/{params.get('dbname', '')}"
        )

        # MySQL/MariaDB: QueuePool
        engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=pool_config["pool_size"],
            max_overflow=pool_config["max_overflow"],
            pool_timeout=pool_config["pool_timeout"],
            pool_recycle=pool_config["pool_recycle"],
            pool_pre_ping=pool_config["pool_pre_ping"],
            echo_pool=pool_config["echo_pool"]
        )

        return engine

    raise ValueError(f"Unsupported driver: {driver}")


@lru_cache(maxsize=10)
def mt_db_get_engine(driver: str | None = None) -> Engine:
    """Get cached SQLAlchemy engine with connection pool.

    Creates engine on first call and caches it for reuse. All subsequent calls
    return the same engine instance with its connection pool.

    Args:
        driver: Database driver (auto-detect if None)

    Returns:
        Cached SQLAlchemy Engine with connection pool

    Raises:
        ValueError: If configuration invalid or no database enabled
    """
    # Auto-detect driver if not specified
    if driver is None:
        if _get_env("SQLITE3_ENABLED") == "y":
            driver = "sqlite3"
        elif _get_env("MARIADB_ENABLED") == "y":
            driver = "mariadb"
        elif _get_env("PGSQL_ENABLED") == "y":
            driver = "pgsql"
        else:
            raise ValueError("No database enabled. Set SQLITE3_ENABLED, MARIADB_ENABLED, or PGSQL_ENABLED to 'y'")

    if driver not in _engines:
        _engines[driver] = _create_engine(driver)

    return _engines[driver]


def mt_db_dispose_pools():
    """Dispose all connection pools (cleanup on shutdown).

    Closes all connections in all pools and clears the engine cache.
    Call this during application shutdown.

    Example:
        # FastAPI
        @app.on_event("shutdown")
        async def shutdown_event():
            from microtools import mt_db_dispose_pools
            mt_db_dispose_pools()
    """
    for engine in _engines.values():
        engine.dispose()
    _engines.clear()


def mt_db_get_pool_status(driver: str | None = None) -> Dict[str, Any]:
    """Get connection pool status for monitoring.

    Args:
        driver: Database driver (auto-detect if None)

    Returns:
        Dictionary with pool statistics:
        - pool_size: Number of permanent connections
        - checked_out: Connections currently in use
        - checked_in: Available connections in pool
        - overflow: Temporary connections created beyond pool_size
        - total: Total connections (pool_size + overflow)

    Example:
        >>> mt_db_get_pool_status()
        {
            "pool_size": 5,
            "checked_out": 2,
            "checked_in": 3,
            "overflow": 1,
            "total": 6
        }
    """
    try:
        engine = mt_db_get_engine(driver)
        pool = engine.pool

        checked_out = pool.checkedout()
        pool_size = pool.size()
        overflow = pool.overflow() if hasattr(pool, 'overflow') else 0

        return {
            "pool_size": pool_size,
            "checked_out": checked_out,
            "checked_in": pool_size - checked_out,
            "overflow": overflow,
            "total": pool_size + overflow
        }
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# Context Managers for Connection Pool Usage
# ==============================================================================


@contextmanager
def mt_db_connection(driver: str | None = None):
    """Context manager for database connection from pool.

    Retrieves a connection from the pool, yields it, and returns it to the pool
    when done. The connection is NOT closed (socket stays open), just returned
    to the pool for reuse.

    Args:
        driver: Database driver (auto-detect if None)

    Yields:
        Database connection from pool (DBAPI connection object)

    Raises:
        ValueError: If configuration invalid

    Example:
        with mt_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
            rows = cursor.fetchall()
            cursor.close()
    """
    engine = mt_db_get_engine(driver)
    conn = engine.raw_connection()  # Get DBAPI connection from pool
    try:
        yield conn
    finally:
        conn.close()  # Return connection to pool (does NOT close socket)


@contextmanager
def mt_db_cursor(driver: str | None = None, autocommit: bool = True):
    """Context manager for database cursor with pooled connection.

    Retrieves connection from pool, creates cursor, and handles commit/rollback
    automatically. Connection is returned to pool after use.

    Args:
        driver: Database driver (auto-detect if None)
        autocommit: Commit transaction on success (default: True)

    Yields:
        Database cursor from pooled connection

    Raises:
        ValueError: If configuration invalid

    Example:
        # Auto-commit insert
        with mt_db_cursor() as cursor:
            cursor.execute("INSERT INTO table VALUES (?)", (value,))

        # Read-only query (no commit needed)
        with mt_db_cursor(autocommit=False) as cursor:
            cursor.execute("SELECT * FROM table")
            rows = cursor.fetchall()

        # Explicit driver
        with mt_db_cursor(driver="pgsql") as cursor:
            cursor.execute("SELECT version()")
    """
    with mt_db_connection(driver) as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if autocommit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


@contextmanager
def mt_db_transaction(driver: str | None = None):
    """Context manager for atomic database transaction with pooled connection.

    Use for multi-step operations that must be atomic. Transaction commits only
    if context exits normally; any exception triggers rollback. Connection is
    returned to pool after transaction completes.

    Args:
        driver: Database driver (auto-detect if None)

    Yields:
        tuple[Connection, Cursor]: Pooled connection and cursor

    Raises:
        ValueError: If configuration invalid

    Example:
        # Atomic multi-step operation
        with mt_db_transaction() as (conn, cursor):
            cursor.execute("INSERT INTO accounts VALUES (?, ?)", (1, 1000))
            cursor.execute("INSERT INTO transactions VALUES (?, ?)", (1, 'deposit'))
            # Both operations commit atomically, or both rollback on error

        # Money transfer (atomic)
        with mt_db_transaction() as (conn, cursor):
            cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100, 1))
            cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100, 2))
            # Transfer is atomic: both updates succeed or both fail
    """
    with mt_db_connection(driver) as conn:
        cursor = conn.cursor()
        try:
            yield conn, cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


# ==============================================================================
# Legacy API Compatibility (mt_db_get_connection)
# ==============================================================================


def mt_db_get_connection(driver: str | None = None) -> tuple[Any, str]:
    """Get database connection from pool (legacy API compatibility).

    This function provides backward compatibility with code expecting a tuple
    (connection, driver). Uses connection pool internally.

    Args:
        driver: Database driver (auto-detect if None)

    Returns:
        Tuple of (connection, driver_name)

    Raises:
        ValueError: If configuration invalid

    Note:
        Prefer using mt_db_connection(), mt_db_cursor(), or mt_db_transaction()
        context managers for automatic resource management.
    """
    if driver is None:
        if _get_env("SQLITE3_ENABLED") == "y":
            driver = "sqlite3"
        elif _get_env("MARIADB_ENABLED") == "y":
            driver = "mariadb"
        elif _get_env("PGSQL_ENABLED") == "y":
            driver = "pgsql"
        else:
            raise ValueError("No database enabled")

    engine = mt_db_get_engine(driver)
    conn = engine.raw_connection()
    return conn, driver
