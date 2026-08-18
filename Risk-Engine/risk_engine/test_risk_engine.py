"""
Run with: pytest test_risk_engine.py -v
"""

import pytest

from risk_classifier import Workload, RiskLevel, classify
from wbgt import estimate_wbgt


def test_wbgt_increases_with_temperature():
    assert estimate_wbgt(35, 60) > estimate_wbgt(25, 60)


def test_wbgt_increases_with_humidity():
    assert estimate_wbgt(30, 80) > estimate_wbgt(30, 40)


def test_wbgt_rejects_implausible_temperature():
    with pytest.raises(ValueError):
        estimate_wbgt(999, 50)


def test_wbgt_rejects_implausible_humidity():
    with pytest.raises(ValueError):
        estimate_wbgt(30, 150)


def test_classify_safe_at_low_wbgt():
    result = classify(20, workload=Workload.LIGHT)
    assert result.risk_level == RiskLevel.SAFE
    assert result.work_rest_regimen == "100-0"


def test_classify_danger_at_high_wbgt():
    result = classify(35, workload=Workload.HEAVY)
    assert result.risk_level == RiskLevel.DANGER
    assert result.work_rest_regimen == "0-100"


def test_classify_risk_increases_monotonically_with_wbgt():
    levels_order = [RiskLevel.SAFE, RiskLevel.CAUTION, RiskLevel.WARNING, RiskLevel.DANGER]
    prev_index = -1
    for wbgt in range(15, 40):
        result = classify(float(wbgt), workload=Workload.MODERATE)
        idx = levels_order.index(result.risk_level)
        assert idx >= prev_index, f"Risk level decreased at WBGT={wbgt}"
        prev_index = idx


def test_unacclimatized_workers_have_lower_thresholds():
    wbgt = 27.0
    acclimatized = classify(wbgt, workload=Workload.MODERATE, acclimatized=True)
    unacclimatized = classify(wbgt, workload=Workload.MODERATE, acclimatized=False)
    levels_order = [RiskLevel.SAFE, RiskLevel.CAUTION, RiskLevel.WARNING, RiskLevel.DANGER]
    assert levels_order.index(unacclimatized.risk_level) >= levels_order.index(
        acclimatized.risk_level
    )


def test_heavy_workload_never_safe_for_continuous_work():
    # ACGIH/NIOSH table has no 100% work limit for heavy workload -- any
    # measurable WBGT should require at least some rest.
    result = classify(15, workload=Workload.HEAVY)
    assert result.work_rest_regimen != "100-0"
