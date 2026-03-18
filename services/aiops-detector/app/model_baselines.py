BASELINES: dict[str, float] = {
    "frontend_rps": 1.0,
    "ads_rps": 0.5,
    "cart_add_latency_ms": 120.0,
    "cart_get_latency_ms": 90.0,
    "cart_add_p95_latency_ms": 220.0,
    "cart_get_p95_latency_ms": 180.0,
}

WEIGHTS: dict[str, float] = {
    "frontend_rps": 0.10,
    "ads_rps": 0.05,
    "cart_add_latency_ms": 0.25,
    "cart_get_latency_ms": 0.20,
    "cart_add_p95_latency_ms": 0.25,
    "cart_get_p95_latency_ms": 0.15,
}
