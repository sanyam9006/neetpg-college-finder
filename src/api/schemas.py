from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    score: float = Field(..., ge=0, le=800, description="Raw exam score")
    pattern: int = Field(default=800, description="Exam pattern: 800 or 720")
    category: str = Field(default="UR", description="Category: UR, OBC, SC, ST, EWS, PH")


class PredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    score: float
    max_marks: int
    pattern: int
    category: str
    predicted_rank: int
    min_rank: int
    max_rank: int
    percentile: float
    is_qualified: bool
    qualifying_cutoff_marks: float
    tier_outlook: str
    scope_summary: str
    accessible_branches: List[str]
    model_version: str


class RecommendFilterRequest(BaseModel):
    rank: int = Field(..., ge=1, le=300000)
    category: str = Field(default="UR")
    state: Optional[str] = None
    college_type: Optional[str] = None
    specialty: Optional[str] = None
    tier: Optional[int] = None
    min_rank: Optional[int] = None
    max_rank: Optional[int] = None
    include_reach: bool = False


class UnifiedPredictAndRecommendRequest(BaseModel):
    score: float = Field(..., ge=0, le=800)
    pattern: int = Field(default=800)
    category: str = Field(default="UR")
    state: Optional[str] = None
    college_type: Optional[str] = None
    specialty: Optional[str] = None
    tier: Optional[int] = None
    include_reach: bool = False


class CollegeItem(BaseModel):
    name: str
    state: str
    type: str
    tier: int
    seats: int
    specialties: List[str]
    category_cutoff: int
    safety_margin: int
    admission_probability: str
    probability_badge_color: str
    best_eligible_specialty: Optional[str] = None
    branch_cutoff_display: Optional[str] = None
    is_new_2025: bool
    is_ini_cet: bool


class RecommendResponse(BaseModel):
    total_found: int
    rank_evaluated: int
    category: str
    colleges: List[CollegeItem]


class UnifiedResponse(BaseModel):
    prediction: PredictResponse
    recommendation: RecommendResponse


class FeedbackRequest(BaseModel):
    score: float = Field(..., ge=0, le=800)
    pattern: int = Field(default=800)
    category: str = Field(default="UR")
    predicted_rank: int = Field(..., ge=1)
    actual_rank: int = Field(..., ge=1)
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str
    error_ranks: int
    error_percentage: float
