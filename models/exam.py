from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Exam:
    """Exam model representing exam eligibility criteria."""
    exam_id: int
    exam_name: str
    conducting_body: str
    exam_level: str
    exam_mode: str
    website: str
    fee_gen_ews: int
    total_duration_mins: int
    min_age: int
    max_age: int
    min_10_percent: float
    min_12_percent: float
    min_ug_cgpa: float
    subjects: List[str]
    documents: List[str]

    def __post_init__(self):
        """Validate exam data after initialization."""
        self.validate()

    def validate(self):
        """Validate exam fields."""
        errors = []
        
        if not isinstance(self.exam_id, int) or self.exam_id <= 0:
            errors.append("Exam ID must be a positive integer")
        
        if not self.exam_name or len(self.exam_name.strip()) < 3:
            errors.append("Exam name must be at least 3 characters")
        
        if not isinstance(self.min_age, int) or self.min_age < 0:
            errors.append("Minimum age must be a non-negative integer")
        
        if not isinstance(self.max_age, int) or self.max_age < self.min_age:
            errors.append("Maximum age must be greater than or equal to minimum age")
        
        if not isinstance(self.min_10_percent, (int, float)) or self.min_10_percent < 0 or self.min_10_percent > 100:
            errors.append("Minimum 10th percentage must be between 0 and 100")
        
        if not isinstance(self.min_12_percent, (int, float)) or self.min_12_percent < 0 or self.min_12_percent > 100:
            errors.append("Minimum 12th percentage must be between 0 and 100")
        
        if not isinstance(self.min_ug_cgpa, (int, float)) or self.min_ug_cgpa < 0 or self.min_ug_cgpa > 10:
            errors.append("Minimum UG CGPA must be between 0 and 10")
        
        if errors:
            raise ValueError("; ".join(errors))

    def is_eligible(self, candidate) -> bool:
        """Check if a candidate is eligible for this exam."""
        # Age check
        if candidate.age < self.min_age or candidate.age > self.max_age:
            return False
        
        # Academic checks
        if candidate.p10 < self.min_10_percent:
            return False
        
        if candidate.p12 < self.min_12_percent:
            return False
        
        if candidate.ug_cgpa < self.min_ug_cgpa:
            return False
        
        return True

    def to_dict(self) -> dict:
        """Convert exam to dictionary."""
        return {
            'exam_id': self.exam_id,
            'exam_name': self.exam_name,
            'conducting_body': self.conducting_body,
            'exam_level': self.exam_level,
            'exam_mode': self.exam_mode,
            'website': self.website,
            'fee_gen_ews': self.fee_gen_ews,
            'total_duration_mins': self.total_duration_mins,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'min_10_percent': self.min_10_percent,
            'min_12_percent': self.min_12_percent,
            'min_ug_cgpa': self.min_ug_cgpa,
            'subjects': self.subjects,
            'documents': self.documents
        }
