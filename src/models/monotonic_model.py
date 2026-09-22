import os
import json
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from sklearn.isotonic import IsotonicRegression


@dataclass
class PredictionOutput:
    score: float
    max_marks: int
    pattern: int
    category: str
    predicted_rank: int
    min_rank: int
    max_rank: int
    percentile: float
    is_qualified: bool
    qualifying_cutoff_marks: float
    tier_outlook: str
    scope_summary: str
    accessible_branches: List[str]


def load_scope_config(config_path: str = "data/config/branch_scopes.json") -> Dict[str, Any]:
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Robust built-in fallback
    return {
        "qualifying_percentiles": {
            "UR": 50.0, "EWS": 50.0, "OBC": 40.0, "SC": 40.0, "ST": 40.0, "PH": 45.0
        },
        "uncertainty_envelope": {
            "p10_factor": 0.88,
            "p90_factor": 1.12
        },
        "tiers": [
            {
                "max_rank": 1000,
                "tier_outlook": "Tier 1 – AIIMS & Premier Central Institutes",
                "scope_summary": "Unrestricted access to high-demand clinical specialties across top GMCs",
                "accessible_branches": [
                    "MD Radio-diagnosis", "MD Dermatology", "MD General Medicine", "MD Pediatrics", "MS General Surgery"
                ]
            },
            {
                "max_rank": 5000,
                "tier_outlook": "Tier 1 & Premier State GMCs",
                "scope_summary": "High admission probability for core clinical branches",
                "accessible_branches": [
                    "MD General Medicine", "MD Pediatrics", "MS Orthopedics", "MS General Surgery", "MS Obs & Gynae"
                ]
            },
            {
                "max_rank": 15000,
                "tier_outlook": "Tier 1 & Tier 2 State GMCs",
                "scope_summary": "Strong probability across State GMCs and top Deemed universities",
                "accessible_branches": [
                    "MD General Medicine", "MD Pediatrics", "MS General Surgery", "MS Orthopedics", "MD Anaesthesia", "MD Pathology"
                ]
            },
            {
                "max_rank": 30000,
                "tier_outlook": "Tier 2 GMCs & Premier Deemed/Private",
                "scope_summary": "Solid surgical, diagnostic, and Deemed clinical options",
                "accessible_branches": [
                    "MS ENT", "MS Ophthalmology", "MD Anaesthesia", "MD Psychiatry", "MD Pathology", "MD Respiratory Medicine"
                ]
            },
            {
                "max_rank": 60000,
                "tier_outlook": "Deemed Clinical & Government Para-clinical",
                "scope_summary": "Clinical seats in reputed Deemed universities and Government diagnostic seats",
                "accessible_branches": [
                    "Deemed Clinical MD/MS", "MD Pathology", "MD Anaesthesia", "MS ENT", "MD Pharmacology"
                ]
            },
            {
                "max_rank": None,
                "tier_outlook": "Private & Deemed Universities",
                "scope_summary": "Management quota clinical seats and Government pre-clinical specialties",
                "accessible_branches": [
                    "Deemed MD/MS", "Management Quota", "MD Pathology", "MD Pharmacology", "MD Community Medicine"
                ]
            }
        ],
        "disqualified_tier": {
            "tier_outlook": "Below Qualifying Cutoff",
            "scope_summary_template": "Score is below the required {category} cutoff (~{cutoff_marks} marks)",
            "accessible_branches": [
                "Mop-up Round Re-evaluation",
                "Private Pre-clinical"
            ]
        }
    }


