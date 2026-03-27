from __future__ import annotations

import json
from pathlib import Path

import joblib


class ModelRegistry:
    def __init__(
        self,
        model_file: Path,
        scaler_file: Path,
        threshold_file: Path,
    ) -> None:
        self.model_file = model_file
        self.scaler_file = scaler_file
        self.threshold_file = threshold_file

    def artifacts_exist(self) -> bool:
        return (
            self.model_file.exists()
            and self.scaler_file.exists()
            and self.threshold_file.exists()
        )

    def load_model(self):
        return joblib.load(self.model_file)

    def load_scaler(self):
        return joblib.load(self.scaler_file)

    def load_threshold(self) -> float:
        with self.threshold_file.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return float(payload["threshold"])
