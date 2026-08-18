from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

readings = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


class SensorData(BaseModel):
    device_code: str
    temperature_c: float
    humidity_pct: float


# risk calculation ชั่วคราว
# รอ Integration มาต่อกับ Risk Engine ตัวจริงของเพื่อนทีหลัง
def calculate_risk(temp: float, hum: float) -> str:
    if temp > 40 or hum > 80:
        return "High"
    elif temp > 35 or hum > 70:
        return "Medium"
    else:
        return "Low"


@app.get("/")
def home():
    return {"message": "Backend is running!"}


@app.post("/api/readings")
async def receive_reading(data: SensorData):
    risk_level = calculate_risk(data.temperature_c, data.humidity_pct)
    record = data.dict()
    record["risk"] = risk_level
    readings.append(record)
<<<<<<< HEAD
    
=======
>>>>>>> cf5175f0a8f6725b1ce87ec35b9a632e0b9b9cb1
    await manager.broadcast(record)
    return {"status": "received", "data": record}


@app.get("/api/risk")
def get_risk():
    if not readings:
        return {"risk": "UNKNOWN", "message": "No data available in system"}

    latest = readings[-1]
    risk_value = latest.get("risk") or calculate_risk(
        latest.get("temperature_c", 0),
        latest.get("humidity_pct", 0),
    )
    return {
        "device_code": latest.get("device_code", "UNKNOWN"),
        "risk": risk_value,
        "temperature_c": latest.get("temperature_c", 0),
        "humidity_pct": latest.get("humidity_pct", 0),
    }


@app.get("/api/history")
def get_history(limit: int = 20):
    return {
        "total": len(readings),
        "data": readings[-limit:],
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
