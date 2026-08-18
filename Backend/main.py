import os
import sys


from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import psycopg2
from psycopg2.extras import RealDictCursor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RISK_ENGINE_PATH = os.path.join(
    BASE_DIR,
    "Risk-Engine",
    "risk_engine"
)

sys.path.insert(0, RISK_ENGINE_PATH)

from risk_engine.wbgt import estimate_wbgt
from risk_engine.risk_classifier import (
    classify,
    Workload,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/eec_heat_risk"
)


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

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

def calculate_heat_risk(
        temperature_c: float,
        humidity_pct: float
):

    wbgt = estimate_wbgt(
        temperature_c,
        humidity_pct
    )

    assessment = classify(
        wbgt = wbgt,
        Workload = Workload.MODERATE,
        acclimatized = True
    )

    return {
        "wbgt" : assessment.wbgt_estimated,

        "risk_level" : assessment.risk_level.value,

        "work_rest_regimen" : (
            assessment.work_rest_regimen
        ),

        "recommendation" : (
            assessment.recommendation
        )
    }

# # risk calculation ชั่วคราว
# # รอ Integration มาต่อกับ Risk Engine ตัวจริงของเพื่อนทีหลัง
# def calculate_risk(temp: float, hum: float) -> str:
#     if temp > 40 or hum > 80:
#         return "High"
#     elif temp > 35 or hum > 70:
#         return "Medium"
#     else:
#         return "Low"


@app.get("/")
def home():
    return {"message": "Backend is running!"}


@app.post("/api/readings")
async def receive_reading(data: SensorData):
 # --------------------------------------------------------
    # 1. Calculate Heat Risk
    # --------------------------------------------------------

    risk = calculate_heat_risk(
        data.temperature_c,
        data.humidity_pct
    )


    # --------------------------------------------------------
    # 2. Build complete record
    # --------------------------------------------------------

    record = {

        "device_code": data.device_code,

        "temperature_c": data.temperature_c,

        "humidity_pct": data.humidity_pct,

        "wbgt": risk["wbgt"],

        "risk_level": risk["risk_level"],

        "work_rest_regimen": (
            risk["work_rest_regimen"]
        ),

        "recommendation": (
            risk["recommendation"]
        )
    }


    # --------------------------------------------------------
    # 3. Save to PostgreSQL
    # --------------------------------------------------------

    conn = get_db_connection()

    try:

        with conn.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            # Make sure zone exists
            cursor.execute(
                """
                INSERT INTO zones (device_code, name)
                VALUES (%s, %s)
                ON CONFLICT (device_code)
                DO NOTHING
                """,
                (
                    data.device_code,
                    data.device_code
                )
            )


            # Get zone
            cursor.execute(
                """
                SELECT id
                FROM zones
                WHERE device_code = %s
                """,
                (data.device_code,)
            )

            zone = cursor.fetchone()

            zone_id = zone["id"]


            # Save sensor reading
            cursor.execute(
                """
                INSERT INTO sensor_readings
                (
                    zone_id,
                    temperature_c,
                    humidity_pct
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    zone_id,
                    data.temperature_c,
                    data.humidity_pct
                )
            )

            reading = cursor.fetchone()

            reading_id = reading["id"]


            # Save risk result
            cursor.execute(
                """
                INSERT INTO risk_records
                (
                    reading_id,
                    wbgt,
                    risk_level,
                    work_rest_regimen,
                    recommendation
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    reading_id,
                    risk["wbgt"],
                    risk["risk_level"],
                    risk["work_rest_regimen"],
                    risk["recommendation"]
                )
            )


            # ------------------------------------------------
            # ⭐ NEW: Alert for Warning / Danger
            # ------------------------------------------------

            if risk["risk_level"] in [
                "Warning",
                "Danger"
            ]:

                cursor.execute(
                    """
                    INSERT INTO alerts
                    (
                        zone_id,
                        risk_level,
                        message
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        zone_id,
                        risk["risk_level"],
                        risk["recommendation"]
                    )
                )


        conn.commit()

    finally:

        conn.close()

    await manager.broadcast(record)

    return {
        "status" : "received",
        "data" : record
    }

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
    conn = get_db_connection()

    try:

        with conn.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    z.device_code,
                    sr.temperature_c,
                    sr.humidity_pct,
                    rr.wbgt,
                    rr.risk_level,
                    rr.work_rest_regimen,
                    rr.recommendation,
                    sr.created_at
                FROM sensor_readings sr

                JOIN zones z
                    ON z.id = sr.zone_id

                JOIN risk_records rr
                    ON rr.reading_id = sr.id

                ORDER BY sr.created_at DESC

                LIMIT %s
                """,
                (limit,)
            )

            return {
                "data": [
                    dict(row)
                    for row in cursor.fetchall()
                ]
            }

    finally:

        conn.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# Add CORS Middleware if not already present
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive data or keep the connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        print("Client disconnected")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Send initial dummy/sensor data right away on connection
    initial_data = {
        "device_code": "ZONE-01",
        "temperature": 34.5,
        "humidity": 65,
        "heat_index": 38.2,
        "status": "Warning"
    }
    await websocket.send_json(initial_data)
    
    try:
        while True:
            # Keep connection active
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("Client disconnected")