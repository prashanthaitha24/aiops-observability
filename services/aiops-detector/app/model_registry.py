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
        metadata_file: Path | None = None,
    ) -> None:
        self.model_file = model_file
        self.scaler_file = scaler_file
        self.threshold_file = threshold_file
        self.metadata_file = metadata_file

    def artifacts_exist(self) -> bool:
        required = [
            self.model_file.exists(),
            self.scaler_file.exists(),
            self.threshold_file.exists(),
        ]
        if self.metadata_file is not None:
            required.append(self.metadata_file.exists())
        return all(required)

    def load_model(self):
        return joblib.load(self.model_file)

    def load_scaler(self):
        return joblib.load(self.scaler_file)

    def load_threshold(self) -> float:
        with self.threshold_file.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return float(payload["threshold"])

    def load_metadata(self) -> dict:
        if self.metadata_file is None:
            return {}
        with self.metadata_file.open("r", encoding="utf-8") as file:
            return json.load(file)
