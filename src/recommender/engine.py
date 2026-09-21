from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from src.data.dataset_loader import DatasetLoader

# Recognized 22 NEET PG Specialties with empirical cutoff multipliers relative to MD General Medicine
# Exact ratios from MCC NEET PG 2024 AIQ Round 1 branch-wise closing ranks / MD General Medicine (3,803)
SPECIALTY_MULTIPLIERS: Dict[str, float] = {
    # Super-Competitive Clinical
    "MD Radio-diagnosis": 0.56,
    "MD Dermatology, Venereology & Leprosy": 0.69,
    "MD General Medicine": 1.00,  # Base clinical anchor
    "MD Pediatrics": 1.70,
    # Core Surgical & Clinical
    "MS Obstetrics & Gynaecology": 2.39,
    "MS General Surgery": 2.84,
    "MS Orthopedics": 3.12,
    "MS Ophthalmology": 3.68,
    "MD Respiratory Medicine": 3.94,
    "MS ENT": 4.21,
    # Secondary Clinical & Diagnostic
    "MD Psychiatry": 4.87,
    "MD Anaesthesiology": 5.26,
    "MD Emergency Medicine": 5.79,
    "MD Radiation Oncology": 6.58,
    # Para-Clinical
    "MD Pathology": 9.20,
    "MD Microbiology": 14.46,
    "MD Community Medicine": 15.78,
    "MD Pharmacology": 17.09,
    "MD Forensic Medicine": 18.41,
    # Pre-Clinical
    "MD Physiology": 22.35,
    "MD Biochemistry": 23.67,
    "MD Anatomy": 26.30
}


class CollegeRecommendation(BaseModel):
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


class RecommendationRequest(BaseModel):
    rank: int = Field(..., ge=1, le=300000)
    category: str = Field(default="UR")
    state: Optional[str] = None
    college_type: Optional[str] = None
    specialty: Optional[str] = None
    tier: Optional[int] = None
    min_rank: Optional[int] = None
    max_rank: Optional[int] = None
    include_reach_colleges: bool = False


class RecommendationEngine:
    def __init__(self, data_dir: str = "data"):
        loader = DatasetLoader(data_dir=data_dir)
        self.colleges = loader.load_colleges()

    def get_specialty_cutoff(self, base_cutoff: int, specialty: str) -> int:
        mult = SPECIALTY_MULTIPLIERS.get(specialty, 1.0)
        return min(230114, max(1, int(round(base_cutoff * mult))))

    def find_best_eligible_specialty(self, base_cutoff: int, user_rank: int, offered_specialties: List[str]) -> Tuple[Optional[str], int]:
        """
        Finds the highest-demand specialty that the candidate qualifies for in this college.
        """
        # Order specialties from most competitive to least competitive
        sorted_specs = sorted(offered_specialties, key=lambda s: SPECIALTY_MULTIPLIERS.get(s, 1.0))
        for sp in sorted_specs:
            sp_cutoff = self.get_specialty_cutoff(base_cutoff, sp)
            if user_rank <= sp_cutoff:
                return sp, sp_cutoff

        # If none strictly qualified, check the most accessible branch
        if sorted_specs:
            last_sp = sorted_specs[-1]
            return last_sp, self.get_specialty_cutoff(base_cutoff, last_sp)

        return None, base_cutoff

    def recommend(self, req: RecommendationRequest) -> List[CollegeRecommendation]:
        user_rank = req.rank
        cat = req.category
        p10 = req.min_rank or int(user_rank * 0.88)
        p90 = req.max_rank or int(user_rank * 1.12)

        recommendations = []

        for col in self.colleges:
            # Filter checks
            if req.state and col["state"] != req.state:
                continue
            if req.college_type and col["type"] != req.college_type:
                continue
            if req.tier and col["tier"] != req.tier:
                continue
            if req.specialty and req.specialty not in col["specialties"]:
                continue

            # Base category cutoff (MD General Medicine anchor)
            base_cutoff = col["cutoffs"].get(cat, col["cutoffs"].get("UR", 50000))

            if req.specialty:
                # Specific branch evaluation
                effective_cutoff = self.get_specialty_cutoff(base_cutoff, req.specialty)
                best_sp = req.specialty
                branch_display = f"{req.specialty}: {effective_cutoff:,}"
            else:
                # General evaluation across all offered branches
                best_sp, effective_cutoff = self.find_best_eligible_specialty(base_cutoff, user_rank, col["specialties"])
                min_sp_cutoff = self.get_specialty_cutoff(base_cutoff, "MD Radio-diagnosis")
                max_sp_cutoff = self.get_specialty_cutoff(base_cutoff, "MD Pathology")
                branch_display = f"Clinical ~{base_cutoff:,} | Para ~{max_sp_cutoff:,}"

            margin = effective_cutoff - user_rank

            # Determine eligibility
            if user_rank > effective_cutoff and not (req.include_reach_colleges and margin >= -0.10 * effective_cutoff):
                continue

            # Admission probability scoring based on confidence intervals
            if effective_cutoff >= p90 * 1.25:
                prob = "Very High / Safety Seat"
                badge = "#10b981"
            elif effective_cutoff >= user_rank * 1.10:
                prob = "High Probability"
                badge = "#06b6d4"
            elif effective_cutoff >= user_rank:
                prob = "Moderate / Competitive"
                badge = "#f59e0b"
            else:
                prob = "Reach / Ambitious (R2/R3)"
                badge = "#ec4899"

            rec = CollegeRecommendation(
                name=col["name"],
                state=col["state"],
                type=col["type"],
                tier=col["tier"],
                seats=col["seats"],
                specialties=col["specialties"],
                category_cutoff=effective_cutoff,
                safety_margin=margin,
                admission_probability=prob,
                probability_badge_color=badge,
                best_eligible_specialty=best_sp,
                branch_cutoff_display=branch_display,
                is_new_2025=col.get("is_new_2025", False),
                is_ini_cet=col["type"] == "INI-CET"
            )
            recommendations.append(rec)

        # Sort by effective cutoff rank ascending
        recommendations.sort(key=lambda x: x.category_cutoff)
        return recommendations
