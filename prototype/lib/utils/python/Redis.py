import os
import redis as redis_lib
from typing import Any, List

class Redis:

    def __init__(self):
        self.client = None

    def connect(self):
        if self.client is not None:
            raise RuntimeError("Already connected")
        host = os.getenv("REDIS_HOST")
        port = os.getenv("REDIS_PORT")
        if not host:
            raise RuntimeError("REDIS_HOST not set")
        if not port:
            raise RuntimeError("REDIS_PORT not set")
        self.client = redis_lib.Redis(
            host=host,
            port=int(port),
            decode_responses=True
        )

    def disconnect(self):
        if self.client is None:
            return
        self.client.close()
        self.client = None

    def is_connected(self) -> bool:
        return self.client is not None

    def get(self, key: str) -> Any:
        if not self.is_connected():
            raise RuntimeError("Not connected to Redis")
        return self.client.get(key)

    def set(self, key: str, value: Any):
        if not self.is_connected():
            raise RuntimeError("Not connected to Redis")
        self.client.set(key, value)

    def list(self) -> List[str]:
        if not self.is_connected():
            raise RuntimeError("Not connected to Redis")
        return self.client.keys("*")

    def delete(self, key: str):
        if not self.is_connected():
            raise RuntimeError("Not connected to Redis")
        self.client.delete(key)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
