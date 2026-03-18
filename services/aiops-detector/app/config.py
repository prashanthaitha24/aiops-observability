import os


PROMETHEUS_BASE_URL = os.getenv("PROMETHEUS_BASE_URL", "http://127.0.0.1:9090")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.70"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

EXPORTER_ENABLED = os.getenv("EXPORTER_ENABLED", "true").lower() == "true"
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", "8001"))
EXPORTER_BIND_HOST = os.getenv("EXPORTER_BIND_HOST", "0.0.0.0")
