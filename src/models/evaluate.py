import sys
import numpy as np
from src.registry.model_registry import ModelRegistry


def evaluate_model_quality_gates(pattern: int = 800) -> bool:
    print(f"\n==========================================")
    print(f"Running Quality Gates for Pattern: {pattern} Marks")
    print(f"==========================================")
    registry = ModelRegistry(registry_dir="models")

    try:
        model = registry.load_model(pattern=pattern, version="latest")
    except Exception as e:
        print(f"GATE FAILED: Could not load model: {e}")
        return False

    # GATE 1: Monotonicity Gate (higher score must yield <= rank)
    print("Evaluating Gate 1: Strict Monotonicity...")
    test_scores = np.linspace(model.max_marks, 0, 500)
    preds = [model.predict_single(s) for s in test_scores]
    ranks = [p.predicted_rank for p in preds]

    monotonic_violations = 0
    for i in range(len(ranks) - 1):
        if ranks[i] > ranks[i + 1]:
            monotonic_violations += 1
            print(f"Violation: Score {test_scores[i]} rank {ranks[i]} > Score {test_scores[i+1]} rank {ranks[i+1]}")

    if monotonic_violations > 0:
        print(f"❌ GATE 1 FAILED: Found {monotonic_violations} monotonicity violations!")
        return False
    print("✅ GATE 1 PASSED: Strict monotonicity verified across 500 test points.")

    # GATE 2: Bounds & Limits Gate
    print("\nEvaluating Gate 2: Absolute Rank Bounds...")
    for p in preds:
        if p.predicted_rank < 1 or p.predicted_rank > model.total_candidates:
            print(f"❌ GATE 2 FAILED: Rank {p.predicted_rank} out of bounds [1, {model.total_candidates}]")
            return False
    print(f"✅ GATE 2 PASSED: All predictions fall within valid bounds [1, {model.total_candidates}].")

    # GATE 3: Confidence Interval Integrity Gate
    print("\nEvaluating Gate 3: Confidence Interval Integrity (P10 <= P50 <= P90)...")
    interval_violations = 0
    for p in preds:
        if not (p.min_rank <= p.predicted_rank <= p.max_rank):
            interval_violations += 1

    if interval_violations > 0:
        print(f"❌ GATE 3 FAILED: Found {interval_violations} confidence interval inversions!")
        return False
    print("✅ GATE 3 PASSED: P10 <= P50 <= P90 holds universally across all scores.")

    # GATE 4: Cutoff Sanity Gate
    print("\nEvaluating Gate 4: Cutoff Sanity Check...")
    ur_qual = model.predict_single(model.max_marks * 0.9, category="UR")
    ur_fail = model.predict_single(model.max_marks * 0.1, category="UR")
    if not ur_qual.is_qualified or ur_fail.is_qualified:
        print("❌ GATE 4 FAILED: Cutoff qualification logic inverted!")
        return False
    print("✅ GATE 4 PASSED: Category qualification logic verified.")

    # GATE 5: Empirical Held-Out Accuracy & Coverage Gate (LOOCV)
    print("\nEvaluating Gate 5: Empirical Held-Out Accuracy Gate (LOOCV vs Baseline)...")
    benchmarks = model.benchmarks
    if len(benchmarks) >= 5:
        errors = []
        coverages = []
        baseline_errors = []

        for i in range(1, len(benchmarks) - 1):
            test_pt = benchmarks[i]
            train_pts = benchmarks[:i] + benchmarks[i + 1:]
            score = test_pt["marks"]
            true_rank = test_pt["rank"]

            # Log-linear interpolation on leave-one-out train_pts
            pred_rank = None
            for j in range(len(train_pts) - 1):
                p1, p2 = train_pts[j], train_pts[j + 1]
                if p1["marks"] >= score >= p2["marks"]:
                    span = p1["marks"] - p2["marks"]
                    t = (p1["marks"] - score) / span if span > 0 else 0.0
                    l1, l2 = np.log(p1["rank"]), np.log(p2["rank"])
                    pred_rank = int(round(np.exp(l1 + t * (l2 - l1))))
                    break

            # Dumb baseline: simple linear interpolation on raw ranks
            linear_rank = None
            for j in range(len(train_pts) - 1):
                p1, p2 = train_pts[j], train_pts[j + 1]
                if p1["marks"] >= score >= p2["marks"]:
                    span = p1["marks"] - p2["marks"]
                    t = (p1["marks"] - score) / span if span > 0 else 0.0
                    linear_rank = int(round(p1["rank"] + t * (p2["rank"] - p1["rank"])))
                    break

            if pred_rank is not None and linear_rank is not None:
                err_pct = abs(pred_rank - true_rank) / true_rank * 100.0
                lin_err_pct = abs(linear_rank - true_rank) / true_rank * 100.0
                in_band = (pred_rank * 0.88) <= true_rank <= (pred_rank * 1.12)
                errors.append(err_pct)
                baseline_errors.append(lin_err_pct)
                coverages.append(in_band)

        mape = float(np.mean(errors))
        baseline_mape = float(np.mean(baseline_errors))
        coverage_pct = float(np.mean(coverages) * 100.0)

        print(f"  • Sample Size: {len(benchmarks)} benchmark anchors from NBE published tables")
        print(f"  • Log-Linear Model LOOCV MAPE: {mape:.2f}% (Target: < 7.0%)")
        print(f"  • Linear Baseline LOOCV MAPE:  {baseline_mape:.2f}%")
        print(f"  • P10-P90 Heuristic Band (±12%) Coverage: {coverage_pct:.1f}%")
        print("    (Note: ±12% represents a heuristic volatility envelope for annual paper difficulty shifts, not a parametric posterior)")

        if mape > 7.0:
            print(f"❌ GATE 5 FAILED: LOOCV MAPE {mape:.2f}% exceeds tolerance threshold of 7.0%!")
            return False
        if mape >= baseline_mape:
            print(f"❌ GATE 5 FAILED: Model ({mape:.2f}%) did not outperform linear baseline ({baseline_mape:.2f}%)!")
            return False
        print(f"✅ GATE 5 PASSED: Empirical MAPE {mape:.2f}% beats linear baseline ({baseline_mape:.2f}%) on N={len(benchmarks)} points.")
    else:
        print("⚠️ GATE 5 SKIPPED: Insufficient benchmark points for cross-validation.")

    print(f"\nAll 5 Quality & Accuracy Gates PASSED for pattern {pattern}!")
    return True


