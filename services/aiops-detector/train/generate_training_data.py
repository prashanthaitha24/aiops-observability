from __future__ import annotations

import logging
import time

from app.config import (
    PROMETHEUS_BASE_URL,
    TRAINING_COLLECTION_INTERVAL_SECONDS,
    TRAINING_COLLECTION_SAMPLES,
    TRAINING_DATA_FILE,
)
from app.feature_builder import FEATURE_ORDER, build_feature_dict
from app.prometheus_api_client import PrometheusAPIClient
from app.training_data import TrainingDataWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("training-data-generator")


def main() -> None:
    logger.info("starting telemetry collection for training data")
    logger.info("prometheus url: %s", PROMETHEUS_BASE_URL)
    logger.info("output file: %s", TRAINING_DATA_FILE)
    logger.info("samples: %s", TRAINING_COLLECTION_SAMPLES)
    logger.info(
        "collection interval: %s seconds",
        TRAINING_COLLECTION_INTERVAL_SECONDS,
    )

    prometheus_client = PrometheusAPIClient(PROMETHEUS_BASE_URL)
    writer = TrainingDataWriter(TRAINING_DATA_FILE, list(FEATURE_ORDER))

    for index in range(TRAINING_COLLECTION_SAMPLES):
        raw_metrics = prometheus_client.fetch_feature_metrics()
        features = build_feature_dict(raw_metrics)
        writer.append_row(features)

        logger.info(
            "saved sample %s/%s: %s",
            index + 1,
            TRAINING_COLLECTION_SAMPLES,
            features,
        )

        if index < TRAINING_COLLECTION_SAMPLES - 1:
            time.sleep(TRAINING_COLLECTION_INTERVAL_SECONDS)

    logger.info("training data generation completed")


if __name__ == "__main__":
    main()
