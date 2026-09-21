import time
import os
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.api.schemas import (
    PredictRequest, PredictResponse,
    RecommendFilterRequest, RecommendResponse, CollegeItem,
    UnifiedPredictAndRecommendRequest, UnifiedResponse,
    FeedbackRequest, FeedbackResponse
)
from src.registry.model_registry import ModelRegistry
from src.recommender.engine import RecommendationEngine, RecommendationRequest
from src.api.monitoring import (
    REQUESTS_TOTAL, REQUEST_DURATION_SECONDS,
    PREDICTED_RANKS_HISTOGRAM, INPUT_SCORES_HISTOGRAM,
    DRIFT_GAUGE, drift_monitor, log_feedback_record
)
from src.api.auth import router as auth_router

# Global model store & recommender
models = {}
recommender: RecommendationEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global models, recommender
    print("Initializing NEET PG MLOps Service...")
    registry = ModelRegistry(registry_dir="models")
    
    # Load models
    for pat in [800, 720]:
        try:
            models[pat] = registry.load_model(pattern=pat, version="latest")
            print(f"Loaded model for pattern {pat}")
        except Exception as e:
            print(f"Warning: Could not load model for pattern {pat}: {e}")

    # Load recommendation engine
    recommender = RecommendationEngine(data_dir="data")
    print(f"Loaded {len(recommender.colleges)} colleges into Recommendation Engine.")
    yield
    print("Shutting down NEET PG MLOps Service...")


app = FastAPI(
    title="NEET PG Marks-to-Rank & College Recommender MLOps API",
    description="Production-grade ML microservice for NEET PG rank prediction, confidence intervals, and college recommendation.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    endpoint = request.url.path
    method = request.method
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    status = str(response.status_code)
    
    REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION_SECONDS.labels(endpoint=endpoint).observe(duration)
    return response


@app.get("/")
def serve_index():
    index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "NEET PG College Finder API is running"}


