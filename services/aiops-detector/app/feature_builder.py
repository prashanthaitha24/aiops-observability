from __future__ import annotations

from typing import Iterable


FEATURE_ORDER = [
    "frontend_rps",
    "ads_rps",
    "cart_add_latency_ms",
    "cart_get_latency_ms",
    "cart_add_p95_latency_ms",
    "cart_get_p95_latency_ms",
]


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        number = float(value)
        if number < 0:
            return 0.0
        return number
    except (TypeError, ValueError):
        return default


def build_feature_dict(raw_metrics: dict[str, float]) -> dict[str, float]:
    features: dict[str, float] = {}

    for key in FEATURE_ORDER:
        features[key] = _safe_float(raw_metrics.get(key, 0.0))

    return features


def build_feature_vector(feature_dict: dict[str, float]) -> list[float]:
    return [feature_dict[key] for key in FEATURE_ORDER]


def feature_names() -> Iterable[str]:
    return tuple(FEATURE_ORDER)
