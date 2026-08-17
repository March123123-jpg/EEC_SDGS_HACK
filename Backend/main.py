from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

readings = []

class SensorData(BaseModel):
    device_code: str
    temperature_c: float
    humidity_pct: float

@app.get("/")
def home():
    return {"message": "Backend is running!"}

@app.post("/api/readings")
def receive_reading(data: SensorData):
    readings.append(data.dict())
    return {"status": "received", "data": data}