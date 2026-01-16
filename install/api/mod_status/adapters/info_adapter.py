import os
import asyncio
import httpx
import websockets
import json
from typing import Dict, Any

# Config microservizio C++
MOD_STATUS_HOST = os.getenv("MICROSERVICE_MOD_STATUS_HOST", "127.0.0.1")
MOD_STATUS_PORT = os.getenv("MICROSERVICE_MOD_STATUS_PORT", "9001")
MOD_STATUS_HTTP_URL = f"http://{MOD_STATUS_HOST}:{MOD_STATUS_PORT}"
MOD_STATUS_WS_URL = f"ws://{MOD_STATUS_HOST}:{MOD_STATUS_PORT}/ws"
JOB_TIMEOUT = 30


async def get() -> Dict[str, Any]:
    """Recupera info status da microservizio C++ via WebSocket."""
    async with websockets.connect(MOD_STATUS_WS_URL) as ws:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{MOD_STATUS_HTTP_URL}/api/status/info")
            resp.raise_for_status()
            data = resp.json()
            job_id = data.get("job_id")
            if not job_id:
                raise RuntimeError("Nessun job_id restituito dal microservizio")
        await ws.send(job_id)
        result_json = await asyncio.wait_for(ws.recv(), timeout=JOB_TIMEOUT)
        result = json.loads(result_json)
        return result
