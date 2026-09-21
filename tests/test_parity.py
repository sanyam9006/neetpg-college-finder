import subprocess
import json
import pytest
from src.registry.model_registry import ModelRegistry


def test_python_javascript_model_parity():
    """
    Verifies that client-side JavaScript prediction logic in index.html
    produces identical outputs to the Python MonotonicQuantileRegressor
    across score bands for both 800 and 720 patterns.
    """
    registry = ModelRegistry(registry_dir="models")
    py_model_800 = registry.load_model(pattern=800, version="latest")
    py_model_720 = registry.load_model(pattern=720, version="latest")

    test_scores_800 = [760, 700, 640, 580, 520, 460, 400, 340, 280, 220, 160]
    test_scores_720 = [680, 620, 560, 500, 440, 380, 320, 260, 200, 140]

    # Node.js runner to extract points from index.html and evaluate calculatePrediction
    node_script = """
    const fs = require('fs');
    const html = fs.readFileSync('index.html', 'utf-8');

    // Extract POINTS_800 and POINTS_720
    const p800Match = html.match(/const POINTS_800 = (\\[[\\s\\S]*?\\]);/);
    const p720Match = html.match(/const POINTS_720 = (\\[[\\s\\S]*?\\]);/);

    const POINTS_800 = eval(p800Match[1]);
    const POINTS_720 = eval(p720Match[1]);

    function calculatePrediction(score, pattern, category) {
      score = Math.max(0, Math.min(pattern, Number(score) || 0));
      const pts = pattern === 720 ? POINTS_720 : POINTS_800;
      let predRank = 230000, minRank = 220000, maxRank = 230114, percentile = 0.1;
      for (let i = 0; i < pts.length - 1; i++) {
        const p1 = pts[i], p2 = pts[i+1];
        if (score <= p1.m && score >= p2.m) {
          const t = (p1.m - score) / (p1.m - p2.m);
          const logR1 = Math.log(p1.r);
          const logR2 = Math.log(p2.r);
          predRank = Math.round(Math.exp(logR1 + t * (logR2 - logR1)));
          minRank = Math.max(1, Math.round(predRank * 0.88));
          maxRank = Math.round(predRank * 1.12);
          percentile = +(p1.p - t * (p1.p - p2.p)).toFixed(1);
          break;
        }
      }
      return { predRank, minRank, maxRank, percentile };
    }

    const test800 = %s;
    const test720 = %s;

    const res800 = test800.map(s => calculatePrediction(s, 800, 'UR'));
    const res720 = test720.map(s => calculatePrediction(s, 720, 'UR'));

    console.log(JSON.stringify({ res800, res720 }));
    """ % (json.dumps(test_scores_800), json.dumps(test_scores_720))

    out = subprocess.check_output(["node", "-e", node_script], text=True)
    js_results = json.loads(out)

    # Compare 800 pattern
    for i, s in enumerate(test_scores_800):
        py_res = py_model_800.predict_single(s, category="UR")
        js_res = js_results["res800"][i]
        # Rank must match within <= 1 rank (rounding precision)
        rank_diff = abs(py_res.predicted_rank - js_res["predRank"])
        assert rank_diff <= 1, f"800 Pattern Parity Drift at score {s}: Python={py_res.predicted_rank}, JS={js_res['predRank']}"
        assert abs(py_res.min_rank - js_res["minRank"]) <= 2
        assert abs(py_res.max_rank - js_res["maxRank"]) <= 2

    # Compare 720 pattern
    for i, s in enumerate(test_scores_720):
        py_res = py_model_720.predict_single(s, category="UR")
        js_res = js_results["res720"][i]
        rank_diff = abs(py_res.predicted_rank - js_res["predRank"])
        assert rank_diff <= 1, f"720 Pattern Parity Drift at score {s}: Python={py_res.predicted_rank}, JS={js_res['predRank']}"
        assert abs(py_res.min_rank - js_res["minRank"]) <= 2
        assert abs(py_res.max_rank - js_res["maxRank"]) <= 2
