from app.anomaly_model import AnomalyModel
from app.feature_builder import build_feature_dict, build_feature_vector


def test_build_feature_vector_order() -> None:
    raw_metrics = {
        "frontend_rps": 1.2,
        "ads_rps": 0.4,
        "cart_add_latency_ms": 12.3,
        "cart_get_latency_ms": 8.7,
        "cart_add_p95_latency_ms": 25.0,
        "cart_get_p95_latency_ms": 18.0,
    }

    feature_dict = build_feature_dict(raw_metrics)
    feature_vector = build_feature_vector(feature_dict)

    assert feature_vector == [1.2, 0.4, 12.3, 8.7, 25.0, 18.0]


def test_anomaly_model_detects_large_deviation() -> None:
    model = AnomalyModel(threshold=0.2)

    features = {
        "frontend_rps": 3.0,
        "ads_rps": 1.5,
        "cart_add_latency_ms": 500.0,
        "cart_get_latency_ms": 400.0,
        "cart_add_p95_latency_ms": 900.0,
        "cart_get_p95_latency_ms": 700.0,
    }

    result = model.score(features)

    assert result["score"] > 0.2
    assert result["detected"] is True


def test_anomaly_model_normal_case() -> None:
    model = AnomalyModel(threshold=0.7)

    features = {
        "frontend_rps": 1.0,
        "ads_rps": 0.5,
        "cart_add_latency_ms": 100.0,
        "cart_get_latency_ms": 80.0,
        "cart_add_p95_latency_ms": 220.0,
        "cart_get_p95_latency_ms": 180.0,
    }

    result = model.score(features)

    assert result["score"] == 0.0
    assert result["detected"] is False