@app.get("/admin", response_class=HTMLResponse)
def serve_admin():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Candidate Database | NEET PG Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f8fafc;
    --card: #ffffff;
    --border: #e2e8f0;
    --text: #0f172a;
    --muted: #64748b;
    --primary: #0284c7;
    --primary-hover: #0369a1;
    --success: #10b981;
  }
  * { box-sizing: border-box; }
  body { font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px 16px; }
  .container { max-width: 1100px; margin: 0 auto; }
  .header { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 24px; }
  .title-block h1 { margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--primary); }
  .title-block p { margin: 4px 0 0 0; color: var(--muted); font-size: 0.88rem; }
  .actions { display: flex; flex-wrap: wrap; gap: 10px; }
  .btn { display: inline-flex; align-items: center; gap: 6px; padding: 9px 15px; border-radius: 8px; font-weight: 600; font-size: 0.85rem; border: none; cursor: pointer; text-decoration: none; transition: 0.15s; }
  .btn-primary { background: var(--primary); color: #fff; }
  .btn-primary:hover { background: var(--primary-hover); }
  .btn-outline { background: #fff; color: var(--text); border: 1px solid var(--border); }
  .btn-outline:hover { background: #f1f5f9; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .toolbar { display: flex; flex-wrap: wrap; gap: 12px; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .search-box { flex: 1; min-width: 240px; }
  .search-box input { width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.9rem; font-family: inherit; }
  .search-box input:focus { outline: none; border-color: var(--primary); }
  .stat-badge { background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.82rem; }
  .table-responsive { overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }
  table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; min-width: 700px; }
  th { background: #f1f5f9; padding: 12px 14px; font-weight: 600; color: var(--muted); border-bottom: 1px solid var(--border); }
  td { padding: 12px 14px; border-bottom: 1px solid var(--border); }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #f8fafc; }
  .phone-link { color: #0284c7; text-decoration: none; font-weight: 600; }
  .phone-link:hover { text-decoration: underline; }
  .toast { position: fixed; bottom: 24px; right: 24px; background: #0f172a; color: #fff; padding: 10px 18px; border-radius: 8px; font-size: 0.85rem; display: none; z-index: 9999; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
  .auth-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 16px; z-index: 1000; }
  .auth-box { background: #fff; border-radius: 12px; padding: 24px; max-width: 380px; width: 100%; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
  .auth-box h3 { margin: 0 0 8px 0; font-size: 1.15rem; }
  .auth-box p { color: var(--muted); font-size: 0.85rem; margin: 0 0 16px 0; }
  .auth-box input { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.9rem; margin-bottom: 16px; }
</style>
</head>
<body>
<div class="auth-overlay" id="authOverlay" style="display:none">
  <div class="auth-box">
    <h3>🔐 Admin Verification</h3>
    <p>Please enter your <code>ADMIN_KEY</code> to view candidate registrations.</p>
    <form onsubmit="handleAuthSubmit(event)">
      <input type="password" id="adminKeyInput" placeholder="Enter Admin Key..." required />
      <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center">Access Dashboard</button>
    </form>
  </div>
</div>

<div class="container">
  <div class="header">
    <div class="title-block">
      <h1>🩺 Candidate Registrations</h1>
      <p>Real-time database of registered NEET PG medical candidates</p>
    </div>
    <div class="actions">
      <button class="btn btn-outline" onclick="copyAllPhones()">📋 Copy All Phone Numbers</button>
      <button class="btn btn-primary" onclick="downloadCSV()">📥 Export to CSV</button>
    </div>
  </div>

  <div class="card">
    <div class="toolbar">
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="🔍 Search candidate by name, email, or phone..." oninput="filterTable()">
      </div>
      <div>
        <span class="stat-badge" id="countBadge">Loading candidates...</span>
      </div>
    </div>

    <div class="table-responsive">
      <table id="candidateTable">
        <thead>
          <tr>
            <th>#</th>
            <th>Candidate Name</th>
            <th>Email</th>
            <th>Mobile / WhatsApp</th>
            <th>MBBS Batch</th>
            <th>Registered At</th>
          </tr>
        </thead>
        <tbody id="tableBody">
          <tr><td colspan="6" style="text-align:center;color:var(--muted);padding:30px;">Loading candidate records...</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let adminKey = new URLSearchParams(window.location.search).get('admin_key') || sessionStorage.getItem('neetpg_admin_key') || '';
let allCandidates = [];

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(() => { t.style.display = 'none'; }, 3000);
}

function handleAuthSubmit(e) {
  e.preventDefault();
  adminKey = document.getElementById('adminKeyInput').value.trim();
  sessionStorage.setItem('neetpg_admin_key', adminKey);
  document.getElementById('authOverlay').style.display = 'none';
  loadCandidates();
}

async function loadCandidates() {
  if (!adminKey) {
    document.getElementById('authOverlay').style.display = 'flex';
    return;
  }
  try {
    const res = await fetch(`/api/v1/auth/users?admin_key=${encodeURIComponent(adminKey)}`);
    if (res.status === 403) {
      sessionStorage.removeItem('neetpg_admin_key');
      adminKey = '';
      document.getElementById('authOverlay').style.display = 'flex';
      showToast('❌ Invalid Admin Key');
      return;
    }
    const data = await res.json();
    allCandidates = data.users || [];
    renderTable(allCandidates);
  } catch(err) {
    showToast('❌ Failed to fetch candidates: ' + err.message);
  }
}

function renderTable(list) {
  const tbody = document.getElementById('tableBody');
  document.getElementById('countBadge').textContent = `${list.length} Candidate${list.length === 1 ? '' : 's'}`;
  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:30px;">No registered candidates found.</td></tr>';
    return;
  }
  tbody.innerHTML = list.map((c, idx) => `
    <tr>
      <td style="color:var(--muted)">${idx + 1}</td>
      <td><strong>${escapeHtml(c.name)}</strong></td>
      <td>${escapeHtml(c.email)}</td>
      <td><a class="phone-link" href="https://wa.me/91${c.phone.replace(/\\D/g,'')}" target="_blank">📱 ${escapeHtml(c.phone)}</a></td>
      <td><span style="background:#f1f5f9;padding:2px 8px;border-radius:4px;font-size:0.8rem">${escapeHtml(c.batch_year)}</span></td>
      <td style="color:var(--muted);font-size:0.82rem">${new Date(c.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</td>
    </tr>
  `).join('');
}

function filterTable() {
  const q = document.getElementById('searchInput').value.toLowerCase().trim();
  if (!q) { renderTable(allCandidates); return; }
  const filtered = allCandidates.filter(c => 
    c.name.toLowerCase().includes(q) || 
    c.email.toLowerCase().includes(q) || 
    c.phone.toLowerCase().includes(q) ||
    c.batch_year.toLowerCase().includes(q)
  );
  renderTable(filtered);
}

function downloadCSV() {
  if (!adminKey) { document.getElementById('authOverlay').style.display = 'flex'; return; }
  window.open(`/api/v1/auth/users/export?admin_key=${encodeURIComponent(adminKey)}`, '_blank');
}

function copyAllPhones() {
  if (!allCandidates.length) { showToast('No candidate phone numbers to copy.'); return; }
  const phones = allCandidates.map(c => c.phone).filter(Boolean).join(', ');
  navigator.clipboard.writeText(phones).then(() => {
    showToast(`✅ Copied ${allCandidates.length} phone numbers to clipboard!`);
  }).catch(() => {
    showToast('Failed to copy to clipboard.');
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

window.addEventListener('DOMContentLoaded', loadCandidates);
</script>
</body>
</html>
"""



# In-memory IP rate limiter for feedback submissions to prevent spam/poisoning
# Note: Suitable for single-worker or local dev. Multi-worker/multi-pod production would use Redis.
feedback_rate_limits = {}

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def check_feedback_rate_limit(client_ip: str, limit: int = 10, window_seconds: int = 60) -> bool:
    now = time.time()
    timestamps = feedback_rate_limits.get(client_ip, [])
    timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(timestamps) >= limit:
        return False
    timestamps.append(now)
    feedback_rate_limits[client_ip] = timestamps
    return True



@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    loaded_patterns = [p for p, m in models.items() if m is not None]
    colleges_count = len(recommender.colleges) if recommender else 0
    is_healthy = (800 in loaded_patterns or 720 in loaded_patterns) and colleges_count > 0

    return {
        "status": "healthy" if is_healthy else "degraded",
        "models_loaded": loaded_patterns,
        "colleges_loaded": colleges_count,
        "environment": "production"
    }


@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/predict", response_model=PredictResponse)
def predict_rank(req: PredictRequest):
    if req.pattern not in models:
        raise HTTPException(status_code=400, detail=f"Unsupported pattern {req.pattern}. Valid patterns: 800, 720")

    model = models[req.pattern]
    pred = model.predict_single(score=req.score, category=req.category)

    # Record metrics & drift
    INPUT_SCORES_HISTOGRAM.observe(req.score)
    PREDICTED_RANKS_HISTOGRAM.observe(pred.predicted_rank)
    drift_monitor.log_score(req.score)

    return PredictResponse(
        score=pred.score,
        max_marks=pred.max_marks,
        pattern=pred.pattern,
        category=pred.category,
        predicted_rank=pred.predicted_rank,
        min_rank=pred.min_rank,
        max_rank=pred.max_rank,
        percentile=pred.percentile,
        is_qualified=pred.is_qualified,
        qualifying_cutoff_marks=pred.qualifying_cutoff_marks,
        tier_outlook=pred.tier_outlook,
        scope_summary=pred.scope_summary,
        accessible_branches=pred.accessible_branches,
        model_version="v1.0"
    )


@app.post("/api/v1/recommend", response_model=RecommendResponse)
def recommend_colleges(req: RecommendFilterRequest):
    if not recommender:
        raise HTTPException(status_code=503, detail="Recommender service not ready")

    engine_req = RecommendationRequest(
        rank=req.rank,
        category=req.category,
        state=req.state if req.state else None,
        college_type=req.college_type if req.college_type else None,
        specialty=req.specialty if req.specialty else None,
        tier=req.tier if req.tier else None,
        min_rank=req.min_rank,
        max_rank=req.max_rank,
        include_reach_colleges=req.include_reach
    )

    results = recommender.recommend(engine_req)

    items = [
        CollegeItem(
            name=c.name,
            state=c.state,
            type=c.type,
            tier=c.tier,
            seats=c.seats,
            specialties=c.specialties,
            category_cutoff=c.category_cutoff,
            safety_margin=c.safety_margin,
            admission_probability=c.admission_probability,
            probability_badge_color=c.probability_badge_color,
            best_eligible_specialty=c.best_eligible_specialty,
            branch_cutoff_display=c.branch_cutoff_display,
            is_new_2025=c.is_new_2025,
            is_ini_cet=c.is_ini_cet
        ) for c in results
    ]

    return RecommendResponse(
        total_found=len(items),
        rank_evaluated=req.rank,
        category=req.category,
        colleges=items
    )


@app.post("/api/v1/predict-and-recommend", response_model=UnifiedResponse)
def unified_predict_and_recommend(req: UnifiedPredictAndRecommendRequest):
    # Step 1: Predict
    if req.pattern not in models:
        raise HTTPException(status_code=400, detail=f"Unsupported pattern {req.pattern}")

    model = models[req.pattern]
    pred = model.predict_single(score=req.score, category=req.category)

    # Record metrics & drift
    INPUT_SCORES_HISTOGRAM.observe(req.score)
    PREDICTED_RANKS_HISTOGRAM.observe(pred.predicted_rank)
    drift_monitor.log_score(req.score)

    pred_resp = PredictResponse(
        score=pred.score,
        max_marks=pred.max_marks,
        pattern=pred.pattern,
        category=pred.category,
        predicted_rank=pred.predicted_rank,
        min_rank=pred.min_rank,
        max_rank=pred.max_rank,
        percentile=pred.percentile,
        is_qualified=pred.is_qualified,
        qualifying_cutoff_marks=pred.qualifying_cutoff_marks,
        tier_outlook=pred.tier_outlook,
        scope_summary=pred.scope_summary,
        accessible_branches=pred.accessible_branches,
        model_version="v1.0"
    )

    # Step 2: Recommend
    engine_req = RecommendationRequest(
        rank=pred.predicted_rank,
        category=req.category,
        state=req.state if req.state else None,
        college_type=req.college_type if req.college_type else None,
        specialty=req.specialty if req.specialty else None,
        tier=req.tier if req.tier else None,
        min_rank=pred.min_rank,
        max_rank=pred.max_rank,
        include_reach_colleges=req.include_reach
    )
    rec_results = recommender.recommend(engine_req)

    rec_items = [
        CollegeItem(
            name=c.name,
            state=c.state,
            type=c.type,
            tier=c.tier,
            seats=c.seats,
            specialties=c.specialties,
            category_cutoff=c.category_cutoff,
            safety_margin=c.safety_margin,
            admission_probability=c.admission_probability,
            probability_badge_color=c.probability_badge_color,
            best_eligible_specialty=c.best_eligible_specialty,
            branch_cutoff_display=c.branch_cutoff_display,
            is_new_2025=c.is_new_2025,
            is_ini_cet=c.is_ini_cet
        ) for c in rec_results
    ]

    rec_resp = RecommendResponse(
        total_found=len(rec_items),
        rank_evaluated=pred.predicted_rank,
        category=req.category,
        colleges=rec_items
    )

    return UnifiedResponse(
        prediction=pred_resp,
        recommendation=rec_resp
    )


@app.post("/api/v1/feedback", response_model=FeedbackResponse)
def submit_feedback(req: FeedbackRequest, request: Request):
    client_ip = get_client_ip(request)
    if not check_feedback_rate_limit(client_ip, limit=10, window_seconds=60):
        raise HTTPException(
            status_code=429,
            detail="Too many feedback submissions from this IP. Please wait 60 seconds before submitting again."
        )

    err = abs(req.actual_rank - req.predicted_rank)
    err_pct = round((err / req.actual_rank) * 100, 2)

    record = {
        "timestamp": time.time(),
        "score": req.score,
        "pattern": req.pattern,
        "category": req.category,
        "predicted_rank": req.predicted_rank,
        "actual_rank": req.actual_rank,
        "error_ranks": err,
        "error_pct": err_pct,
        "notes": req.notes
    }

    log_feedback_record(record)

    return FeedbackResponse(
        status="success",
        message="Actual result feedback logged for model drift analysis and retraining.",
        error_ranks=err,
        error_percentage=err_pct
    )


@app.get("/api/v1/drift")
def get_drift_status():
    drift_status = drift_monitor.check_drift()
    DRIFT_GAUGE.set(1.0 if drift_status["drift_detected"] else 0.0)
    return drift_status
