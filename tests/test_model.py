import pytest
import numpy as np
from src.registry.model_registry import ModelRegistry
from src.models.monotonic_model import MonotonicQuantileRegressor


@pytest.fixture
def model_800():
    registry = ModelRegistry(registry_dir="models")
    return registry.load_model(pattern=800, version="latest")


@pytest.fixture
def model_720():
    registry = ModelRegistry(registry_dir="models")
    return registry.load_model(pattern=720, version="latest")


def test_monotonicity_across_range(model_800):
    scores = np.linspace(800, 0, 100)
    ranks = [model_800.predict_single(s).predicted_rank for s in scores]

    for i in range(len(ranks) - 1):
        assert ranks[i] <= ranks[i + 1], f"Monotonicity failed at score {scores[i]}: {ranks[i]} > {ranks[i+1]}"


def test_confidence_interval_ordering(model_800):
    for s in [750, 620, 540, 450, 320, 200]:
        pred = model_800.predict_single(s)
        assert pred.min_rank <= pred.predicted_rank <= pred.max_rank
        assert 1 <= pred.min_rank <= model_800.total_candidates
        assert 1 <= pred.max_rank <= model_800.total_candidates


def test_category_qualification(model_800):
    # Score 280: >276 -> UR Qualified
    pred_ur_pass = model_800.predict_single(280, category="UR")
    assert pred_ur_pass.is_qualified is True

    # Score 260: <276 -> UR Not Qualified
    pred_ur_fail = model_800.predict_single(260, category="UR")
    assert pred_ur_fail.is_qualified is False

    # Score 260: >245 -> OBC Qualified!
    pred_obc_pass = model_800.predict_single(260, category="OBC")
    assert pred_obc_pass.is_qualified is True


def test_720_pattern_model(model_720):
    pred = model_720.predict_single(600, category="UR")
    assert pred.max_marks == 720
    assert pred.predicted_rank < 5000
    assert pred.percentile > 98.0


def test_empirical_accuracy_loocv():
    from src.models.evaluate import evaluate_model_quality_gates, verify_recommender_consistency
    assert evaluate_model_quality_gates(800) is True
    assert evaluate_model_quality_gates(720) is True
    assert verify_recommender_consistency() is True

