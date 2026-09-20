from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from src.data.dataset_loader import DatasetLoader

# Recognized 22 NEET PG Specialties with empirical cutoff multipliers relative to MD General Medicine
SPECIALTY_MULTIPLIERS: Dict[str, float] = {
    # Clinical (Super-Competitive)
    "MD Radio-diagnosis": 0.28,
    "MD Dermatology, Venereology & Leprosy": 0.45,
    "MD General Medicine": 1.00,  # Base clinical anchor
    "MD Pediatrics": 1.15,
    # Core Surgical & Clinical
    "MS Obstetrics & Gynaecology": 1.30,
    "MS Orthopedics": 1.25,
    "MS General Surgery": 1.40,
    "MD Respiratory Medicine": 1.45,
    # Secondary Clinical & Diagnostic
    "MS Ophthalmology": 1.65,
    "MS ENT": 1.75,
    "MD Psychiatry": 1.90,
    "MD Anaesthesiology": 2.20,
    "MD Emergency Medicine": 2.00,
    "MD Radiation Oncology": 2.40,
    # Para-Clinical
    "MD Pathology": 3.80,
    "MD Microbiology": 5.20,
    "MD Pharmacology": 6.00,
    "MD Forensic Medicine": 6.50,
    "MD Community Medicine": 5.80,
    # Pre-Clinical
    "MD Physiology": 8.50,
    "MD Biochemistry": 9.00,
    "MD Anatomy": 10.50
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
