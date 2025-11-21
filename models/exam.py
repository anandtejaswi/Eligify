from dataclasses import dataclass
from typing import List


@dataclass
class Exam:
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