from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests


@dataclass
class PrometheusClient:
    base_url: str

    def query(self, promql: str) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api/v1/query",
            params={"query": promql},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "success":
            raise ValueError(f"Prometheus query failed: {data}")
        return data

    def query_range(
        self,
        promql: str,
        start: float,
        end: float,
        step: str = "30s",
    ) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api/v1/query_range",
            params={
                "query": promql,
                "start": start,
                "end": end,
                "step": step,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "success":
            raise ValueError(f"Prometheus range query failed: {data}")
        return data

    @staticmethod
    def extract_series_values(data: dict[str, Any]) -> list[float]:
        results = data.get("data", {}).get("result", [])
        values: list[float] = []

        for series in results:
            for item in series.get("values", []):
                if len(item) == 2:
                    try:
                        values.append(float(item[1]))
                    except (TypeError, ValueError):
                        continue

        return values
