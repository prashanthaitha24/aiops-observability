from __future__ import annotations

import logging
import time

from .anomaly_model import AnomalyModel
from .config import (
    ANOMALY_THRESHOLD,
    DL_MODEL_ENABLED,
    EXPORTER_BIND_HOST,
    EXPORTER_ENABLED,
    EXPORTER_PORT,
    LOG_LEVEL,
    MODEL_FILE,
    MODEL_MODE,
    POLL_INTERVAL_SECONDS,
    PROMETHEUS_BASE_URL,
    SCALER_FILE,
    THRESHOLD_FILE,
)
from .dl_model import DeepLearningAnomalyModel
from .feature_builder import build_feature_dict, build_feature_vector
from .metrics_exporter import (
    start_metrics_server,
    update_dl_metrics,
    update_metrics,
)
from .model_registry import ModelRegistry
from .prometheus_api_client import PrometheusAPIClient
from .result_publisher import publish_result

logger = logging.getLogger("aiops-detector")


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def build_model() -> object:
    if DL_MODEL_ENABLED:
        registry = ModelRegistry(
            model_file=MODEL_FILE,
            scaler_file=SCALER_FILE,
            threshold_file=THRESHOLD_FILE,
        )
        logger.info("loading deep learning anomaly model")
        return DeepLearningAnomalyModel(registry)

    logger.info("loading baseline anomaly model")
    return AnomalyModel(threshold=ANOMALY_THRESHOLD)


def run_once(
    prometheus_client: PrometheusAPIClient,
    model: object,
) -> dict[str, object]:
    raw_metrics = prometheus_client.fetch_feature_metrics()
    feature_dict = build_feature_dict(raw_metrics)
    _feature_vector = build_feature_vector(feature_dict)

    result = model.score(feature_dict)  # type: ignore[attr-defined]
    update_metrics(feature_dict, result)
    update_dl_metrics(result)
    publish_result(result, feature_dict)

    if EXPORTER_ENABLED:
        update_metrics(feature_dict, result)
        if MODEL_MODE == "dl":
            update_dl_metrics(result)

    return {
        "features": feature_dict,
        "result": result,
    }


def main() -> None:
    configure_logging()
    logger.info("starting aiops detector")
    logger.info("prometheus url: %s", PROMETHEUS_BASE_URL)
    logger.info("poll interval: %s seconds", POLL_INTERVAL_SECONDS)
    logger.info("model mode: %s", MODEL_MODE)

    if EXPORTER_ENABLED:
        start_metrics_server(EXPORTER_BIND_HOST, EXPORTER_PORT)
        logger.info(
            "metrics exporter started on http://%s:%s/metrics",
            EXPORTER_BIND_HOST,
            EXPORTER_PORT,
        )

    prometheus_client = PrometheusAPIClient(PROMETHEUS_BASE_URL)
    model = build_model()

    while True:
        try:
            run_once(prometheus_client, model)
        except KeyboardInterrupt:
            logger.info("detector interrupted, exiting")
            break
        except Exception as exc:
            logger.exception("detector loop failed: %s", exc)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
