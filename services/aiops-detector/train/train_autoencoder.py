from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from app.config import MODEL_FILE, SCALER_FILE, THRESHOLD_FILE, TRAINING_DATA_FILE
from app.feature_builder import FEATURE_ORDER


def main() -> None:
    if not TRAINING_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Training data file not found: {TRAINING_DATA_FILE}. "
            "Run generate_training_data.py first."
        )

    data_frame = pd.read_csv(TRAINING_DATA_FILE)

    missing_columns = [name for name in FEATURE_ORDER if name not in data_frame.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in training data: {missing_columns}")

    features = data_frame[FEATURE_ORDER].astype("float32").to_numpy()

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    x_train, x_val = train_test_split(
        scaled_features,
        test_size=0.2,
        random_state=42,
        shuffle=True,
    )

    # MLP autoencoder-like model:
    # input -> hidden -> bottleneck -> hidden -> output
    model = MLPRegressor(
        hidden_layer_sizes=(16, 8, 4, 8, 16),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=min(16, len(x_train)),
        learning_rate_init=1e-3,
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
    )

    model.fit(x_train, x_train)

    reconstructed = model.predict(x_val)
    reconstruction_errors = np.mean(np.square(x_val - reconstructed), axis=1)

    threshold = float(np.percentile(reconstruction_errors, 99))

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    with THRESHOLD_FILE.open("w", encoding="utf-8") as file:
        json.dump({"threshold": threshold}, file, indent=2)

    print(f"Saved model to: {MODEL_FILE}")
    print(f"Saved scaler to: {SCALER_FILE}")
    print(f"Saved threshold to: {THRESHOLD_FILE}")
    print(f"Chosen anomaly threshold: {threshold:.6f}")


if __name__ == "__main__":
    main()
