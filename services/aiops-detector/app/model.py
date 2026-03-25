import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    def __init__(self):
        # contamination = expected anomaly ratio
        self.model = IsolationForest(contamination=0.1, random_state=42)

    def score(self, values):
        values = np.array(values).reshape(-1, 1)

        # Fit on provided window
        self.model.fit(values)

        # Last value is the newest metric
        latest = values[-1].reshape(1, -1)

        anomaly_score = float(self.model.decision_function(latest)[0])
        anomaly_flag = bool(self.model.predict(latest)[0] == -1)

        return anomaly_score, anomaly_flag
