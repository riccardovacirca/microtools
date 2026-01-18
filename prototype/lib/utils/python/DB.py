from typing import Dict, List, Any
from .DBConnPool import DBConnPool

class DB:
    """Database connection and query handler with connection pool support."""

    def __init__(self):
        """Initialize DB handler."""
        self._connection = None
        self._pool = None
        self._cursor = None
        self._cursorResult = None
        self._cursorIndex = 0
        self._columns = []

    def acquire(self, pool: DBConnPool):
        """Acquire connection from pool."""
        if self._connection is not None:
            raise RuntimeError("Already connected")
        self._pool = pool
        self._connection = pool.acquire()

    def release(self):
        """Release connection back to pool."""
        if self._connection is not None:
            self.cursorClose()
            if self._pool:
                self._pool.release(self._connection)
            self._connection = None
            self._pool = None

    def hasConnection(self) -> bool:
        """Check if connected to database."""
        return self._connection is not None

    def begin(self):
        """Begin transaction."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        self._connection.execute("BEGIN")

    def commit(self):
        """Commit transaction."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        self._connection.commit()

    def rollback(self):
        """Rollback transaction."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        self._connection.rollback()

    def query(self, sql: str, params: tuple = None) -> int | None:
        """Execute INSERT, UPDATE, DELETE query and return affected rows."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        retv = None
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            self._connection.commit()
            retv = cursor.rowcount
        except Exception:
            self._connection.rollback()
        finally:
            cursor.close()
        return retv

    def select(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return list of dict."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        retv = []
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            rows = cursor.fetchall()
            if rows:
                cols = []
                for col in cursor.description:
                    cols.append(col[0])
                for row in rows:
                    record = {}
                    for i in range(len(cols)):
                        record[cols[i]] = row[i]
                    retv.append(record)
        finally:
            cursor.close()
        return retv

    def cursorOpen(self, sql: str, params: tuple = None):
        """Open cursor for iterating through results."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        self.cursorClose()
        self._cursor = self._connection.cursor()
        if params:
            self._cursor.execute(sql, params)
        else:
            self._cursor.execute(sql)
        self._cursorResult = self._cursor.fetchall()
        self._cursorIndex = 0
        self._columns = []
        if self._cursor.description:
            for col in self._cursor.description:
                self._columns.append(col[0])

    def cursorHasNext(self) -> bool:
        """Check if cursor has more rows."""
        retv = False
        if self._cursorResult is not None:
            retv = self._cursorIndex < len(self._cursorResult)
        return retv

    def cursorNext(self) -> Dict[str, Any]:
        """Get next row from cursor."""
        retv = {}
        if self.cursorHasNext():
            row = self._cursorResult[self._cursorIndex]
            self._cursorIndex += 1
            for i in range(len(self._columns)):
                retv[self._columns[i]] = row[i]
        return retv

    def cursorClose(self):
        """Close cursor and release resources."""
        if self._cursor:
            try:
                self._cursor.close()
            except Exception:
                pass
        self._cursor = None
        self._cursorResult = None
        self._cursorIndex = 0
        self._columns = []

    def columns(self) -> List[str]:
        """Return column names from last query."""
        return self._columns.copy()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
