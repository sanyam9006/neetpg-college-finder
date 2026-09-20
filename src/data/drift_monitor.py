import numpy as np
from scipy import stats
from typing import Dict, Any, List


class DriftMonitor:
    """
    Monitors data drift between baseline training exam score distribution
    and live inference score requests.
    """

    def __init__(self, baseline_scores: np.ndarray = None):
        if baseline_scores is not None:
            self.baseline_scores = np.asarray(baseline_scores).flatten()
        else:
            # Default reference distribution based on standard NEET PG score curve
            self.baseline_scores = np.random.normal(loc=380, scale=120, size=5000).clip(0, 800)

        self.inference_log: List[float] = []

    def log_score(self, score: float):
        self.inference_log.append(float(score))

    def calculate_psi(self, actual: np.ndarray, expected: np.ndarray, num_bins: int = 10) -> float:
        """
        Calculates the Population Stability Index (PSI).
        PSI < 0.1: No significant distribution change.
        0.1 <= PSI < 0.2: Moderate change.
        PSI >= 0.2: Significant shift / drift detected.
        """
        actual = np.asarray(actual).flatten()
        expected = np.asarray(expected).flatten()

        if len(actual) < 10 or len(expected) < 10:
            return 0.0

        percentiles = np.linspace(0, 100, num_bins + 1)
        bins = np.percentile(expected, percentiles)
        bins[0] = -np.inf
        bins[-1] = np.inf

        expected_counts, _ = np.histogram(expected, bins=bins)
        actual_counts, _ = np.histogram(actual, bins=bins)

        expected_pct = expected_counts / len(expected)
        actual_pct = actual_counts / len(actual)

        # Avoid zero division
        expected_pct = np.where(expected_pct == 0, 1e-4, expected_pct)
        actual_pct = np.where(actual_pct == 0, 1e-4, actual_pct)

        psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(psi)

    def check_drift(self, recent_window: int = 100) -> Dict[str, Any]:
        """
        Runs two-sample Kolmogorov-Smirnov test and PSI on recent logged scores.
        """
        if len(self.inference_log) < 20:
            return {
                "status": "insufficient_data",
                "sample_count": len(self.inference_log),
                "ks_statistic": 0.0,
                "p_value": 1.0,
                "psi": 0.0,
                "drift_detected": False
            }

        recent_scores = np.array(self.inference_log[-recent_window:])
        ks_res = stats.ks_2samp(self.baseline_scores, recent_scores)
        psi_val = self.calculate_psi(recent_scores, self.baseline_scores)

        drift_detected = (ks_res.pvalue < 0.05) or (psi_val >= 0.2)

        return {
            "status": "active",
            "sample_count": len(recent_scores),
            "ks_statistic": float(ks_res.statistic),
            "p_value": float(ks_res.pvalue),
            "psi": round(psi_val, 4),
            "drift_detected": bool(drift_detected),
            "recommendation": "Retrain model with updated shift data" if drift_detected else "Model distribution stable"
        }
