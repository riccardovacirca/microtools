"""Database connection helpers.

This module provides database connection utilities for SQLite3, PostgreSQL, and MySQL.
"""
import os
import sqlite3
from typing import Dict, Tuple, Any, List


def get_env(key: str, default: str = "") -> str:
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


def get_enabled_drivers() -> List[str]:
    """Get list of enabled database drivers.

    Returns:
        List of enabled driver names
    """
    drivers = []
    if get_env("SQLITE3_ENABLED") == "y":
        drivers.append("sqlite3")
    if get_env("MARIADB_ENABLED") == "y":
        drivers.append("mariadb")
    if get_env("PGSQL_ENABLED") == "y":
        drivers.append("pgsql")
    return drivers


def get_db_connection(driver: str = None) -> Tuple[Any, str]:
    """Get database connection based on environment configuration.

    Args:
        driver: Database driver (sqlite3|mariadb|pgsql).
                If None, uses first enabled driver.

    Returns:
        Tuple of (connection, db_driver)

    Raises:
        ValueError: If driver is unsupported or no drivers enabled
    """
    # Auto-detect driver if not specified
    if driver is None:
        if get_env("SQLITE3_ENABLED") == "y":
            driver = "sqlite3"
        elif get_env("MARIADB_ENABLED") == "y":
            driver = "mariadb"
        elif get_env("PGSQL_ENABLED") == "y":
            driver = "pgsql"
        else:
            raise ValueError("No database enabled. Set SQLITE3_ENABLED, MARIADB_ENABLED, or PGSQL_ENABLED to 'y'")

    if driver == "sqlite3":
        db_connection_str = get_env("SQLITE3_CONNECTION")
        if not db_connection_str:
            raise ValueError("SQLITE3_CONNECTION not set")
        db_path = db_connection_str.replace("file:", "")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn, driver

    elif driver == "pgsql":
        import psycopg2
        from psycopg2.extras import RealDictCursor
        db_connection_str = get_env("PGSQL_CONNECTION")
        if not db_connection_str:
            raise ValueError("PGSQL_CONNECTION not set")
        params = parse_connection_string(db_connection_str)
        conn = psycopg2.connect(
            host=params.get("host", "localhost"),
            port=int(params.get("port", "5432")),
            user=params.get("user", ""),
            password=params.get("password", ""),
            dbname=params.get("dbname", ""),
            cursor_factory=RealDictCursor
        )
        return conn, driver

    elif driver == "mariadb":
        import pymysql
        db_connection_str = get_env("MARIADB_CONNECTION")
        if not db_connection_str:
            raise ValueError("MARIADB_CONNECTION not set")
        params = parse_connection_string(db_connection_str)
        conn = pymysql.connect(
            host=params.get("host", "localhost"),
            port=int(params.get("port", "3306")),
            user=params.get("user", ""),
            password=params.get("pass", ""),
            database=params.get("dbname", ""),
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn, driver

    raise ValueError(f"Unsupported driver: {driver}")


def parse_connection_string(conn_str: str) -> Dict[str, str]:
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
