from typing import Dict, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool
from .Env import Env

class DBConnPool:
  """SQLAlchemy connection pool manager."""
  
  def __init__(self, driver: str = None, env=None, **config):
    """
    Initialize connection pool.
    
    Args:
      driver: Database driver (sqlite3|mariadb|pgsql, auto-detect if None)
      env: Env instance for configuration
      **config: Pool configuration parameters
    """
    self.env = env or Env()
    self.driver = self._detect_driver(driver)
    self.config = {
      "pool_size": int(self.env.get("DB_POOL_SIZE", config.get("pool_size", 5))),
      "max_overflow": int(self.env.get("DB_POOL_MAX_OVERFLOW", config.get("max_overflow", 10))),
      "pool_timeout": int(self.env.get("DB_POOL_TIMEOUT", config.get("pool_timeout", 30))),
      "pool_recycle": int(self.env.get("DB_POOL_RECYCLE", config.get("pool_recycle", 3600))),
      "pool_pre_ping": self.env.get("DB_POOL_PRE_PING", str(config.get("pool_pre_ping", True))).lower() == "true",
      "echo_pool": self.env.get("DB_POOL_ECHO", str(config.get("echo_pool", False))).lower() == "true"
    }
    self._engine = self._create_engine()
    self._active_connections = {}
  
  def _detect_driver(self, driver: Optional[str]) -> str:
    """Auto-detect driver from environment if not specified."""
    if driver:
      return driver
    
    if self.env.get("SQLITE3_ENABLED") == "y":
      return "sqlite3"
    elif self.env.get("MARIADB_ENABLED") == "y":
      return "mariadb"
    elif self.env.get("PGSQL_ENABLED") == "y":
      return "pgsql"
    else:
      raise ValueError("No database enabled. Set SQLITE3_ENABLED, MARIADB_ENABLED, or PGSQL_ENABLED to 'y'")
  
  def _create_engine(self) -> Engine:
    """Create SQLAlchemy engine with connection pooling."""
    if self.driver == "sqlite3":
      db_path = self.env.get("SQLITE3_CONNECTION", "").replace("file:", "")
      if not db_path:
        raise ValueError("SQLITE3_CONNECTION not set")
      
      engine = create_engine(
        f"sqlite:///{db_path}",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo_pool=self.config["echo_pool"]
      )
      
      @event.listens_for(engine, "connect")
      def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
      
      return engine
      
    elif self.driver == "pgsql":
      conn_str = self.env.get("PGSQL_CONNECTION")
      if not conn_str:
        raise ValueError("PGSQL_CONNECTION not set")
      
      params = self._parse_connection_string(conn_str)
      url = (
        f"postgresql+psycopg2://{params.get('user', '')}:{params.get('password', '')}"
        f"@{params.get('host', 'localhost')}:{params.get('port', '5432')}"
        f"/{params.get('dbname', '')}"
      )
      
      return create_engine(
        url,
        poolclass=QueuePool,
        pool_size=self.config["pool_size"],
        max_overflow=self.config["max_overflow"],
        pool_timeout=self.config["pool_timeout"],
        pool_recycle=self.config["pool_recycle"],
        pool_pre_ping=self.config["pool_pre_ping"],
        echo_pool=self.config["echo_pool"]
      )
      
    elif self.driver == "mariadb":
      conn_str = self.env.get("MARIADB_CONNECTION")
      if not conn_str:
        raise ValueError("MARIADB_CONNECTION not set")
      
      params = self._parse_connection_string(conn_str)
      url = (
        f"mysql+pymysql://{params.get('user', '')}:{params.get('pass', '')}"
        f"@{params.get('host', 'localhost')}:{params.get('port', '3306')}"
        f"/{params.get('dbname', '')}"
      )
      
      return create_engine(
        url,
        poolclass=QueuePool,
        **self.config
      )
      
    raise ValueError(f"Unsupported driver: {self.driver}")
  
  def _parse_connection_string(self, conn_str: str) -> Dict[str, str]:
    """Parse database connection string."""
    params = {}
    parts = conn_str.split(",") if "," in conn_str else conn_str.split()
    for part in parts:
      if "=" in part:
        key, value = part.split("=", 1)
        params[key.strip()] = value.strip()
    return params
  
  def acquire(self):
    """Acquire a connection from the pool."""
    conn = self._engine.raw_connection()
    conn_id = id(conn)
    self._active_connections[conn_id] = conn
    return conn
  
  def release(self, conn):
    """Release connection back to the pool."""
    conn_id = id(conn)
    if conn_id in self._active_connections:
      del self._active_connections[conn_id]
    conn.close()
  
  def terminate(self):
    """Terminate all connections and dispose pool."""
    for conn in self._active_connections.values():
      try:
        conn.close()
      except:
        pass
    self._active_connections.clear()
    self._engine.dispose()
  
  @contextmanager
  def connection(self):
    """Context manager for connection."""
    conn = self.acquire()
    try:
      yield conn
    finally:
      self.release(conn)
  
  def get_pool_status(self) -> Dict:
    """Get connection pool status."""
    try:
      pool = self._engine.pool
      checked_out = pool.checkedout()
      pool_size = pool.size()
      overflow = pool.overflow() if hasattr(pool, 'overflow') else 0
      
      return {
        "pool_size": pool_size,
        "checked_out": checked_out,
        "checked_in": pool_size - checked_out,
        "overflow": overflow,
        "total": pool_size + overflow,
        "active_connections": len(self._active_connections)
      }
    except Exception as e:
      return {"error": str(e)}