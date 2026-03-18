import time

import numpy as np
import os
from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response
from .model import AnomalyDetector
from .prometheus_client import PrometheusClient

app = FastAPI(title="AIOps Detector", version="0.1.0")

REQ_COUNT = Counter("aiops_requests_total", "Total requests", ["endpoint"])
REQ_LAT = Histogram("aiops_request_latency_seconds", "Request latency", ["endpoint"])
detector = AnomalyDetector()
#PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus-server.otel-demo.svc.cluster.local")
PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://prometheus.otel-demo.svc.cluster.local:9090",
)
prom_client = PrometheusClient(PROMETHEUS_URL)

class ScoreRequest(BaseModel):
    # Window of metric values (single series for MVP). Later we'll accept multivariate.
    values: list[float] = Field(..., min_length=5, description="Metric window values")
    service: str = Field("unknown", description="Service name")


class PrometheusScoreRequest(BaseModel):
    service: str = Field(..., description="Service name")
    metric_query: str = Field(..., description="PromQL query")
    window_minutes: int = Field(10, ge=1, le=60, description="Lookback window in minutes")
    step: str = Field("30s", description="Prometheus query step")

class ScoreResponse(BaseModel):
    service: str
    anomaly_score: float
    anomaly: bool
    top_k_root_causes: list[str]
    rca_summary: str


@app.get("/")
def root():
    return {
        "service": "aiops-detector",
        "status": "ok",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "metrics": "/metrics",
            "score": "/score",
        },
    }

@app.get("/health")
def health():
    REQ_COUNT.labels(endpoint="/health").inc()
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    # Prometheus scrape endpoint
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    start = time.time()
    REQ_COUNT.labels(endpoint="/score").inc()

    arr = np.array(req.values, dtype=float)

    # MVP anomaly score: robust z-score-ish using median and MAD (no training yet)
    #med = np.median(arr)
    #mad = np.median(np.abs(arr - med)) + 1e-9
    #z = np.abs(arr[-1] - med) / (1.4826 * mad)
    #anomaly_score = float(z)

    #anomaly = anomaly_score >= 3.5  # common robust threshold; we'll replace with DL model later
    # Isolation Forest anomaly detection
    anomaly_score, anomaly = detector.score(arr)
    # MVP RCA: placeholder — later we’ll rank using service graph + multi-metric lead/lag
    top_k = [req.service] if anomaly else []

    summary = (
        f"Anomaly detected for service={req.service}. "
        f"Score={anomaly_score:.2f}. "
        f"Likely root candidates: {top_k if top_k else 'none'}."
    )

    REQ_LAT.labels(endpoint="/score").observe(time.time() - start)

    return ScoreResponse(
        service=req.service,
        anomaly_score=anomaly_score,
        anomaly=anomaly,
        top_k_root_causes=top_k,
        rca_summary=summary,
    )

@app.post("/score/prometheus", response_model=ScoreResponse)
def score_prometheus(req: PrometheusScoreRequest):
    start_time = time.time()
    REQ_COUNT.labels(endpoint="/score/prometheus").inc()

    end_ts = time.time()
    start_ts = end_ts - (req.window_minutes * 60)

    data = prom_client.query_range(
        promql=req.metric_query,
        start=start_ts,
        end=end_ts,
        step=req.step,
    )
    values = prom_client.extract_series_values(data)

    if len(values) < 5:
        REQ_LAT.labels(endpoint="/score/prometheus").observe(time.time() - start_time)
        return ScoreResponse(
            service=req.service,
            anomaly_score=0.0,
            anomaly=False,
            top_k_root_causes=[],
            rca_summary=f"Not enough data points returned from Prometheus for service={req.service}.",
        )

    arr = np.array(values, dtype=float)
    anomaly_score, anomaly = detector.score(arr)

    top_k = [req.service] if anomaly else []
    summary = (
        f"Prometheus-based anomaly detection for service={req.service}. "
        f"Score={anomaly_score:.2f}. "
        f"Likely root candidates: {top_k if top_k else 'none'}."
    )

    REQ_LAT.labels(endpoint="/score/prometheus").observe(time.time() - start_time)

    return ScoreResponse(
        service=req.service,
        anomaly_score=anomaly_score,
        anomaly=anomaly,
        top_k_root_causes=top_k,
        rca_summary=summary,
    )
