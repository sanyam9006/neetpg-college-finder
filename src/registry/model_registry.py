import os
import json
import datetime
import joblib
from typing import Dict, Any, Optional
from src.models.monotonic_model import MonotonicQuantileRegressor


class ModelRegistry:
    def __init__(self, registry_dir: str = "models"):
        self.registry_dir = registry_dir
        os.makedirs(registry_dir, exist_ok=True)

    def save_model(
        self,
        model: MonotonicQuantileRegressor,
        pattern: int,
        metrics: Dict[str, Any],
        version: str = "latest"
    ) -> str:
        version_dir = os.path.join(self.registry_dir, f"pattern_{pattern}", version)
        os.makedirs(version_dir, exist_ok=True)

        model_path = os.path.join(version_dir, "model.joblib")
        metadata_path = os.path.join(version_dir, "metadata.json")

        joblib.dump(model, model_path)

        metadata = {
            "model_type": "MonotonicQuantileRegressor",
            "pattern": pattern,
            "max_marks": model.max_marks,
            "total_candidates": model.total_candidates,
            "version": version,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "benchmarks_count": len(model.benchmarks),
            "metrics": metrics
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return version_dir

    def load_model(self, pattern: int = 800, version: str = "latest") -> MonotonicQuantileRegressor:
        model_path = os.path.join(self.registry_dir, f"pattern_{pattern}", version, "model.joblib")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found at {model_path}. Please train the model first.")
        return joblib.load(model_path)

    def get_metadata(self, pattern: int = 800, version: str = "latest") -> Dict[str, Any]:
        metadata_path = os.path.join(self.registry_dir, f"pattern_{pattern}", version, "metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Model metadata not found at {metadata_path}")
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
