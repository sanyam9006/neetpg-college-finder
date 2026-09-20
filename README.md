# NEET PG Score-to-Rank Predictor & College Recommender: MLOps Platform

Production-grade Machine Learning Operations (MLOps) platform for NEET PG All India Rank (AIR) prediction, confidence interval modeling, and probabilistic college recommendation across 818 Indian medical colleges.

---

## 🏛️ System Architecture

```
                               ┌─────────────────────────────┐
                               │  Historical Exam Benchmarks │
                               │   (800 & 720 Mark Formats)  │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │   Dataset Loader & Schema   │
                               │    Validation (Pydantic)    │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
┌──────────────────────────────┐ ┌───────────────────────────┐
│     Model Gatekeeper CI      │ │ Monotonic Quantile Model  │
│  - Strict Monotonicity Gate  │◄┤  - Median Rank (P50)      │
│  - Bounds: [1, 230,114]      │ │  - Optimistic Rank (P10)  │
│  - Interval: P10 <= P50 <= P90 │  - Conservative Rank (P90)│
└──────────────┬───────────────┘ └─────────────┬─────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌───────────────────────────┐
│        Model Registry        │ │   College Recommender     │
│   (Versioned joblib + meta)  │ │  (Probabilistic Matching) │
└──────────────┬───────────────┘ └─────────────┬─────────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │    FastAPI Microservice       │
               │  - /api/v1/predict            │
               │  - /api/v1/recommend          │
               │  - /api/v1/feedback           │
               │  - /metrics (Prometheus)      │
               └───────────────┬───────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
   ┌──────────────────────────┐  ┌───────────────────────────┐
   │     Web Frontend UI      │  │   Observability Stack     │
   │  (Live API + Offline Fall)  │  │ (Prometheus & Drift Mon)  │
   └──────────────────────────┘  └───────────────────────────┘
```

---

## 📁 Repository Structure

```
├── .github/workflows/ci.yml       # Automated GitHub Actions testing & gatekeeping
├── data/
│   ├── raw/                       # Historical exam benchmark datasets (800 & 720 patterns)
│   ├── processed/                 # Feedback logs & drift monitoring records
│   └── college_cutoffs.json       # 818 verified medical colleges cutoff database
├── docker/
│   ├── Dockerfile                 # Multi-stage production container
│   ├── docker-compose.yml         # Containerized API + Prometheus monitoring
│   └── prometheus.yml             # Metric scraping configuration
├── models/                        # Versioned model artifacts (joblib + metadata)
│   ├── pattern_800/latest/
│   └── pattern_720/latest/
├── src/
│   ├── api/                       # FastAPI microservice, Pydantic schemas, Prometheus metrics
│   ├── data/                      # Dataset loader and KS/PSI drift monitor
│   ├── models/                    # Monotonic quantile model, training pipeline, quality gates
│   ├── recommender/               # Probabilistic college recommendation engine
│   └── registry/                  # Model versioning and metadata management
├── tests/                         # Full Pytest unit and integration test suite
├── Makefile                       # Developer shortcuts (`make train`, `make test`, etc.)
├── requirements.txt               # Locked production dependencies
└── index.html                     # Responsive web interface with live API connection & offline fallback
```

---

## ⚡ Quick Start

### 1. Local Environment Setup
```bash
# Clone and enter directory
cd neetpg-college-finder

# Install dependencies
pip install -r requirements.txt
```

### 2. Train & Evaluate Models (Quality Gates)
```bash
# Execute training pipeline
python3 -m src.models.train

# Run automated quality gatekeeper
python3 -m src.models.evaluate
```

### 3. Run Test Suite
```bash
pytest tests/ -v
```

### 4. Start the FastAPI Microservice
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Prometheus Telemetry: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🐳 Docker Deployment

To launch the microservice and Prometheus monitoring stack:
```bash
make docker-up
# Or using docker compose directly:
docker compose -f docker/docker-compose.yml up --build -d
```
- API Endpoint: `http://localhost:8000`
- Prometheus Dashboard: `http://localhost:9090`

---

## 📡 API Reference

### 1. Predict Rank & Percentile
`POST /api/v1/predict`
```json
{
  "score": 540,
  "pattern": 800,
  "category": "UR"
}
```
**Response:**
```json
{
  "score": 540.0,
  "max_marks": 800,
  "pattern": 800,
  "category": "UR",
  "predicted_rank": 12427,
  "min_rank": 10936,
  "max_rank": 13918,
  "percentile": 94.51,
  "is_qualified": true,
  "qualifying_cutoff_marks": 276.0,
  "tier_outlook": "Tier 1 & Tier 2 State GMCs",
  "scope_summary": "Strong probability across State GMCs and top Deemed universities",
  "accessible_branches": [
    "MD General Medicine",
    "MD Pediatrics",
    "MS General Surgery",
    "MS Orthopedics",
    "MD Anaesthesia",
    "MD Pathology"
  ],
  "model_version": "v1.0"
}
```

### 2. Probabilistic College Recommendation
`POST /api/v1/recommend`
```json
{
  "rank": 8500,
  "category": "UR",
  "state": "Maharashtra",
  "college_type": "Government"
}
```

### 3. Log Actual Scorecard Rank (Feedback for Drift Monitoring)
`POST /api/v1/feedback`
```json
{
  "score": 550,
  "pattern": 800,
  "category": "UR",
  "predicted_rank": 10500,
  "actual_rank": 10250,
  "notes": "Shift 1 score verification"
}
```

---

## 🛡️ Model Quality Gates

In CI/CD, every trained model artifact must pass 4 non-negotiable gates:
1. **Monotonicity Gate:** $\forall s_1 > s_2 \implies \text{rank}(s_1) \le \text{rank}(s_2)$ evaluated over 500 continuous test points.
2. **Bounds Gate:** Asserts all predictions are strictly within $[1, 230114]$.
3. **Quantile Gate:** Verifies confidence interval ordering $P_{10} \le P_{50} \le P_{90}$ globally.
4. **Cutoff Sanity Gate:** Validates category-specific qualifying percentile thresholds.
