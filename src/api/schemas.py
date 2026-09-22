from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class CandidateCategory(str, Enum):
    UR = "UR"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"
    PH = "PH"


class ExamPattern(int, Enum):
    PATTERN_800 = 800
    PATTERN_720 = 720


class PredictRequest(BaseModel):
    score: float = Field(..., ge=0, le=800, description="Raw exam score")
    pattern: ExamPattern = Field(default=ExamPattern.PATTERN_800, description="Exam pattern: 800 or 720")
    category: CandidateCategory = Field(default=CandidateCategory.UR, description="Category: UR, OBC, SC, ST, EWS, PH")

    @model_validator(mode="after")
    def validate_score_within_pattern(self) -> "PredictRequest":
        max_allowed = float(self.pattern.value if hasattr(self.pattern, "value") else self.pattern)
        if self.score > max_allowed:
            raise ValueError(f"Score {self.score} cannot exceed max marks ({max_allowed}) for pattern {self.pattern}.")
        return self


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
    category: CandidateCategory = Field(default=CandidateCategory.UR)
    state: Optional[str] = Field(default=None, max_length=100)
    college_type: Optional[str] = Field(default=None, max_length=50)
    specialty: Optional[str] = Field(default=None, max_length=100)
    tier: Optional[int] = Field(default=None, ge=1, le=3)
    min_rank: Optional[int] = Field(default=None, ge=1)
    max_rank: Optional[int] = Field(default=None, le=300000)
    include_reach: bool = False


class UnifiedPredictAndRecommendRequest(BaseModel):
    score: float = Field(..., ge=0, le=800)
    pattern: ExamPattern = Field(default=ExamPattern.PATTERN_800)
    category: CandidateCategory = Field(default=CandidateCategory.UR)
    state: Optional[str] = Field(default=None, max_length=100)
    college_type: Optional[str] = Field(default=None, max_length=50)
    specialty: Optional[str] = Field(default=None, max_length=100)
    tier: Optional[int] = Field(default=None, ge=1, le=3)
    include_reach: bool = False

    @model_validator(mode="after")
    def validate_score_within_pattern(self) -> "UnifiedPredictAndRecommendRequest":
        max_allowed = float(self.pattern.value if hasattr(self.pattern, "value") else self.pattern)
        if self.score > max_allowed:
            raise ValueError(f"Score {self.score} cannot exceed max marks ({max_allowed}) for pattern {self.pattern}.")
        return self


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
    pattern: ExamPattern = Field(default=ExamPattern.PATTERN_800)
    category: CandidateCategory = Field(default=CandidateCategory.UR)
    predicted_rank: int = Field(..., ge=1, le=250000)
    actual_rank: int = Field(..., ge=1, le=250000)
    notes: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_score_within_pattern(self) -> "FeedbackRequest":
        max_allowed = float(self.pattern.value if hasattr(self.pattern, "value") else self.pattern)
        if self.score > max_allowed:
            raise ValueError(f"Score {self.score} cannot exceed max marks ({max_allowed}) for pattern {self.pattern}.")
        return self


class FeedbackResponse(BaseModel):
    status: str
    message: str
    error_ranks: int
    error_percentage: float
