# mcp_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime
import httpx
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP")

app = FastAPI(title="MCP Live Sports Server - Stable v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected clients
clients: list[WebSocket] = []

# --------------------- Data Fetchers ---------------------
async def fetch_cricket():
    url = "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/40381/hscard"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),  # ← .env থেকে পড়া ভালো
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            return r.json().get("results", [])[:10]
        except Exception as e:
            logger.error(f"Cricket fetch failed: {e}")
            return []

async def fetch_football():
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            return r.json().get("response", [])[:20]
        except Exception as e:
            logger.error(f"Football fetch failed: {e}")
            return []

async def fetch_headtohead():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/headtohead?h2h=33-34"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(url, headers=headers)
            return r.json().get("response", [])[:10]
        except Exception as e:
            logger.warning(f"H2H fetch failed: {e}")
            return []

# --------------------- Broadcast Loop ---------------------
async def broadcast_data():
    while True:
        try:
            cricket = await fetch_cricket()
            football = await fetch_football()
            h2h = await fetch_headtohead()

            payload = {
                "timestamp": datetime.now().isoformat(),
                "cricket": cricket,
                "football": football,
                "headtohead": h2h,
                "server": "MCP Live Server v2"
            }

            # Safely remove disconnected clients
            disconnected = []
            for ws in clients[:]:
                try:
                    await ws.send_json(payload)
                except:
                    disconnected.append(ws)

            for ws in disconnected:
                if ws in clients:
                    clients.remove(ws)
                    logger.info(f"Client disconnected. Total: {len(clients)}")

            logger.info(f"Broadcast sent to {len(clients)} clients | Cricket: {len(cricket)}, Football: {len(football)}")

        except Exception as e:
            logger.error(f"Broadcast error: {e}")

        await asyncio.sleep(30)

# --------------------- WebSocket Endpoint ---------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    logger.info(f"New client connected! Total: {len(clients)}")

    try:
        while True:
            data = await websocket.receive_text()
            # Future: handle commands here
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in clients:
            clients.remove(websocket)
        logger.info(f"Client left. Total: {len(clients)}")

# --------------------- Startup & Root ---------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_data())
    logger.info("MCP Server Started - Broadcasting every 30s")

@app.get("/")
async def root():
    return {
        "status": "MCP Server Running",
        "clients_connected": len(clients),
        "uptime": datetime.now().strftime("%H:%M:%S")
    }
