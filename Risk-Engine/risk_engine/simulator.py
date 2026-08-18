"""
Background simulator that generates plausible sensor readings and feeds them
through the same pipeline as real ESP32 data -- so the dashboard team can
demo the whole system before hardware is on-site.

Temperature follows a rough daily curve (cooler at night, peaks early
afternoon) plus small random noise, loosely modeled on the ~30.3°C WBGT
figure the proposal cites for a steel plant.
"""

import asyncio
import math
import random
from datetime import datetime, timezone

from models import SensorReading
from risk_classifier import Workload

DEFAULT_LOCATIONS = [
    {"device_id": "sim-esp32-01", "location": "steel-plant-zone-a", "workload": Workload.HEAVY},
    {"device_id": "sim-esp32-02", "location": "construction-site-b", "workload": Workload.MODERATE},
    {"device_id": "sim-esp32-03", "location": "logistics-warehouse-c", "workload": Workload.LIGHT},
]

_task: asyncio.Task | None = None


def _simulated_reading(zone: dict) -> SensorReading:
    now = datetime.now(timezone.utc)
    hour = now.hour + now.minute / 60
    # Daily curve peaking ~13:00, base temp higher for heavy-industry zones.
    base = 27 if zone["workload"] == Workload.HEAVY else 25
    daily_swing = 8 * math.sin(math.pi * (hour - 6) / 12) if 6 <= hour <= 18 else -2
    temperature = base + daily_swing + random.uniform(-1, 1)
    humidity = 60 + random.uniform(-10, 15)
    humidity = max(20, min(95, humidity))

    return SensorReading(
        device_id=zone["device_id"],
        location=zone["location"],
        temperature_c=round(temperature, 1),
        humidity_percent=round(humidity, 1),
        workload=zone["workload"],
        acclimatized=True,
    )


async def _run(process_fn, interval_seconds: float):
    while True:
        for zone in DEFAULT_LOCATIONS:
            reading = _simulated_reading(zone)
            process_fn(reading)
        await asyncio.sleep(interval_seconds)


def start(process_fn, interval_seconds: float = 5.0) -> bool:
    """Start the simulator loop. Returns False if already running."""
    global _task
    if _task is not None and not _task.done():
        return False
    _task = asyncio.create_task(_run(process_fn, interval_seconds))
    return True


def stop() -> bool:
    """Stop the simulator loop. Returns False if it wasn't running."""
    global _task
    if _task is None or _task.done():
        return False
    _task.cancel()
    _task = None
    return True


def is_running() -> bool:
    return _task is not None and not _task.done()
