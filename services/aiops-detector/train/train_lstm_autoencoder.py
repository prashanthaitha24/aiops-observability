from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Model
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import LSTM, Dense, Input, RepeatVector, TimeDistributed

FEATURE_ORDER = [
    "frontend_rps",
    "ads_rps",
    "cart_add_latency_ms",
    "cart_get_latency_ms",
    "cart_add_p95_latency_ms",
    "cart_get_p95_latency_ms",
]

DATA_FILE = Path("data/telemetry_training_data.csv")
MODELS_DIR = Path("models")
MODEL_FILE = MODELS_DIR / "lstm_autoencoder.pkl"
SCALER_FILE = MODELS_DIR / "lstm_scaler.pkl"
THRESHOLD_FILE = MODELS_DIR / "lstm_threshold.json"
METADATA_FILE = MODELS_DIR / "lstm_metadata.json"

SEQUENCE_LENGTH = 10
EPOCHS = 30
BATCH_SIZE = 32


def build_sequences(values: np.ndarray, sequence_length: int) -> np.ndarray:
    sequences = []
    for i in range(len(values) - sequence_length + 1):
        sequences.append(values[i : i + sequence_length])
    return np.array(sequences, dtype=np.float32)


def create_model(sequence_length: int, n_features: int) -> Model:
    inputs = Input(shape=(sequence_length, n_features))
    encoded = LSTM(32, activation="tanh", return_sequences=False)(inputs)
    bottleneck = Dense(16, activation="relu")(encoded)

    decoded = RepeatVector(sequence_length)(bottleneck)
    decoded = LSTM(32, activation="tanh", return_sequences=True)(decoded)
    outputs = TimeDistributed(Dense(n_features))(decoded)

    model = Model(inputs, outputs)
    model.compile(optimizer="adam", loss="mse")
    return model


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_FILE)

    missing = [col for col in FEATURE_ORDER if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    values = df[FEATURE_ORDER].astype(float).values

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(values)

    sequences = build_sequences(scaled_values, SEQUENCE_LENGTH)
    if len(sequences) == 0:
        raise ValueError("Not enough rows to build training sequences.")

    model = create_model(SEQUENCE_LENGTH, len(FEATURE_ORDER))

    callbacks = [
        EarlyStopping(
            monitor="loss",
            patience=5,
            restore_best_weights=True,
        )
    ]

    model.fit(
        sequences,
        sequences,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1,
        callbacks=callbacks,
        shuffle=False,
    )

    reconstructed = model.predict(sequences, verbose=0)
    errors = np.mean(np.square(sequences - reconstructed), axis=(1, 2))

    threshold = float(np.percentile(errors, 95))

    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    with THRESHOLD_FILE.open("w", encoding="utf-8") as f:
        json.dump({"threshold": threshold}, f, indent=2)

    with METADATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model_type": "lstm_autoencoder",
                "sequence_length": SEQUENCE_LENGTH,
                "feature_order": FEATURE_ORDER,
            },
            f,
            indent=2,
        )

    print("Saved:")
    print(f"  model: {MODEL_FILE}")
    print(f"  scaler: {SCALER_FILE}")
    print(f"  threshold: {THRESHOLD_FILE}")
    print(f"  metadata: {METADATA_FILE}")
    print(f"  threshold value: {threshold:.6f}")


if __name__ == "__main__":
    main()
