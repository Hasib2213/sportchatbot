# realtime_mcp_client.py
import asyncio
import websockets
import json
from typing import List, Dict

class RealTimeMCPClient:
    def __init__(self, url="ws://localhost:8000/ws"):
        self.url = url
        self.websocket = None
        self.latest_data = {
            'cricket': [],
            'football': [],
            'last_updated': None
        }
        self.data_ready = asyncio.Event()

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.url)
            print("Connected to MCP Server (Real-time Push)")
            asyncio.create_task(self._listener())
            return True
        except Exception as e:
            print(f"WebSocket failed: {e}. Falling back to polling...")
            return True  # Still allow polling fallback

    async def _listener(self):
        async for message in self.websocket:
            data = json.loads(message)
            self.latest_data.update({
                'cricket': data.get('cricket', []),
                'football': data.get('football', []),
                'last_updated': data['timestamp']
            })
            self.data_ready.set()

    async def fetch_cricket_current_matches(self) -> List[Dict]:
        self.data_ready.clear()
        await self.data_ready.wait()
        return self.latest_data['cricket']

    async def fetch_football_today_matches(self) -> List[Dict]:
        self.data_ready.clear()
        await self.data_ready.wait()
        return self.latest_data['football']

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()