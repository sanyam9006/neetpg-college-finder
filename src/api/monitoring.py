import time
import os
import json
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from src.data.drift_monitor import DriftMonitor

# Prometheus Metric Definitions
REQUESTS_TOTAL = Counter(
    "neetpg_api_requests_total",
    "Total HTTP requests to the NEET PG MLOps API",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION_SECONDS = Histogram(
    "neetpg_api_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"]
)

PREDICTED_RANKS_HISTOGRAM = Histogram(
    "neetpg_predicted_ranks",
    "Distribution of predicted All India Ranks",
    buckets=[100, 1000, 5000, 15000, 30000, 60000, 100000, 150000, 200000, 250000]
)

INPUT_SCORES_HISTOGRAM = Histogram(
    "neetpg_input_scores",
    "Distribution of candidate raw marks",
    buckets=[100, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800]
)

DRIFT_GAUGE = Gauge(
    "neetpg_data_drift_status",
    "Indicates if data drift is detected (1 = drift detected, 0 = stable)"
)

# Global Drift Monitor instance
drift_monitor = DriftMonitor()

FEEDBACK_FILE = "data/processed/user_feedback.jsonl"


def log_feedback_record(record: dict):
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
