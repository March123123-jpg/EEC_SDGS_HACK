"""
Heat-risk classification from estimated WBGT.

Thresholds are the standard NIOSH / ACGIH WBGT Threshold Limit Values (TLVs),
published in NIOSH (2016) "Criteria for a Recommended Standard: Occupational
Exposure to Heat and Hot Environments" -- also cited in the project proposal's
bibliography. TLVs are given as the max WBGT (°C) for a given work/rest
regimen and workload category, split by whether workers are heat-acclimatized.

We use them the other way around: given the *measured* WBGT and a workload
category, find the least-restrictive work/rest regimen that is still safe,
and report that as the recommendation.
"""

from dataclasses import dataclass
from enum import Enum


class Workload(str, Enum):
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"


class RiskLevel(str, Enum):
    SAFE = "Safe"
    CAUTION = "Caution"
    WARNING = "Warning"
    DANGER = "Danger"


# WBGT (°C) upper limit for each work/rest regimen, by workload.
# Regimens ordered from least restrictive (100% work) to most (25% work / 75% rest).
# `None` means that regimen is not considered safe at any WBGT for that workload
# (matches the published ACGIH/NIOSH table, which leaves heavy/100% blank).
TLV_ACCLIMATIZED = {
    Workload.LIGHT:    {"100-0": 31.0, "75-25": 31.0, "50-50": 32.0, "25-75": 32.5},
    Workload.MODERATE: {"100-0": 28.0, "75-25": 29.0, "50-50": 30.0, "25-75": 31.5},
    Workload.HEAVY:    {"100-0": None, "75-25": 27.5, "50-50": 29.0, "25-75": 30.5},
}

TLV_UNACCLIMATIZED = {
    Workload.LIGHT:    {"100-0": 28.0, "75-25": 28.5, "50-50": 29.5, "25-75": 30.0},
    Workload.MODERATE: {"100-0": 25.0, "75-25": 26.0, "50-50": 27.0, "25-75": 29.0},
    Workload.HEAVY:    {"100-0": None, "75-25": 24.0, "50-50": 25.5, "25-75": 27.5},
}

REGIMEN_ORDER = ["100-0", "75-25", "50-50", "25-75"]

RECOMMENDATIONS = {
    RiskLevel.SAFE: "ทำงานต่อเนื่องได้ตามปกติ ควรดื่มน้ำสม่ำเสมอ",
    RiskLevel.CAUTION: "เพิ่มความถี่ในการพักและดื่มน้ำ เฝ้าระวังอาการเบื้องต้นของ heat stress",
    RiskLevel.WARNING: "ปรับตารางทำงาน-พักตามรอบที่แนะนำ ลดระยะเวลาทำงานต่อเนื่อง แจ้งหัวหน้างาน/จป.",
    RiskLevel.DANGER: "หยุดหรือปรับเปลี่ยนการปฏิบัติงานทันที ย้ายไปพื้นที่ร่มเย็น แจ้ง จป. และเฝ้าระวังอาการฮีทสโตรก",
}


@dataclass
class RiskAssessment:
    wbgt_estimated: float
    workload: Workload
    acclimatized: bool
    risk_level: RiskLevel
    work_rest_regimen: str  # e.g. "50-50" meaning 50% work / 50% rest per hour
    recommendation: str


def classify(
    wbgt: float,
    workload: Workload = Workload.MODERATE,
    acclimatized: bool = True,
) -> RiskAssessment:
    table = TLV_ACCLIMATIZED if acclimatized else TLV_UNACCLIMATIZED
    limits = table[workload]

    # Find the least-restrictive regimen whose TLV is >= measured WBGT.
    safe_regimen = None
    for regimen in REGIMEN_ORDER:
        limit = limits[regimen]
        if limit is not None and wbgt <= limit:
            safe_regimen = regimen
            break

    if safe_regimen == "100-0":
        level = RiskLevel.SAFE
    elif safe_regimen == "75-25":
        level = RiskLevel.CAUTION
    elif safe_regimen == "50-50":
        level = RiskLevel.WARNING
    elif safe_regimen == "25-75":
        level = RiskLevel.DANGER
    else:
        # Exceeds even the most restrictive regimen -> stop work.
        safe_regimen = "0-100"
        level = RiskLevel.DANGER

    return RiskAssessment(
        wbgt_estimated=wbgt,
        workload=workload,
        acclimatized=acclimatized,
        risk_level=level,
        work_rest_regimen=safe_regimen,
        recommendation=RECOMMENDATIONS[level],
    )
