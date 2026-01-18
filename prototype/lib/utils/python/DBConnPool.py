from typing import Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool

class DBConnPool:
    """SQLAlchemy connection pool manager."""

    def __init__(self, driver: str, env: Any, **config):
        """Initialize connection pool."""
        self._env = env
        self._driver = self._detectDriver(driver)
        self._config = self._buildConfig(config)
        self._engine = self._createEngine()
        self._activeConnections = {}

    def _detectDriver(self, driver: str) -> str:
        """Auto-detect driver from environment if not specified."""
        retv = driver
        if not retv:
            if self._env.get("SQLITE3_ENABLED", "n") == "y":
                retv = "sqlite3"
            elif self._env.get("MARIADB_ENABLED", "n") == "y":
                retv = "mariadb"
            elif self._env.get("PGSQL_ENABLED", "n") == "y":
                retv = "pgsql"
            else:
                raise ValueError("No database enabled")
        return retv

    def _buildConfig(self, config: Dict) -> Dict:
        """Build configuration from environment and defaults."""
        retv = {}
        retv["pool_size"] = int(self._env.get("DB_POOL_SIZE", str(config.get("pool_size", 5))))
        retv["max_overflow"] = int(self._env.get("DB_POOL_MAX_OVERFLOW", str(config.get("max_overflow", 10))))
        retv["pool_timeout"] = int(self._env.get("DB_POOL_TIMEOUT", str(config.get("pool_timeout", 30))))
        retv["pool_recycle"] = int(self._env.get("DB_POOL_RECYCLE", str(config.get("pool_recycle", 3600))))
        prePing = self._env.get("DB_POOL_PRE_PING", str(config.get("pool_pre_ping", True)))
        retv["pool_pre_ping"] = prePing.lower() == "true"
        echoPool = self._env.get("DB_POOL_ECHO", str(config.get("echo_pool", False)))
        retv["echo_pool"] = echoPool.lower() == "true"
        return retv

    def _createEngine(self) -> Engine:
        """Create SQLAlchemy engine with connection pooling."""
        retv = None
        if self._driver == "sqlite3":
            retv = self._createSqliteEngine()
        elif self._driver == "pgsql":
            retv = self._createPgsqlEngine()
        elif self._driver == "mariadb":
            retv = self._createMariadbEngine()
        else:
            raise ValueError("Unsupported driver: " + self._driver)
        return retv

    def _createSqliteEngine(self) -> Engine:
        """Create SQLite engine."""
        dbPath = self._env.get("SQLITE3_CONNECTION", "")
        dbPath = dbPath.replace("file:", "")
        if not dbPath:
            raise ValueError("SQLITE3_CONNECTION not set")
        engine = create_engine(
            "sqlite:///" + dbPath,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo_pool=self._config["echo_pool"]
        )
        @event.listens_for(engine, "connect")
        def setSqlitePragma(dbapiConn, connectionRecord):
            cursor = dbapiConn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        return engine

    def _createPgsqlEngine(self) -> Engine:
        """Create PostgreSQL engine."""
        connStr = self._env.get("PGSQL_CONNECTION", "")
        if not connStr:
            raise ValueError("PGSQL_CONNECTION not set")
        params = self._parseConnectionString(connStr)
        url = "postgresql+psycopg2://"
        url = url + params.get("user", "") + ":" + params.get("password", "")
        url = url + "@" + params.get("host", "localhost") + ":" + params.get("port", "5432")
        url = url + "/" + params.get("dbname", "")
        retv = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=self._config["pool_size"],
            max_overflow=self._config["max_overflow"],
            pool_timeout=self._config["pool_timeout"],
            pool_recycle=self._config["pool_recycle"],
            pool_pre_ping=self._config["pool_pre_ping"],
            echo_pool=self._config["echo_pool"]
        )
        return retv

    def _createMariadbEngine(self) -> Engine:
        """Create MariaDB engine."""
        connStr = self._env.get("MARIADB_CONNECTION", "")
        if not connStr:
            raise ValueError("MARIADB_CONNECTION not set")
        params = self._parseConnectionString(connStr)
        url = "mysql+pymysql://"
        url = url + params.get("user", "") + ":" + params.get("pass", "")
        url = url + "@" + params.get("host", "localhost") + ":" + params.get("port", "3306")
        url = url + "/" + params.get("dbname", "")
        retv = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=self._config["pool_size"],
            max_overflow=self._config["max_overflow"],
            pool_timeout=self._config["pool_timeout"],
            pool_recycle=self._config["pool_recycle"],
            pool_pre_ping=self._config["pool_pre_ping"],
            echo_pool=self._config["echo_pool"]
        )
        return retv

    def _parseConnectionString(self, connStr: str) -> Dict[str, str]:
        """Parse database connection string."""
        retv = {}
        parts = []
        if "," in connStr:
            parts = connStr.split(",")
        else:
            parts = connStr.split()
        for part in parts:
            if "=" in part:
                idx = part.index("=")
                key = part[:idx].strip()
                value = part[idx + 1:].strip()
                retv[key] = value
        return retv

    def acquire(self):
        """Acquire a connection from the pool."""
        conn = self._engine.raw_connection()
        connId = id(conn)
        self._activeConnections[connId] = conn
        return conn

    def release(self, conn):
        """Release connection back to the pool."""
        connId = id(conn)
        if connId in self._activeConnections:
            del self._activeConnections[connId]
        conn.close()

    def terminate(self):
        """Terminate all connections and dispose pool."""
        for conn in self._activeConnections.values():
            try:
                conn.close()
            except Exception:
                pass
        self._activeConnections.clear()
        self._engine.dispose()

    @contextmanager
    def connection(self):
        """Context manager for connection."""
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)

    def getPoolStatus(self) -> Dict[str, Any]:
        """Get connection pool status."""
        retv = {}
        try:
            pool = self._engine.pool
            checkedOut = pool.checkedout()
            poolSize = pool.size()
            overflow = 0
            if hasattr(pool, "overflow"):
                overflow = pool.overflow()
            retv["pool_size"] = poolSize
            retv["checked_out"] = checkedOut
            retv["checked_in"] = poolSize - checkedOut
            retv["overflow"] = overflow
            retv["total"] = poolSize + overflow
            retv["active_connections"] = len(self._activeConnections)
        except Exception as e:
            retv["error"] = str(e)
        return retv
