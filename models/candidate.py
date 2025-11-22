from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
import re


@dataclass
class Candidate:
    """Candidate model with validation."""
    first_name: str
    dob: str
    email: str
    category: str
    p10: float
    p12: float
    ug_cgpa: float
    age: Optional[int] = None

    def __post_init__(self):
        """Validate candidate data after initialization."""
        self.validate()

    def validate(self):
        """Validate all candidate fields."""
        errors = []
        
        # Validate first name
        if not self.first_name or not isinstance(self.first_name, str):
            errors.append("First name is required and must be a string")
        elif len(self.first_name.strip()) < 2:
            errors.append("First name must be at least 2 characters")
        elif len(self.first_name) > 100:
            errors.append("First name must be less than 100 characters")
        elif not re.match(r'^[a-zA-Z\s\-\.]+$', self.first_name):
            errors.append("First name contains invalid characters")
        
        # Validate email
        if not self.email or not isinstance(self.email, str):
            errors.append("Email is required")
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            errors.append("Invalid email format")
        elif len(self.email) > 100:
            errors.append("Email must be less than 100 characters")
        
        # Validate category
        valid_categories = ['GEN', 'EWS', 'OBC-NCL', 'SC', 'ST']
        if self.category not in valid_categories:
            errors.append(f"Category must be one of: {', '.join(valid_categories)}")
        
        # Validate DOB
        try:
            dob_date = datetime.strptime(self.dob, '%Y-%m-%d').date()
            if dob_date > date.today():
                errors.append("Date of birth cannot be in the future")
            # Check reasonable age (0-150 years)
            age_calc = (date.today() - dob_date).days // 365
            if age_calc < 0 or age_calc > 150:
                errors.append("Invalid date of birth")
        except (ValueError, TypeError):
            errors.append("Invalid date format. Use YYYY-MM-DD")
        
        # Validate percentages (0-100)
        if not isinstance(self.p10, (int, float)) or self.p10 < 0 or self.p10 > 100:
            errors.append("10th percentage must be between 0 and 100")
        
        if not isinstance(self.p12, (int, float)) or self.p12 < 0 or self.p12 > 100:
            errors.append("12th percentage must be between 0 and 100")
        
        # Validate CGPA (0-10)
        if not isinstance(self.ug_cgpa, (int, float)) or self.ug_cgpa < 0 or self.ug_cgpa > 10:
            errors.append("UG CGPA must be between 0 and 10")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        # Calculate age if not provided
        if self.age is None:
            try:
                dob_date = datetime.strptime(self.dob, '%Y-%m-%d').date()
                today = date.today()
                self.age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            except (ValueError, TypeError):
                pass

    @classmethod
    def from_dict(cls, data: dict) -> 'Candidate':
        """Create Candidate instance from dictionary with validation."""
        return cls(
            first_name=data.get('first_name', '').strip(),
            dob=data.get('dob', ''),
            email=data.get('email', '').strip().lower(),
            category=data.get('category', ''),
            p10=float(data.get('p10', 0)),
            p12=float(data.get('p12', 0)),
            ug_cgpa=float(data.get('ug_cgpa', 0))
        )

    def to_dict(self) -> dict:
        """Convert candidate to dictionary."""
        return {
            'first_name': self.first_name,
            'dob': self.dob,
            'email': self.email,
            'category': self.category,
            'p10': self.p10,
            'p12': self.p12,
            'ug_cgpa': self.ug_cgpa,
            'age': self.age
        }
