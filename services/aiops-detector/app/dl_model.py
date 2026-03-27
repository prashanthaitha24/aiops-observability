from __future__ import annotations

from typing import Any

import numpy as np

from .feature_builder import FEATURE_ORDER, build_feature_vector
from .model_registry import ModelRegistry


class DeepLearningAnomalyModel:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

        if not self.registry.artifacts_exist():
            raise FileNotFoundError(
                "Deep learning model artifacts are missing. "
                "Train the model before enabling MODEL_MODE=dl."
            )

        self.model = self.registry.load_model()
        self.scaler = self.registry.load_scaler()
        self.threshold = self.registry.load_threshold()

    def score(self, features: dict[str, float]) -> dict[str, Any]:
        vector = np.array([build_feature_vector(features)], dtype=np.float32)
        scaled_vector = self.scaler.transform(vector)

        reconstructed = self.model.predict(scaled_vector)
        if reconstructed.ndim == 1:
            reconstructed = reconstructed.reshape(1, -1)

        reconstruction_error = float(
            np.mean(np.square(scaled_vector - reconstructed))
        )

        detected = reconstruction_error >= self.threshold

        top_feature_deltas = np.abs(scaled_vector[0] - reconstructed[0])
        top_indices = np.argsort(top_feature_deltas)[::-1][:3]
        reasons = [
            (
                f"{FEATURE_ORDER[index]} contributed strongly to reconstruction error "
                f"({top_feature_deltas[index]:.4f})"
            )
            for index in top_indices
        ]

        normalized_score = min(
            1.0,
            reconstruction_error / self.threshold if self.threshold > 0 else 0.0,
        )

        return {
            "score": round(normalized_score, 4),
            "detected": detected,
            "reconstruction_error": reconstruction_error,
            "reasons": reasons,
            "model_type": "mlp_autoencoder",
        }
