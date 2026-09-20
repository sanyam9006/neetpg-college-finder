import json
import os
from typing import Dict, List, Any, Tuple
from pydantic import BaseModel, Field, field_validator
import numpy as np


class BenchmarkPoint(BaseModel):
    marks: float = Field(..., ge=0)
    rank: int = Field(..., ge=1)
    percentile: float = Field(..., ge=0, le=100)


class ExamPatternData(BaseModel):
    pattern_name: str
    max_marks: int
    total_candidates: int
    qualifying_percentiles: Dict[str, float]
    benchmarks: List[BenchmarkPoint]

    @field_validator("benchmarks")
    @classmethod
    def validate_monotonicity(cls, benchmarks: List[BenchmarkPoint]) -> List[BenchmarkPoint]:
        # Benchmarks should be ordered descending by marks
        sorted_b = sorted(benchmarks, key=lambda x: x.marks, reverse=True)
        for i in range(len(sorted_b) - 1):
            curr = sorted_b[i]
            nxt = sorted_b[i + 1]
            if curr.rank > nxt.rank:
                raise ValueError(
                    f"Monotonicity violation: score {curr.marks} has rank {curr.rank} > score {nxt.marks} rank {nxt.rank}"
                )
        return sorted_b


class DatasetLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.raw_dir = os.path.join(data_dir, "raw")
        self.college_file = os.path.join(data_dir, "college_cutoffs.json")

    def load_pattern_data(self, pattern: int = 800) -> ExamPatternData:
        filename = f"neetpg_historical_{pattern}.json"
        path = os.path.join(self.raw_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Pattern dataset not found at {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ExamPatternData(**data)

    def load_colleges(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.college_file):
            raise FileNotFoundError(f"College cutoffs not found at {self.college_file}")

        with open(self.college_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_synthetic_samples(
        self, pattern_data: ExamPatternData, n_samples: int = 2000, noise_std: float = 0.03
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates synthetic student score vs rank training and validation pairs
        using log-linear piecewise interpolation of empirical benchmarks with realistic exam noise.
        """
        benchmarks = sorted(pattern_data.benchmarks, key=lambda x: x.marks, reverse=True)
        scores = np.linspace(0, pattern_data.max_marks, n_samples)
        ranks = []

        for score in scores:
            for i in range(len(benchmarks) - 1):
                p1 = benchmarks[i]
                p2 = benchmarks[i + 1]
                if score <= p1.marks and score >= p2.marks:
                    t = (p1.marks - score) / (p1.marks - p2.marks) if (p1.marks != p2.marks) else 0
                    log_r1 = np.log(p1.rank)
                    log_r2 = np.log(p2.rank)
                    base_rank = np.exp(log_r1 + t * (log_r2 - log_r1))
                    
                    # Add subtle realistic variation
                    noise = np.random.normal(0, noise_std)
                    noisy_rank = max(1, min(pattern_data.total_candidates, int(base_rank * (1 + noise))))
                    ranks.append(noisy_rank)
                    break
            else:
                ranks.append(pattern_data.total_candidates)

        return scores.reshape(-1, 1), np.array(ranks)
