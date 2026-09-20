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
    print(f"✅ GATE 4 PASSED: Category qualification logic verified.")

    print(f"\nAll 4 Quality Gates PASSED for pattern {pattern}!")
    return True


def run_evaluation_suite():
    all_passed = True
    for pat in [800, 720]:
        passed = evaluate_model_quality_gates(pat)
        if not passed:
            all_passed = False

    if not all_passed:
        print("\n❌ CI/CD Model Gatekeeper: One or more models FAILED quality gates.")
        sys.exit(1)
    else:
        print("\n🚀 CI/CD Model Gatekeeper: ALL MODELS APPROVED FOR PRODUCTION DEPLOYMENT!")
        sys.exit(0)


if __name__ == "__main__":
    run_evaluation_suite()
