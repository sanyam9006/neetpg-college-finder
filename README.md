# NEET PG Rank Predictor & College Recommender

A decision-support tool and ML pipeline for NEET PG All India Rank (AIR) estimation and college discovery across 351 accredited medical colleges in India.

[![CI Quality & Accuracy Gates](https://github.com/sanyam9006/neetpg-college-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/sanyam9006/neetpg-college-finder/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Deploy: Vercel](https://img.shields.io/badge/frontend-Vercel-black.svg)](https://neetpg-college-finder.vercel.app)

---

> ### ⚠️ Important Disclaimer & Medical Advisory
> This project is an **independent decision-support tool** created to help candidates navigate counselling options. It is **not affiliated with or endorsed by the National Board of Examinations (NBE) or the Medical Counselling Committee (MCC)**.
>
> NEET PG ranks and cutoffs vary from year to year based on applicant volume, session difficulty, normalization shifts, and seat additions. **Never base final career or counselling registration decisions solely on predictions.** Always verify real allotment lists and official notifications directly at **[mcc.nic.in](https://mcc.nic.in)** and **[natboard.edu.in](https://natboard.edu.in)**.

---

## 🧭 Overview & What This Tool Solves

During post-NEET PG counselling, students face high uncertainty:
- **Score-to-Rank Mapping**: Converting marks (out of 800 or 720) to an estimated All India Rank (AIR) across shifting percentiles.
- **Branch-Wise Cutoffs**: Cutoffs vary widely by specialty within the same college (e.g., Radio-diagnosis closes at rank ~255 at SMS Jaipur, while General Surgery closes at ~1,292 and Anaesthesia at ~2,393).
- **Category Ratios**: Cutoffs differ significantly across UR, OBC, SC, ST, and EWS categories.

This repository provides:
1. A **monotonic score-to-rank predictor** calibrated against official historical NBE score distributions.
2. A **college recommender** mapping candidate ranks to 351 medical colleges across 22 accredited specialties with branch-wise cutoff breakdowns.
3. A **FastAPI microservice** with CI/CD quality and accuracy gates, telemetry, and rate-limited feedback logging.
4. A **responsive web interface** with light/dark theme support and zero-latency client inference.

---

## 🔬 How the Model Works (No Hype, Just Math)

Score-to-rank conversion in competitive exams is fundamentally a **monotonic inverse mapping** of a cumulative distribution function (CDF). We model this using **piecewise log-linear spline interpolation** between verified historical anchor points.

### 1. Why Log-Linear Interpolation?
In high-stakes exams with ~230,000 candidates, score density is heavily skewed in the upper tail:
- Top 1% ranks grow exponentially (Rank 1 at 800 marks $\to$ Rank 85 at 700 marks $\to$ Rank 3,600 at 600 marks).
- In the mid-range (400–276 marks), density is roughly linear.

A naive **linear interpolation on raw ranks** produces huge errors in top percentiles (e.g., interpolating between 800 and 600 marks linearly predicts rank ~1,800 at 700 marks, when the real rank is ~85). 

Log-linear interpolation ($\ln(\text{rank})$ linear with marks) captures this exponential curvature naturally while maintaining strict monotonicity ($\text{marks}_1 > \text{marks}_2 \implies \text{rank}_1 \le \text{rank}_2$).

### 2. Empirical Validation vs. Baseline (LOOCV)
We evaluated the model using Leave-One-Out Cross-Validation (LOOCV) on published NBE benchmark anchors, compared against a linear interpolation baseline:

| Exam Pattern | Benchmark Anchors (N) | Log-Linear Model MAPE | Linear Baseline MAPE | Relative Improvement | P10–P90 Heuristic Band Coverage |
|---|---|---|---|---|---|
| **800 Marks (2024–25)** | **N = 25** | **4.99%** | 20.98% | **4.2× more accurate** | **91.3%** |
| **720 Marks (2026 Shift)** | **N = 22** | **6.29%** | 24.79% | **3.9× more accurate** | **80.0%** |

### 3. What the Uncertainty Bands (P10 / P90) Mean
The model outputs a median estimate ($P_{50}$) alongside illustrative lower ($P_{10}$, $-12\%$) and upper ($P_{90}$, $+12\%$) bounds:
- These bounds represent a **heuristic score-volatility envelope** reflecting typical annual difficulty shifts and cohort size changes.
- They are **not** parametric Bayesian posterior quantiles.
- Across historical NBE anchors, 91.3% of actual benchmark ranks fall within this envelope.

---

## 🏥 College Cutoff Data & Provenance

### Data Sources & Scope
- **MCC NEET PG 2024 All India Quota (AIQ 50%) Round 1**: Sourced from official seat allotment PDFs published by the Medical Counselling Committee ([mcc.nic.in](https://mcc.nic.in)).
- **Qualifying Percentiles**: Official notification thresholds published by NBEMS.
- **Coverage**: **351 accredited medical colleges** across 27 Indian states and Union Territories.

### Indicative Specialty Multipliers
To provide branch guidance across institutions where full granular round-wise matrices are unavailable, specialty cutoffs are estimated using demand multipliers relative to the college's MD General Medicine Round 1 closing rank ($3,803$ AIQ R1):

| Specialty | AIQ R1 Reference Closing | Multiplier vs Gen Med | Example: MAMC (Base: 39) | Example: SMS Jaipur (Base: 455) |
|---|---|---|---|---|
| **MD Radio-diagnosis** | ~2,125 | **0.56** | Est. R1 ≤ 22 | Est. R1 ≤ 255 |
| **MD Dermatology** | ~2,639 | **0.69** | Est. R1 ≤ 27 | Est. R1 ≤ 314 |
| **MD General Medicine** | 3,803 | **1.00** | Est. R1 ≤ 39 | Est. R1 ≤ 455 |
| **MD Pediatrics** | ~6,450 | **1.70** | Est. R1 ≤ 66 | Est. R1 ≤ 774 |
| **MS Obstetrics & Gyn.** | ~9,071 | **2.39** | Est. R1 ≤ 93 | Est. R1 ≤ 1,087 |
| **MS General Surgery** | ~10,797 | **2.84** | Est. R1 ≤ 111 | Est. R1 ≤ 1,292 |
| **MS Orthopedics** | ~11,864 | **3.12** | Est. R1 ≤ 122 | Est. R1 ≤ 1,420 |
| **MD Anaesthesiology** | ~20,000 | **5.26** | Est. R1 ≤ 205 | Est. R1 ≤ 2,393 |
| **MD Pathology** | ~35,000 | **9.20** | Est. R1 ≤ 359 | Est. R1 ≤ 4,186 |

### Important Data Limitations (Please Read)
1. **Multipliers are Indicative Baselines**: Branch demand varies between colleges (e.g. Radio-diagnosis is comparatively tighter at premier centers than peripheral institutes). Multipliers provide a directional estimate, not official individual cutoffs.
2. **Round 1 is Not the Final Closing Rank**: Seats consistently close at significantly higher (more relaxed) ranks across Round 2, Round 3, and stray vacancy rounds. The tool labels all cutoffs as Round 1 baselines.
3. **Branch Offerings Vary**: Not all 351 colleges offer all 22 branches. The tool displays only accredited specialties per college.
4. **Quota Scope**: All India Quota 50% only. State 85% quotas, institutional quotas (DU, IPU, BHU, AMU), and private management quotas are not modeled.

---

## 📊 Recommendation Decision Boundaries & Consistency

Each recommendation computes candidate distance from indicative Round 1 cutoffs:
$$\text{Safety Ratio} = \frac{\text{Effective Cutoff}}{\text{Candidate Rank}}$$

| Category | Ratio Threshold | Meaning |
|---|---|---|
| **Safety Seat** | $\text{Ratio} \ge 1.30$ | Cutoff is $\ge 30\%$ above candidate rank |
| **High Chance** | $1.05 \le \text{Ratio} < 1.30$ | Cutoff is $5\%\text{–}30\%$ above candidate rank |
| **Competitive** | $0.90 \le \text{Ratio} < 1.05$ | Cutoff is within $\pm 10\%$ of candidate rank |
| **Reach** | $\text{Ratio} < 0.90$ | Cutoff closed well above candidate rank in Round 1 |

Automated gatekeeper tests verify that probability tiers partition rank space consistently and monotonically without boundary inversions across all candidate rank scenarios.


---

## 🏛️ System Architecture & Dual Deployment Modes

```
                        ┌─────────────────────────────────┐
                        │   Web Client (index.html)       │
                        │  - User-friendly medical theme  │
                        │  - Light / Dark mode toggle     │
                        │  - Embedded client engine       │
                        └──────────────┬──────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      │                                 │
           (Standalone Vercel)                  (Full Stack / Docker)
                      │                                 │
                      ▼                                 ▼
         ┌─────────────────────────┐      ┌───────────────────────────┐
         │ Embedded Client Engine  │      │   FastAPI Microservice    │
         │ - Instant offline calc  │      │ - /api/v1/predict         │
         │ - Client-side filtering │      │ - /api/v1/recommend       │
         │ - 351 college database  │      │ - Rate-limited /feedback  │
         └─────────────────────────┘      │ - /metrics (Prometheus)   │
                                          └─────────────┬─────────────┘
                                                        │
                                                        ▼
                                          ┌───────────────────────────┐
                                          │   Model Registry & Gates  │
                                          │ - 5 automated gates in CI │
                                          │ - sklearn version pinning │
                                          │ - LOOCV accuracy gate     │
                                          └───────────────────────────┘
```

### Deployment Transparency
- **Live Demo ([neetpg-college-finder.vercel.app](https://neetpg-college-finder.vercel.app))**: Hosted on Vercel as a static web application. It runs the **embedded client inference engine** with the complete 351-college cutoff database and branch calculations directly in the browser (zero latency, offline capable). The header badge clearly labels whether the local FastAPI microservice is connected or running in client mode.
- **Backend API**: The FastAPI service (`src/api/app.py`), Prometheus telemetry, and drift monitoring can be launched locally via Docker Compose or deployed to container platforms (Render, Fly.io, Cloud Run).

---

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/sanyam9006/neetpg-college-finder.git
cd neetpg-college-finder

# Install locked production dependencies
pip install -r requirements.txt

# Or install with development & testing tools
pip install -r requirements-dev.txt
```

### 2. Run CI/CD Quality & Accuracy Gates
```bash
# Trains models and exports versioned artifacts
python3 -m src.models.train

# Runs 5 quality & accuracy gates (monotonicity, bounds, intervals, sanity, LOOCV accuracy)
python3 -m src.models.evaluate
```

### 3. Run Test Suite (25 Automated Tests)
```bash
pytest -v
```
Includes data pipeline validation, recommender logic, LOOCV accuracy gates, API validation, and a Python-to-JavaScript inference engine parity test (`tests/test_parity.py`).

### 4. Start FastAPI Microservice Locally
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Admin Candidate Dashboard: [http://localhost:8000/admin](http://localhost:8000/admin)
- Prometheus Telemetry: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 5. Cloud Deployment (Render / Railway)

#### Deploy to Render
1. Go to [dashboard.render.com](https://dashboard.render.com) and click **New + → Web Service**.
2. Connect your repository (`neetpg-college-finder`).
3. Set the following settings (or select "Use render.yaml blueprint"):
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && python3 -m src.models.train && python3 -m src.models.evaluate`
   - **Start Command**: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `ADMIN_KEY`: Set your private admin password (e.g. `my_secret_admin_key`).
   - `DB_PATH`: `data/users.db` (or `/data/users.db` if attaching a persistent disk).
5. (Optional Persistent Disk): Under **Disks**, add a disk mounted at `/data` with size 1GB and set `DB_PATH=/data/users.db`.

#### Deploy to Railway
1. Go to [railway.app/new](https://railway.app/new) and select **Deploy from GitHub repo**.
2. Railway detects the root `Dockerfile` and `railway.json` automatically.
3. In **Variables**, add `ADMIN_KEY` and optionally add a Railway **Volume** mounted at `/data` with `DB_PATH=/data/users.db`.

#### Accessing Candidate Registrations
- **Admin Web Dashboard**: Open `https://<your-backend>.onrender.com/admin?admin_key=<your_admin_key>` to view registered candidate details, filter by name/phone/email, and copy all phone numbers for WhatsApp broadcasts.
- **Direct CSV Download**: Download the real-time registration spreadsheet at `https://<your-backend>.onrender.com/api/v1/auth/users/export?admin_key=<your_admin_key>`.

#### Connecting Vercel Frontend to Cloud Backend
Once your Render/Railway backend is live (e.g. `https://neetpg-api.onrender.com`):
- Candidates visiting the site can directly use it by visiting `https://neetpg-college-finder.vercel.app/?backend=https://neetpg-api.onrender.com` (persists automatically in browser `localStorage`), OR
- Add an external rewrite in `vercel.json`:
  ```json
  {
    "rewrites": [
      { "source": "/api/:path*", "destination": "https://<your-backend>.onrender.com/api/:path*" }
    ]
  }
  ```

### 6. Local Docker Deployment
```bash
docker compose -f docker/docker-compose.yml up --build -d
```

---

## 🛡️ Model Quality & Accuracy Gates

Before any model artifact is accepted into `models/`, it must pass **5 automated gates** in `src/models/evaluate.py`:
1. **Strict Monotonicity Gate**: Evaluated across 500 points ($\text{marks}_1 > \text{marks}_2 \implies \text{rank}_1 \le \text{rank}_2$). Zero inversions allowed.
2. **Bounds Gate**: All outputs must strictly lie within $[1, 230114]$.
3. **Interval Integrity Gate**: $P_{10} \le P_{50} \le P_{90}$ must hold universally.
4. **Cutoff Sanity Gate**: Confirms category percentile thresholds.
5. **Empirical Accuracy Gate (LOOCV)**: Held-out cross-validation MAPE must be $<7.0\%$ (actual: **4.99%** on 800-pattern, **6.29%** on 720-pattern) and must outperform a linear baseline.

---

## 🔒 API Hardening & Security
- **Feedback Rate Limiting**: `/api/v1/feedback` enforces in-memory IP-based rate limiting (max 10 requests/minute per client IP) using `X-Forwarded-For` proxy resolution to protect drift logs against spam and data poisoning.
- **Strict Schema Validation**: Request bounds are enforced via Pydantic (`score` $\in [0, 800]$, `rank` $\in [1, 250000]$, `notes` length $\le 500$ chars).
- **Environment Compatibility**: Model metadata records the exact `scikit-learn` and Python versions used during training, warning on major version mismatches upon loading.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