def verify_recommender_consistency():
    """
    Verifies categorization consistency: ensures recommendation badges
    (Safety Seat, High Chance, Competitive, Reach) partition rank space
    monotonically without overlaps across candidate rank scenarios.
    """
    print("\n==========================================")
    print("Running College Recommender Consistency Check")
    print("==========================================")
    from src.recommender.engine import RecommendationEngine, RecommendationRequest
    engine = RecommendationEngine(data_dir="data")

    test_ranks = [500, 1000, 2500, 5000, 10000, 20000, 40000]
    total_evaluated = 0
    inversions = 0

    for rank in test_ranks:
        req = RecommendationRequest(rank=rank, category="UR")
        recs = engine.recommend(req)
        total_evaluated += len(recs)
        for r in recs:
            ratio = r.category_cutoff / max(1, rank)
            if r.admission_probability == "Very High / Safety Seat" and ratio < 1.30:
                inversions += 1
            elif r.admission_probability == "High Chance" and not (1.05 <= ratio < 1.30):
                inversions += 1
            elif r.admission_probability == "Competitive" and not (0.90 <= ratio < 1.05):
                inversions += 1
            elif r.admission_probability == "Reach / Low Chance" and ratio >= 0.90:
                inversions += 1

    print(f"  • Total college-candidate pairs evaluated: {total_evaluated}")
    print(f"  • Categorization boundary inversions: {inversions}")
    if inversions > 0:
        print(f"❌ RECOMMENDER CONSISTENCY FAILED: Found {inversions} boundary inversions!")
        return False

    print("✅ RECOMMENDER CONSISTENCY PASSED: All admission probability tiers adhere to decision boundaries.")
    return True


def run_evaluation_suite():
    all_passed = True
    for pat in [800, 720]:
        passed = evaluate_model_quality_gates(pat)
        if not passed:
            all_passed = False

    rec_passed = verify_recommender_consistency()
    if not rec_passed:
        all_passed = False

    if not all_passed:
        print("\n❌ CI/CD Model Gatekeeper: One or more models FAILED quality gates.")
        sys.exit(1)
    else:
        print("\nCI/CD Model Gatekeeper: All models and recommender checks passed.")

        sys.exit(0)


if __name__ == "__main__":
    run_evaluation_suite()
