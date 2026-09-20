import pytest
import numpy as np
from src.data.dataset_loader import DatasetLoader, ExamPatternData, BenchmarkPoint
from src.data.drift_monitor import DriftMonitor


def test_load_valid_patterns():
    loader = DatasetLoader(data_dir="data")
    p800 = loader.load_pattern_data(800)
    assert p800.max_marks == 800
    assert len(p800.benchmarks) > 10

    p720 = loader.load_pattern_data(720)
    assert p720.max_marks == 720
    assert len(p720.benchmarks) > 10


def test_load_colleges():
    loader = DatasetLoader(data_dir="data")
    colleges = loader.load_colleges()
    assert len(colleges) > 200
    first = colleges[0]
    assert "name" in first
    assert "cutoffs" in first
    assert "UR" in first["cutoffs"]


def test_monotonicity_validator_rejects_inverted_data():
    with pytest.raises(ValueError):
        ExamPatternData(
            pattern_name="corrupted",
            max_marks=800,
            total_candidates=200000,
            qualifying_percentiles={"UR": 50.0},
            benchmarks=[
                BenchmarkPoint(marks=700, rank=100, percentile=99.9),
                # Error: higher score (650) with lower rank than 700!
                BenchmarkPoint(marks=650, rank=50, percentile=99.0)
            ]
        )


def test_drift_monitor_no_drift():
    baseline = np.random.normal(400, 100, 1000)
    monitor = DriftMonitor(baseline_scores=baseline)

    for s in np.random.normal(400, 100, 100):
        monitor.log_score(s)

    status = monitor.check_drift()
    assert status["status"] == "active"
    assert status["sample_count"] == 100
    # Similar distributions should not trigger drift
    assert status["psi"] < 0.2


def test_drift_monitor_detects_drift():
    baseline = np.random.normal(300, 50, 1000)
    monitor = DriftMonitor(baseline_scores=baseline)

    # Log severely shifted distribution (mean 600 instead of 300)
    for s in np.random.normal(600, 50, 100):
        monitor.log_score(s)

    status = monitor.check_drift()
    assert status["drift_detected"] is True
    assert status["psi"] >= 0.2