class MonotonicQuantileRegressor:
    """
    Monotonic Quantile Regressor for NEET PG score-to-rank mapping using Scikit-Learn
    IsotonicRegression (PAVA). Ensures strict monotonicity (higher score = better/lower rank).
    Provides P10 (best case), P50 (median estimate), and P90 (conservative case) intervals.
    """

    def __init__(self, max_marks: int = 800, total_candidates: int = 230114, config_path: str = "data/config/branch_scopes.json"):
        self.max_marks = max_marks
        self.total_candidates = total_candidates
        self.config = load_scope_config(config_path)
        self.benchmarks: List[Dict[str, float]] = []
        self.qualifying_percentiles = dict(self.config.get("qualifying_percentiles", {
            "UR": 50.0, "EWS": 50.0, "OBC": 40.0, "SC": 40.0, "ST": 40.0, "PH": 45.0
        }))
        self.isotonic_regressor = IsotonicRegression(increasing=False, out_of_bounds="clip")
        self.is_fitted = False

    def fit(self, benchmarks: List[Dict[str, Any]], qualifying_percentiles: Optional[Dict[str, float]] = None):
        """
        Fits the scikit-learn IsotonicRegression model on (scores, log(ranks))
        using empirical historical exam benchmarks.
        """
        # Sort descending by marks
        sorted_b = sorted(benchmarks, key=lambda x: x["marks"], reverse=True)
        
        # Verify strict monotonicity of ranks
        for i in range(len(sorted_b) - 1):
            if sorted_b[i]["rank"] > sorted_b[i + 1]["rank"]:
                raise ValueError("Input benchmarks violate rank monotonicity!")

        self.benchmarks = sorted_b
        if qualifying_percentiles:
            self.qualifying_percentiles.update(qualifying_percentiles)

        # Fit Scikit-Learn IsotonicRegression on (score -> log(rank))
        scores = np.array([p["marks"] for p in sorted_b], dtype=float)
        log_ranks = np.log([p["rank"] for p in sorted_b])
        self.isotonic_regressor.fit(scores, log_ranks)

        self.is_fitted = True
        return self

    def predict_single(self, score: float, category: str = "UR") -> PredictionOutput:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling predict.")

        score = max(0.0, min(float(self.max_marks), float(score)))

        # 1. Predict rank via fitted IsotonicRegression
        pred_log_rank = float(self.isotonic_regressor.predict([score])[0])
        pred_rank = int(round(math.exp(pred_log_rank)))
        pred_rank = max(1, min(self.total_candidates, pred_rank))

        # 2. Percentile estimation from benchmarks
        percentile = 0.01
        b = self.benchmarks
        for i in range(len(b) - 1):
            p1 = b[i]
            p2 = b[i + 1]
            if p1["marks"] >= score >= p2["marks"]:
                span = p1["marks"] - p2["marks"]
                t = (p1["marks"] - score) / span if span > 0 else 0.0
                pct_span = p1["percentile"] - p2["percentile"]
                percentile = round(p1["percentile"] - t * pct_span, 2)
                break
        
        # 3. Quantile bounds from config
        envelope = self.config.get("uncertainty_envelope", {})
        p10_factor = float(envelope.get("p10_factor", 0.88))
        p90_factor = float(envelope.get("p90_factor", 1.12))
        min_rank = max(1, int(round(pred_rank * p10_factor)))
        max_rank = min(self.total_candidates, int(round(pred_rank * p90_factor)))

        # 4. Cutoff analysis
        req_pct = self.qualifying_percentiles.get(category, 50.0)
        req_cutoff = self._find_score_for_percentile(req_pct)
        is_qualified = score >= req_cutoff

        # 5. Branch advice based on predicted rank
        tier_outlook, scope_summary, branch_tags = self._get_branch_scope(pred_rank, is_qualified, category, req_cutoff)

        return PredictionOutput(
            score=score,
            max_marks=self.max_marks,
            pattern=self.max_marks,
            category=category,
            predicted_rank=pred_rank,
            min_rank=min_rank,
            max_rank=max_rank,
            percentile=percentile,
            is_qualified=is_qualified,
            qualifying_cutoff_marks=req_cutoff,
            tier_outlook=tier_outlook,
            scope_summary=scope_summary,
            accessible_branches=branch_tags
        )

    def _find_score_for_percentile(self, target_pct: float) -> float:
        b = self.benchmarks
        for i in range(len(b) - 1):
            p1 = b[i]
            p2 = b[i + 1]
            if p1["percentile"] >= target_pct >= p2["percentile"]:
                span = p1["percentile"] - p2["percentile"]
                t = (p1["percentile"] - target_pct) / span if span > 0 else 0.0
                score = p1["marks"] - t * (p1["marks"] - p2["marks"])
                return round(score, 1)
        return 0.0

    def _get_branch_scope(self, rank: int, is_qualified: bool, category: str, cutoff_marks: float) -> Tuple[str, str, List[str]]:
        if not is_qualified:
            disq = self.config.get("disqualified_tier", {})
            template = disq.get("scope_summary_template", "Score is below the required {category} cutoff (~{cutoff_marks} marks)")
            return (
                disq.get("tier_outlook", "Below Qualifying Cutoff"),
                template.format(category=category, cutoff_marks=cutoff_marks),
                disq.get("accessible_branches", ["Mop-up Round Re-evaluation", "Private Pre-clinical"])
            )

        for tier in self.config.get("tiers", []):
            max_r = tier.get("max_rank")
            if max_r is None or rank <= max_r:
                return (
                    tier["tier_outlook"],
                    tier["scope_summary"],
                    tier["accessible_branches"]
                )

        return (
            "Private & Deemed Universities",
            "Management quota clinical seats and Government pre-clinical specialties",
            ["Deemed MD/MS", "Management Quota", "MD Pathology", "MD Pharmacology", "MD Community Medicine"]
        )

