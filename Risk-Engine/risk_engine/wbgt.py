"""
WBGT (Wet Bulb Globe Temperature) estimation.

Our sensors (DHT22 / SHT31 on ESP32) measure only dry-bulb temperature and
relative humidity -- there is no black-globe thermometer in the prototype's
hardware list, so true outdoor WBGT (which needs globe temperature and wind
speed) cannot be measured directly.

Instead we use the widely-used WBGT *approximation* formula (Australian
Bureau of Meteorology simplified indoor formula, also commonly used as a
practical estimate when only T and RH are available):

    WBGT ≈ 0.567 * T + 0.393 * e + 3.94
Deter relatingaCSV banalis for the
where:
    T = dry-bulb air temperature (°C)
    e = water vapour pressure (hPa), derived from T and RH

This is a reasonable, well-documented estimate for a hackathon prototype.
It systematically *under-estimates* WBGT in direct sun (no solar/globe term),
so it should be treated as a conservative baseline -- documented as a known
limitation (see proposal section 6.1.1 / 6.2.1: more sensor types, e.g. a
globe thermometer, are a natural next step).
"""

import math


def vapor_pressure_hpa(temperature_c: float, humidity_percent: float) -> float:
    """Water vapour pressure (hPa) from temperature and relative humidity,
    using the Magnus-Tetens approximation for saturation vapour pressure."""
    saturation_vp = 6.105 * math.exp((17.27 * temperature_c) / (237.7 + temperature_c))
    return (humidity_percent / 100.0) * saturation_vp


def estimate_wbgt(temperature_c: float, humidity_percent: float) -> float:
    """Estimate WBGT (°C) from temperature and relative humidity.

    Raises ValueError on physically implausible sensor readings so bad
    hardware data doesn't silently produce a nonsense risk level.
    """
    if not (-20 <= temperature_c <= 70):
        raise ValueError(f"temperature_c out of plausible range: {temperature_c}")
    if not (0 <= humidity_percent <= 100):
        raise ValueError(f"humidity_percent out of plausible range: {humidity_percent}")

    e = vapor_pressure_hpa(temperature_c, humidity_percent)
    wbgt = 0.567 * temperature_c + 0.393 * e + 3.94
    return round(wbgt, 2)
