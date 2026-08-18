from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import simulator
import store
from models import RiskResponse, SensorReading
from risk_classifier import classify
from wbgt import estimate_wbgt

app = FastAPI(
    title="Heat Risk Engine",
    description=(
        "Real-time Heat Risk Monitoring & Early Warning System — Risk Engine. "
        "Takes temperature/humidity sensor readings, estimates WBGT, "
        "classifies heat risk (NIOSH/ACGIH TLVs), and returns recommendations."
    ),
    version="0.1.0",
)

# Wide-open CORS for hackathon demo purposes (dashboard likely on a different
# origin/port). Tighten this before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_reading(reading: SensorReading) -> RiskResponse:
    reading = reading.with_timestamp()
    try:
        wbgt = estimate_wbgt(reading.temperature_c, reading.humidity_percent)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    assessment = classify(
        wbgt, workload=reading.workload, acclimatized=reading.acclimatized
    )

    response = RiskResponse(
        device_id=reading.device_id,
        location=reading.location,
        timestamp=reading.timestamp,
        temperature_c=reading.temperature_c,
        humidity_percent=reading.humidity_percent,
        wbgt_estimated=assessment.wbgt_estimated,
        workload=assessment.workload,
        acclimatized=assessment.acclimatized,
        risk_level=assessment.risk_level.value,
        work_rest_regimen=assessment.work_rest_regimen,
        recommendation=assessment.recommendation,
    )
    store.save(response)
    return response


@app.post("/api/v1/sensor-data", response_model=RiskResponse)
def ingest_sensor_data(reading: SensorReading):
    """Real (or simulated-manually) sensor reading comes in here.
    Returns the computed risk assessment immediately."""
    return process_reading(reading)


@app.get("/api/v1/risk/current", response_model=list[RiskResponse])
def get_current_risk_all():
    """Latest risk status for every known location — for the dashboard's
    overview screen."""
    return store.latest_all()


@app.get("/api/v1/risk/current/{location}", response_model=RiskResponse)
def get_current_risk(location: str):
    result = store.latest(location)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data yet for location '{location}'")
    return result


@app.get("/api/v1/risk/history/{location}", response_model=list[RiskResponse])
def get_history(location: str):
    """Historical readings for one location — for trend charts."""
    return store.history(location)


@app.get("/api/v1/locations")
def get_locations():
    return {"locations": store.known_locations()}


@app.post("/api/v1/simulate/start")
async def start_simulator():
    # Must be async: asyncio.create_task() needs to run on the event-loop
    # thread, not FastAPI's sync-endpoint worker thread.
    started = simulator.start(process_fn=process_reading)
    if not started:
        return {"status": "already_running"}
    return {"status": "started"}


@app.post("/api/v1/simulate/stop")
async def stop_simulator():
    stopped = simulator.stop()
    if not stopped:
        return {"status": "not_running"}
    return {"status": "stopped"}


@app.get("/api/v1/simulate/status")
def simulator_status():
    return {"running": simulator.is_running()}


@app.get("/health")
def health():
    return {"status": "ok"}
