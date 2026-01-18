import os
import redis as redisLib
from typing import Any, List

class Redis:
    """Redis client wrapper."""

    def __init__(self):
        """Initialize Redis handler."""
        self._client = None

    def connect(self):
        """Connect to Redis server."""
        if self._client is not None:
            raise RuntimeError("Already connected")
        host = os.getenv("REDIS_HOST")
        port = os.getenv("REDIS_PORT")
        if not host:
            raise RuntimeError("REDIS_HOST not set")
        if not port:
            raise RuntimeError("REDIS_PORT not set")
        self._client = redisLib.Redis(
            host=host,
            port=int(port),
            decode_responses=True
        )

    def disconnect(self):
        """Disconnect from Redis server."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def hasConnection(self) -> bool:
        """Check if connected to Redis."""
        return self._client is not None

    def get(self, key: str) -> Any:
        """Get value by key."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        return self._client.get(key)

    def set(self, key: str, value: Any):
        """Set value by key."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        self._client.set(key, value)

    def getKeys(self, pattern: str) -> List[str]:
        """Get all keys matching pattern."""
        retv = []
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        keys = self._client.keys(pattern)
        for key in keys:
            retv.append(key)
        return retv

    def delete(self, key: str):
        """Delete key."""
        if not self.hasConnection():
            raise RuntimeError("Not connected")
        self._client.delete(key)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, excType, excVal, excTb):
        """Context manager exit."""
        self.disconnect()
