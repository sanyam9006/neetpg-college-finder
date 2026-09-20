import time
import os
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
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


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "models_loaded": list(models.keys()),
        "colleges_loaded": len(recommender.colleges) if recommender else 0,
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
def submit_feedback(req: FeedbackRequest):
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
