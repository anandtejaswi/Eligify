from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Date, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    sub = Column(String(64), primary_key=True)
    email = Column(String(120), nullable=False, unique=True)
    name = Column(String(120))
    picture = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CandidateProfile(Base):
    __tablename__ = 'candidate_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_sub = Column(String(64), ForeignKey('users.sub'), nullable=False)
    first_name = Column(String(120), nullable=False)
    dob = Column(Date, nullable=False)
    category = Column(String(20), nullable=False)
    p10 = Column(Float, nullable=False)
    p12 = Column(Float, nullable=False)
    ug_cgpa = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentUpload(Base):
    __tablename__ = 'document_uploads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_sub = Column(String(64), ForeignKey('users.sub'), nullable=False)
    doc_type = Column(String(20), nullable=False)
    filename = Column(String(255))
    mime = Column(String(64))
    stored_path = Column(String(255))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class ParsedDocument(Base):
    __tablename__ = 'parsed_documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_id = Column(Integer, ForeignKey('document_uploads.id'), nullable=False)
    parsed_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Exam(Base):
    __tablename__ = 'exams'
    exam_id = Column(Integer, primary_key=True)
    exam_name = Column(String(200), nullable=False)
    conducting_body = Column(String(120), nullable=False)
    exam_level = Column(String(50), nullable=False)
    exam_mode = Column(String(50), nullable=False)
    website = Column(String(120), nullable=False)
    fee_gen_ews = Column(Integer, nullable=False)
    total_duration_mins = Column(Integer, nullable=False)
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    min_10_percent = Column(Float, nullable=False)
    min_12_percent = Column(Float, nullable=False)
    min_ug_cgpa = Column(Float, nullable=False)

class ExamSubject(Base):
    __tablename__ = 'exam_subjects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey('exams.exam_id'), nullable=False)
    subject_name = Column(String(120), nullable=False)

class ExamDocument(Base):
    __tablename__ = 'exam_documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey('exams.exam_id'), nullable=False)
    document_name = Column(String(120), nullable=False)

class EligibilityCheck(Base):
    __tablename__ = 'eligibility_checks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidate_profiles.id'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exams.exam_id'), nullable=False)
    eligible = Column(Integer, nullable=False)
    run_at = Column(DateTime(timezone=True), server_default=func.now())
    inputs_snapshot = Column(Text)
    __table_args__ = (
        UniqueConstraint('candidate_id', 'exam_id', name='uq_candidate_exam_once'),
    )