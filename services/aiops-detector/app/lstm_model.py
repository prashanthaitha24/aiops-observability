from __future__ import annotations

import math
from collections import deque
from typing import Any

import numpy as np

from .feature_builder import FEATURE_ORDER, build_feature_vector
from .model_registry import ModelRegistry


class LSTMAnomalyModel:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

        if not self.registry.artifacts_exist():
            raise FileNotFoundError(
                "LSTM model artifacts are missing. Train the LSTM model first."
            )

        self.model = self.registry.load_model()
        self.scaler = self.registry.load_scaler()
        self.threshold = self.registry.load_threshold()
        self.metadata = self.registry.load_metadata()

        self.sequence_length = int(self.metadata.get("sequence_length", 10))
        self.buffer: deque[list[float]] = deque(maxlen=self.sequence_length)

    def score(self, features: dict[str, float]) -> dict[str, Any]:
        vector = build_feature_vector(features)
        self.buffer.append(vector)

        # ✅ Warm-up phase
        if len(self.buffer) < self.sequence_length:
            warmup_message = (
                "warming up sequence buffer: "
                f"{len(self.buffer)}/{self.sequence_length}"
            )
            return {
                "score": 0.0,
                "detected": False,
                "reconstruction_error": 0.0,
                "reasons": [warmup_message],
                "model_type": "lstm_autoencoder",
            }

        # ✅ Build sequence
        sequence = np.array([list(self.buffer)], dtype=np.float32)
        original_shape = sequence.shape

        # ✅ Scale sequence
        flat_sequence = sequence.reshape(-1, sequence.shape[-1])
        scaled_flat = self.scaler.transform(flat_sequence)
        scaled_sequence = scaled_flat.reshape(original_shape)

        # ✅ Model inference
        reconstructed = self.model.predict(scaled_sequence, verbose=0)

        if reconstructed.ndim != 3:
            raise ValueError(
                f"Unexpected reconstructed output shape: {reconstructed.shape}"
            )

        # ✅ Reconstruction error
        reconstruction_error = float(
            np.mean(np.square(scaled_sequence - reconstructed))
        )

        # 🔥 CRITICAL FIX: handle NaN / inf safely
        if not math.isfinite(reconstruction_error):
            return {
                "score": 0.0,
                "detected": False,
                "reconstruction_error": 0.0,
                "reasons": [
                    "non-finite reconstruction error detected; fallback applied"
                ],
                "model_type": "lstm_autoencoder",
            }

        detected = reconstruction_error >= self.threshold

        # ✅ Feature-level explainability
        latest_original = scaled_sequence[0, -1, :]
        latest_reconstructed = reconstructed[0, -1, :]

        latest_deltas = np.abs(latest_original - latest_reconstructed)

        # 🔥 Fix NaN in feature deltas
        latest_deltas = np.nan_to_num(
            latest_deltas, nan=0.0, posinf=0.0, neginf=0.0
        )

        top_indices = np.argsort(latest_deltas)[::-1][:3]

        reasons = [
            (
                f"{FEATURE_ORDER[index]} contributed strongly to "
                f"sequence reconstruction error "
                f"({latest_deltas[index]:.4f})"
            )
            for index in top_indices
        ]

        # ✅ Improved scoring (smooth instead of hard saturation)
        if self.threshold > 0:
            normalized_score = reconstruction_error / (
                reconstruction_error + self.threshold
            )
        else:
            normalized_score = 0.0

        return {
            "score": round(normalized_score, 4),
            "detected": detected,
            "reconstruction_error": reconstruction_error,
            "reasons": reasons,
            "model_type": "lstm_autoencoder",
        }
