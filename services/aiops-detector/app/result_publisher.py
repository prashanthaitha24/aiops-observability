from __future__ import annotations

import logging

logger = logging.getLogger("aiops-detector")


def publish_result(result: dict[str, object], features: dict[str, float]) -> None:
    score = result.get("score", 0.0)
    detected = result.get("detected", False)
    reasons = result.get("reasons", [])

    logger.info("feature snapshot: %s", features)
    logger.info("anomaly score: %s", score)
    logger.info("anomaly detected: %s", detected)

    if reasons:
        logger.warning("anomaly reasons: %s", "; ".join(str(r) for r in reasons))
