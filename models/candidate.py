from dataclasses import dataclass
from typing import Optional


@dataclass
class Candidate:
    first_name: str
    dob: str
    email: str
    category: str
    p10: float
    p12: float
    ug_cgpa: float
    age: Optional[int] = None