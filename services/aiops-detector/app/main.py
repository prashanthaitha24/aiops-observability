from __future__ import annotations

import logging
import time

from .anomaly_model import AnomalyModel
from .config import (
    ANOMALY_THRESHOLD,
    EXPORTER_BIND_HOST,
    EXPORTER_ENABLED,
    EXPORTER_PORT,
    LOG_LEVEL,
    POLL_INTERVAL_SECONDS,
    PROMETHEUS_BASE_URL,
)
from .feature_builder import build_feature_dict, build_feature_vector
from .metrics_exporter import start_metrics_server, update_metrics
from .prometheus_api_client import PrometheusAPIClient
from .result_publisher import publish_result


logger = logging.getLogger("aiops-detector")


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def run_once(
    prometheus_client: PrometheusAPIClient,
    anomaly_model: AnomalyModel,
) -> dict[str, object]:
    raw_metrics = prometheus_client.fetch_feature_metrics()
    feature_dict = build_feature_dict(raw_metrics)
    _feature_vector = build_feature_vector(feature_dict)

    result = anomaly_model.score(feature_dict)
    publish_result(result, feature_dict)

    if EXPORTER_ENABLED:
        update_metrics(feature_dict, result)

    return {
        "features": feature_dict,
        "result": result,
    }


def main() -> None:
    configure_logging()
    logger.info("starting aiops detector")
    logger.info("prometheus url: %s", PROMETHEUS_BASE_URL)
    logger.info("poll interval: %s seconds", POLL_INTERVAL_SECONDS)
    logger.info("anomaly threshold: %s", ANOMALY_THRESHOLD)

    if EXPORTER_ENABLED:
        start_metrics_server(EXPORTER_BIND_HOST, EXPORTER_PORT)
        logger.info(
            "metrics exporter started on http://%s:%s/metrics",
            EXPORTER_BIND_HOST,
            EXPORTER_PORT,
        )

    prometheus_client = PrometheusAPIClient(PROMETHEUS_BASE_URL)
    anomaly_model = AnomalyModel(threshold=ANOMALY_THRESHOLD)

    while True:
        try:
            run_once(prometheus_client, anomaly_model)
        except KeyboardInterrupt:
            logger.info("detector interrupted, exiting")
            break
        except Exception as exc:
            logger.exception("detector loop failed: %s", exc)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
