from __future__ import annotations

from typing import Any

import requests


class PrometheusAPIClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def query_instant(self, promql: str) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/query"
        response = requests.get(
            url,
            params={"query": promql},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        if payload.get("status") != "success":
            raise RuntimeError(f"Prometheus query failed: {payload}")

        return payload

    def query_scalar(self, promql: str, default: float = 0.0) -> float:
        payload = self.query_instant(promql)
        results = payload.get("data", {}).get("result", [])

        if not results:
            return default

        value = results[0].get("value")
        if not value or len(value) < 2:
            return default

        try:
            return float(value[1])
        except (TypeError, ValueError):
            return default

    def fetch_feature_metrics(self) -> dict[str, float]:
        queries = {
            "frontend_rps": 'sum(rate(app_frontend_requests_total[5m]))',
            "ads_rps": 'sum(rate(app_ads_ad_requests_total[5m]))',
            "cart_add_latency_ms": """
                1000 * (
                  sum(rate(app_cart_add_item_latency_seconds_sum[5m]))
                  /
                  sum(rate(app_cart_add_item_latency_seconds_count[5m]))
                )
            """,
            "cart_get_latency_ms": """
                1000 * (
                  sum(rate(app_cart_get_cart_latency_seconds_sum[5m]))
                  /
                  sum(rate(app_cart_get_cart_latency_seconds_count[5m]))
                )
            """,
            "cart_add_p95_latency_ms": """
                1000 * histogram_quantile(
                  0.95,
                  sum by (le) (rate(app_cart_add_item_latency_seconds_bucket[5m]))
                )
            """,
            "cart_get_p95_latency_ms": """
                1000 * histogram_quantile(
                  0.95,
                  sum by (le) (rate(app_cart_get_cart_latency_seconds_bucket[5m]))
                )
            """,
        }

        metrics: dict[str, float] = {}
        for metric_name, query in queries.items():
            metrics[metric_name] = self.query_scalar(" ".join(query.split()), default=0.0)

        return metrics
