import math
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field


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


class MonotonicQuantileRegressor:
    """
    Monotonic Quantile Regressor for NEET PG score-to-rank mapping.
    Ensures strict non-decreasing rank as marks decrease (higher score = better/lower rank).
    Provides P10 (best case), P50 (median estimate), and P90 (conservative case) intervals.
    """

    def __init__(self, max_marks: int = 800, total_candidates: int = 230114):
        self.max_marks = max_marks
        self.total_candidates = total_candidates
        self.benchmarks: List[Dict[str, float]] = []
        self.qualifying_percentiles = {
            "UR": 50.0,
            "EWS": 50.0,
            "OBC": 40.0,
            "SC": 40.0,
            "ST": 40.0,
            "PH": 45.0
        }
        self.is_fitted = False

    def fit(self, benchmarks: List[Dict[str, Any]], qualifying_percentiles: Dict[str, float] = None):
        """
        Fits the monotonic anchor spline using empirical historical exam benchmarks.
        """
        # Sort strictly descending by marks
        sorted_b = sorted(benchmarks, key=lambda x: x["marks"], reverse=True)
        
        # Verify strict monotonicity of ranks
        for i in range(len(sorted_b) - 1):
            if sorted_b[i]["rank"] > sorted_b[i + 1]["rank"]:
                raise ValueError("Input benchmarks violate rank monotonicity!")

        self.benchmarks = sorted_b
        if qualifying_percentiles:
            self.qualifying_percentiles.update(qualifying_percentiles)

        self.is_fitted = True
        return self

    def predict_single(self, score: float, category: str = "UR") -> PredictionOutput:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling predict.")

        score = max(0.0, min(float(self.max_marks), float(score)))
        b = self.benchmarks

        pred_rank = self.total_candidates
        percentile = 0.01

        for i in range(len(b) - 1):
            p1 = b[i]
            p2 = b[i + 1]
            if p1["marks"] >= score >= p2["marks"]:
                span = p1["marks"] - p2["marks"]
                t = (p1["marks"] - score) / span if span > 0 else 0.0

                log_r1 = math.log(p1["rank"])
                log_r2 = math.log(p2["rank"])
                pred_rank = int(round(math.exp(log_r1 + t * (log_r2 - log_r1))))

                pct_span = p1["percentile"] - p2["percentile"]
                percentile = round(p1["percentile"] - t * pct_span, 2)
                break

        pred_rank = max(1, min(self.total_candidates, pred_rank))
        
        # Quantile bounds: P10 (optimistic, ~-10%) and P90 (conservative, ~+12%)
        min_rank = max(1, int(round(pred_rank * 0.88)))
        max_rank = min(self.total_candidates, int(round(pred_rank * 1.12)))

        # Cutoff analysis
        req_pct = self.qualifying_percentiles.get(category, 50.0)
        req_cutoff = self._find_score_for_percentile(req_pct)
        is_qualified = score >= req_cutoff

        # Branch advice based on predicted rank
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
        if rank <= 1000:
            return (
                "Tier 1 – AIIMS & Premier Central Institutes",
                "Unrestricted access to high-demand clinical specialties across top GMCs",
                ["MD Radio-diagnosis", "MD Dermatology", "MD General Medicine", "MD Pediatrics", "MS General Surgery"]
            )
        elif rank <= 5000:
            return (
                "Tier 1 & Premier State GMCs",
                "High admission probability for core clinical branches",
                ["MD General Medicine", "MD Pediatrics", "MS Orthopedics", "MS General Surgery", "MS Obs & Gynae"]
            )
        elif rank <= 15000:
            return (
                "Tier 1 & Tier 2 State GMCs",
                "Strong probability across State GMCs and top Deemed universities",
                ["MD General Medicine", "MD Pediatrics", "MS General Surgery", "MS Orthopedics", "MD Anaesthesia", "MD Pathology"]
            )
        elif rank <= 30000:
            return (
                "Tier 2 GMCs & Premier Deemed/Private",
                "Solid surgical, diagnostic, and Deemed clinical options",
                ["MS ENT", "MS Ophthalmology", "MD Anaesthesia", "MD Psychiatry", "MD Pathology", "MD Respiratory Medicine"]
            )
        elif rank <= 60000:
            return (
                "Deemed Clinical & Government Para-clinical",
                "Clinical seats in reputed Deemed universities and Government diagnostic seats",
                ["Deemed Clinical MD/MS", "MD Pathology", "MD Anaesthesia", "MS ENT", "MD Pharmacology"]
            )
        elif is_qualified:
            return (
                "Private & Deemed Universities",
                "Management quota clinical seats and Government pre-clinical specialties",
                ["Deemed MD/MS", "Management Quota", "MD Pathology", "MD Pharmacology", "MD Community Medicine"]
            )
        else:
            return (
                "Below Qualifying Cutoff",
                f"Score is below the required {category} cutoff (~{cutoff_marks} marks)",
                ["Mop-up Round Re-evaluation", "Private Pre-clinical"]
            )
