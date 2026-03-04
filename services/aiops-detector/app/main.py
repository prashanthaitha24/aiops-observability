import time

import numpy as np
from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response

app = FastAPI(title="AIOps Detector", version="0.1.0")

REQ_COUNT = Counter("aiops_requests_total", "Total requests", ["endpoint"])
REQ_LAT = Histogram("aiops_request_latency_seconds", "Request latency", ["endpoint"])


class ScoreRequest(BaseModel):
    # Window of metric values (single series for MVP). Later we'll accept multivariate.
    values: list[float] = Field(..., min_length=5, description="Metric window values")
    service: str = Field("unknown", description="Service name")


class ScoreResponse(BaseModel):
    service: str
    anomaly_score: float
    anomaly: bool
    top_k_root_causes: list[str]
    rca_summary: str


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
    med = np.median(arr)
    mad = np.median(np.abs(arr - med)) + 1e-9
    z = np.abs(arr[-1] - med) / (1.4826 * mad)
    anomaly_score = float(z)

    anomaly = anomaly_score >= 3.5  # common robust threshold; we'll replace with DL model later

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
