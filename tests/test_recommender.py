import pytest
from src.recommender.engine import RecommendationEngine, RecommendationRequest


@pytest.fixture
def engine():
    return RecommendationEngine(data_dir="data")


def test_recommender_filters_by_cutoff(engine):
    req = RecommendationRequest(rank=5000, category="UR")
    results = engine.recommend(req)
    assert len(results) > 0
    # Every recommended college must have category_cutoff >= 5000
    for r in results:
        assert r.category_cutoff >= 5000
        assert r.safety_margin >= 0


def test_recommender_state_filter(engine):
    req = RecommendationRequest(rank=10000, category="UR", state="Maharashtra")
    results = engine.recommend(req)
    assert len(results) > 0
    for r in results:
        assert r.state == "Maharashtra"


def test_recommender_specialty_filter(engine):
    spec = "MD General Medicine"
    req = RecommendationRequest(rank=8000, category="UR", specialty=spec)
    results = engine.recommend(req)
    assert len(results) > 0
    for r in results:
        assert spec in r.specialties


def test_recommender_probabilistic_badges(engine):
    req = RecommendationRequest(rank=1000, category="UR")
    results = engine.recommend(req)
    probabilities = {r.admission_probability for r in results}
    assert "Very High / Safety Seat" in probabilities or "High Probability" in probabilities


def test_branch_specific_cutoffs(engine):
    # Radio-diagnosis vs Medicine vs Pathology in the same college
    req_radio = RecommendationRequest(rank=20, category="UR", specialty="MD Radio-diagnosis")
    req_med = RecommendationRequest(rank=100, category="UR", specialty="MD General Medicine")
    req_path = RecommendationRequest(rank=300, category="UR", specialty="MD Pathology")

    results_radio = engine.recommend(req_radio)
    results_med = engine.recommend(req_med)
    results_path = engine.recommend(req_path)

    # In AIIMS New Delhi, Radio cutoff < Med cutoff < Path cutoff
    aiims_radio = next((c for c in results_radio if c.name == "AIIMS New Delhi"), None)
    aiims_med = next((c for c in results_med if c.name == "AIIMS New Delhi"), None)
    aiims_path = next((c for c in results_path if c.name == "AIIMS New Delhi"), None)

    assert aiims_radio is not None
    assert aiims_med is not None
    assert aiims_path is not None
    assert aiims_radio.category_cutoff < aiims_med.category_cutoff < aiims_path.category_cutoff
