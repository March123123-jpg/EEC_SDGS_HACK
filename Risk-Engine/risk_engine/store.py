"""
Simple in-memory store, keyed by location.

Good enough for a hackathon prototype / demo. Swapping this for PostgreSQL
later (per the proposal's tech stack) means only this file changes -- callers
in main.py just use latest()/history()/save().
"""

from collections import defaultdict, deque
from typing import Deque, Dict, List

from models import RiskResponse

MAX_HISTORY_PER_LOCATION = 500

_latest: Dict[str, RiskResponse] = {}
_history: Dict[str, Deque[RiskResponse]] = defaultdict(
    lambda: deque(maxlen=MAX_HISTORY_PER_LOCATION)
)


def save(reading: RiskResponse) -> None:
    _latest[reading.location] = reading
    _history[reading.location].append(reading)


def latest(location: str) -> RiskResponse | None:
    return _latest.get(location)


def latest_all() -> List[RiskResponse]:
    return list(_latest.values())


def history(location: str) -> List[RiskResponse]:
    return list(_history.get(location, []))


def known_locations() -> List[str]:
    return list(_latest.keys())
