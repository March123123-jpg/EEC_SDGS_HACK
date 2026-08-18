from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from risk_classifier import Workload


class SensorReading(BaseModel):
    device_id: str = Field(..., description="ESP32 device identifier")
    location: str = Field(..., description="e.g. 'steel-plant-zone-a'")
    temperature_c: float = Field(..., description="Dry-bulb temperature, °C")
    humidity_percent: float = Field(..., description="Relative humidity, %")
    workload: Workload = Field(
        default=Workload.MODERATE,
        description="Typical physical workload for workers in this zone",
    )
    acclimatized: bool = Field(
        default=True, description="Whether workers are heat-acclimatized"
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="Defaults to server receive time if omitted"
    )

    def with_timestamp(self) -> "SensorReading":
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        return self


class RiskResponse(BaseModel):
    device_id: str
    location: str
    timestamp: datetime
    temperature_c: float
    humidity_percent: float
    wbgt_estimated: float
    workload: Workload
    acclimatized: bool
    risk_level: str
    work_rest_regimen: str
    recommendation: str
