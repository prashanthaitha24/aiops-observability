from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

PROMETHEUS_BASE_URL = os.getenv("PROMETHEUS_BASE_URL", "http://127.0.0.1:9090")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.70"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

EXPORTER_ENABLED = os.getenv("EXPORTER_ENABLED", "true").lower() == "true"
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", "8001"))
EXPORTER_BIND_HOST = os.getenv("EXPORTER_BIND_HOST", "0.0.0.0")

MODEL_MODE = os.getenv("MODEL_MODE", "baseline").lower()
DL_MODEL_ENABLED = MODEL_MODE == "dl"

TRAINING_DATA_FILE = Path(
    os.getenv("TRAINING_DATA_FILE", str(DATA_DIR / "telemetry_training_data.csv"))
)
MODEL_FILE = Path(os.getenv("MODEL_FILE", str(MODELS_DIR / "autoencoder.joblib")))
SCALER_FILE = Path(os.getenv("SCALER_FILE", str(MODELS_DIR / "scaler.joblib")))
THRESHOLD_FILE = Path(
    os.getenv("THRESHOLD_FILE", str(MODELS_DIR / "threshold.json"))
)

TRAINING_COLLECTION_INTERVAL_SECONDS = int(
    os.getenv("TRAINING_COLLECTION_INTERVAL_SECONDS", "15")
)
TRAINING_COLLECTION_SAMPLES = int(os.getenv("TRAINING_COLLECTION_SAMPLES", "120"))

# Creates directories if they do not exist.
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


#MODELS_DIR = Path(os.getenv("MODELS_DIR", "models"))

DL_MODEL_TYPE = os.getenv("DL_MODEL_TYPE", "mlp_autoencoder")

LSTM_SEQUENCE_LENGTH = int(os.getenv("LSTM_SEQUENCE_LENGTH", "10"))

LSTM_MODEL_FILE = Path(
    os.getenv("LSTM_MODEL_FILE", str(MODELS_DIR / "lstm_autoencoder.pkl"))
)
LSTM_SCALER_FILE = Path(
    os.getenv("LSTM_SCALER_FILE", str(MODELS_DIR / "lstm_scaler.pkl"))
)
LSTM_THRESHOLD_FILE = Path(
    os.getenv("LSTM_THRESHOLD_FILE", str(MODELS_DIR / "lstm_threshold.json"))
)
LSTM_METADATA_FILE = Path(
    os.getenv("LSTM_METADATA_FILE", str(MODELS_DIR / "lstm_metadata.json"))
)
