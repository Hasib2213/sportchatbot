# realtime_mcp_client.py
import asyncio
import websockets
import json
from typing import List, Dict, Optional

class RealTimeMCPClient:
    def __init__(self, url: str = "ws://localhost:8000/ws"):
        self.url = url
        self.latest_data = {
            'cricket': [],
            'football': [],
            'last_updated': None
        }
        self.data_ready = asyncio.Event()
        self._task = None

    async def connect(self):
        try:
            self.ws = await websockets.connect(self.url, ping_interval=20)
            print("✅ WebSocket Connected!")
            self._task = asyncio.create_task(self._listener())
            return True
        except Exception as e:
            print(f"❌ WebSocket failed: {e}")
            return False

    async def _listener(self):
        async for message in self.ws:
            try:
                data = json.loads(message)
                self.latest_data.update({
                    'cricket': data.get('cricket', []),
                    'football': data.get('football', []),
                    'last_updated': data.get('timestamp', self.latest_data['last_updated'])
                })
                self.data_ready.set()
            except Exception as e:
                print("JSON parse error:", e)

    async def get_data(self, key: Optional[str] = None):
        if not self.data_ready.is_set():
            try:
                await asyncio.wait_for(self.data_ready.wait(), timeout=15.0)
            except asyncio.TimeoutError:
                pass  # return cache
        self.data_ready.clear()
        return self.latest_data if key is None else self.latest_data.get(key, [])

    async def disconnect(self):
        if hasattr(self, '_task') and self._task:
            self._task.cancel()
        if hasattr(self, 'ws'):
            await self.ws.close()