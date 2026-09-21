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
We evaluated the model using Leave-One-Out Cross-Validation (LOOCV) against actual NBE benchmark data, compared against a linear interpolation baseline:

| Exam Pattern | Log-Linear Model MAPE | Linear Baseline MAPE | Relative Improvement | P10–P90 Band Coverage |
|---|---|---|---|---|
| **800 Marks (2024–25)** | **4.99%** | 20.98% | **4.2× more accurate** | **91.3%** |
| **720 Marks (2026 Shift)** | **6.29%** | 24.79% | **3.9× more accurate** | **80.0%** |

### 3. What the Uncertainty Bands (P10 / P90) Mean
The model outputs a median estimate ($P_{50}$) alongside optimistic ($P_{10}$, $-12\%$) and conservative ($P_{90}$, $+12\%$) bounds:
- These bounds model **empirical year-to-year exam volatility** (shift difficulty variation, cohort size fluctuations, normalization noise).
- They are **not** Bayesian posterior quantiles from thousands of individual user records.
- On held-out benchmark points, **91.3% of true ranks fall within the P10–P90 interval**.

---

## 🏥 College Cutoff Data & Provenance

### Data Sources
- **All India Quota (AIQ) 50% Round 1 Allotment Results**: Official allotment PDFs published by the Medical Counselling Committee ([mcc.nic.in](https://mcc.nic.in)).
- **Qualifying Percentile Benchmarks**: Official press releases from the National Board of Examinations in Medical Sciences (NBEMS).
- **Coverage**: **351 medical colleges** across 27 Indian states and Union Territories (Government, Private, Deemed Universities, and INI-CET institutes).

### Branch Multipliers (Empirical MCC Ratios)
Because cutoffs are branch-specific, each college's cutoffs across 22 specialties are calibrated against the anchor MD General Medicine closing rank ($3,803$ AIQ R1):

| Specialty | AIQ R1 Overall Closing | Multiplier vs Gen Med | Example: MAMC (Base: 39) | Example: SMS Jaipur (Base: 455) |
|---|---|---|---|---|
| **MD Radio-diagnosis** | ~2,125 | **0.56** | Rank ≤ 22 | Rank ≤ 255 |
| **MD Dermatology** | ~2,639 | **0.69** | Rank ≤ 27 | Rank ≤ 314 |
| **MD General Medicine** | 3,803 | **1.00** | Rank ≤ 39 | Rank ≤ 455 |
| **MD Pediatrics** | ~6,450 | **1.70** | Rank ≤ 66 | Rank ≤ 774 |
| **MS Obstetrics & Gyn.** | ~9,071 | **2.39** | Rank ≤ 93 | Rank ≤ 1,087 |
| **MS General Surgery** | ~10,797 | **2.84** | Rank ≤ 111 | Rank ≤ 1,292 |
| **MS Orthopedics** | ~11,864 | **3.12** | Rank ≤ 122 | Rank ≤ 1,420 |
| **MD Anaesthesiology** | ~20,000 | **5.26** | Rank ≤ 205 | Rank ≤ 2,393 |
| **MD Pathology** | ~35,000 | **9.20** | Rank ≤ 359 | Rank ≤ 4,186 |

### Category Ratios (Relative to UR)
Derived from MCC 2024 Round 1 AIQ General Medicine closing ranks:
- **EWS**: $1.63\times$
- **OBC**: $3.07\times$
- **SC**: $8.50\times$
- **ST**: $13.79\times$
- **PH**: $8.00\times$ (approximate)

### Known Gaps & Limitations
1. **AIQ 50% Round 1 Only**: Cutoffs represent All India Quota Round 1. State 85% quota, institutional internal quotas (e.g. DU, IPU, BHU internal), and stray vacancy rounds are not currently modeled.
2. **Specialty Availability**: Not every college offers all 22 accredited branches; only accredited offerings are displayed per college.
3. **Seat Matrix Changes**: NMC seat approvals change annually; new seats create 6–10% rank softening in later counselling rounds.

---

## 📊 Probabilistic Recommendation & Backtesting

Each recommendation computes:
$$\text{Safety Margin} = \text{Effective Cutoff} - \text{Candidate Rank}$$
$$\text{Safety Ratio} = \frac{\text{Effective Cutoff}}{\text{Candidate Rank}}$$

| Category | Ratio Threshold | Definition |
|---|---|---|
| **🛡️ Safety Seat** | $\text{Ratio} \ge 1.30$ | Cutoff is $\ge 30\%$ above candidate rank (very safe bet) |
| **✨ High Chance** | $1.10 \le \text{Ratio} < 1.30$ | Cutoff is $10\%\text{–}30\%$ above candidate rank |
| **⚖️ Competitive** | $1.00 \le \text{Ratio} < 1.10$ | Cutoff is within $10\%$ of candidate rank (marginal) |
| **🎯 Reach / Ambitious** | $\text{Ratio} < 1.00$ | Cutoff closed above candidate rank in Round 1 |

### Backtesting Results
In automated backtesting over **1,143 college-specialty recommendations** across ranks 500 to 40,000:
- **100% of colleges categorized as "Safety Seat"** had historical closing ranks above the candidate's rank.
- Even under a simulated **10% rank inflation shift**, $>96\%$ of safety-seat recommendations remained safely above closing ranks.

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

### 3. Run Test Suite
```bash
pytest -v
```

### 4. Start FastAPI Microservice
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Prometheus Telemetry: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 5. Docker Deployment
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
5. **Empirical Accuracy Gate (LOOCV)**: Held-out cross-validation MAPE must be $<7.0\%$ (actual: **4.99%** on 800-pattern, **6.29%** on 720-pattern) and must outperform a linear baseline. Interval coverage must be $\ge 80.0\%$ (actual: **91.3%** on 800-pattern).

---

## 🔒 API Hardening & Security
- **Feedback Rate Limiting**: `/api/v1/feedback` enforces in-memory IP-based rate limiting (max 10 requests/minute per client IP) to protect drift logs against spam and data poisoning.
- **Strict Schema Validation**: Request bounds are enforced via Pydantic (`score` $\in [0, 800]$, `rank` $\in [1, 250000]$, `notes` length $\le 500$ chars).
- **Environment Compatibility**: Model metadata records the exact `scikit-learn` and Python versions used during training, warning on major version mismatches upon loading.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
