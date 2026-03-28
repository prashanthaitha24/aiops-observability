from __future__ import annotations

from prometheus_client import Gauge, start_http_server


ANOMALY_SCORE = Gauge(
    "aiops_anomaly_score",
    "Current anomaly score calculated by the AIOps detector",
)

ANOMALY_DETECTED = Gauge(
    "aiops_anomaly_detected",
    "1 when anomaly is detected, otherwise 0",
)

DL_ANOMALY_SCORE = Gauge(
    "aiops_dl_anomaly_score",
    "Current deep learning anomaly score calculated by the AIOps detector",
)

DL_ANOMALY_DETECTED = Gauge(
    "aiops_dl_anomaly_detected",
    "1 when deep learning anomaly is detected, otherwise 0",
)

DL_RECONSTRUCTION_ERROR = Gauge(
    "aiops_dl_reconstruction_error",
    "Deep learning autoencoder reconstruction error",
)

FEATURE_FRONTEND_RPS = Gauge(
    "aiops_feature_frontend_rps",
    "Latest frontend requests per second observed by detector",
)

FEATURE_ADS_RPS = Gauge(
    "aiops_feature_ads_rps",
    "Latest ads requests per second observed by detector",
)

FEATURE_CART_ADD_LATENCY_MS = Gauge(
    "aiops_feature_cart_add_latency_ms",
    "Latest average add-to-cart latency in milliseconds",
)

FEATURE_CART_GET_LATENCY_MS = Gauge(
    "aiops_feature_cart_get_latency_ms",
    "Latest average get-cart latency in milliseconds",
)

FEATURE_CART_ADD_P95_LATENCY_MS = Gauge(
    "aiops_feature_cart_add_p95_latency_ms",
    "Latest p95 add-to-cart latency in milliseconds",
)

FEATURE_CART_GET_P95_LATENCY_MS = Gauge(
    "aiops_feature_cart_get_p95_latency_ms",
    "Latest p95 get-cart latency in milliseconds",
)


def start_metrics_server(bind_host: str, port: int) -> None:
    start_http_server(port, addr=bind_host)


def update_metrics(features: dict[str, float], result: dict[str, object]) -> None:
    ANOMALY_SCORE.set(float(result.get("score", 0.0)))
    ANOMALY_DETECTED.set(1.0 if bool(result.get("detected", False)) else 0.0)

    FEATURE_FRONTEND_RPS.set(features.get("frontend_rps", 0.0))
    FEATURE_ADS_RPS.set(features.get("ads_rps", 0.0))
    FEATURE_CART_ADD_LATENCY_MS.set(features.get("cart_add_latency_ms", 0.0))
    FEATURE_CART_GET_LATENCY_MS.set(features.get("cart_get_latency_ms", 0.0))
    FEATURE_CART_ADD_P95_LATENCY_MS.set(features.get("cart_add_p95_latency_ms", 0.0))
    FEATURE_CART_GET_P95_LATENCY_MS.set(features.get("cart_get_p95_latency_ms", 0.0))


def update_dl_metrics(result: dict[str, object]) -> None:
    DL_ANOMALY_SCORE.set(float(result.get("score", 0.0)))
    DL_ANOMALY_DETECTED.set(1.0 if bool(result.get("detected", False)) else 0.0)
    DL_RECONSTRUCTION_ERROR.set(float(result.get("reconstruction_error", 0.0)))
