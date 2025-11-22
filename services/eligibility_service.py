"""Service layer for eligibility checking business logic."""
from typing import List
from models.candidate import Candidate
from models.exam import Exam


class EligibilityService:
    """Service for handling eligibility checks."""
    
    def __init__(self, exams: List[Exam]):
        """Initialize with a list of exams."""
        self.exams = exams
    
    def check_eligibility(self, candidate: Candidate) -> List[Exam]:
        """
        Check which exams a candidate is eligible for.
        
        Args:
            candidate: Candidate object to check eligibility for
            
        Returns:
            List of Exam objects the candidate is eligible for
        """
        eligible_exams = []
        
        for exam in self.exams:
            if exam.is_eligible(candidate):
                eligible_exams.append(exam)
        
        return eligible_exams
    
    def get_all_exams(self) -> List[Exam]:
        """Get all available exams."""
        return self.exams
    
    def get_exam_by_id(self, exam_id: int) -> Exam:
        """Get a specific exam by ID."""
        for exam in self.exams:
            if exam.exam_id == exam_id:
                return exam
        raise ValueError(f"Exam with ID {exam_id} not found")

