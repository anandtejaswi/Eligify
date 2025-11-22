"""Repository for managing exam data."""
from typing import List
from models.exam import Exam


class ExamRepository:
    """Repository for exam data management."""
    
    # Mock exam database - in production, this would connect to a real database
    MOCK_EXAMS = [
        Exam(
            exam_id=101, exam_name='JEE Main (Engineering)', conducting_body='NTA',
            exam_level='National', exam_mode='Online', website='jeemain.nta.nic.in',
            fee_gen_ews=1000, total_duration_mins=180,
            min_age=17, max_age=25, min_10_percent=60, min_12_percent=75, min_ug_cgpa=0.0,
            subjects=['Physics', 'Chemistry', 'Mathematics'],
            documents=['Caste Certificate', 'Domicile', 'Photo', 'Signature', 'Aadhar']
        ),
        Exam(
            exam_id=102, exam_name='NEET UG (Medical)', conducting_body='NTA',
            exam_level='National', exam_mode='Offline', website='neet.nta.nic.in',
            fee_gen_ews=1500, total_duration_mins=200,
            min_age=17, max_age=99, min_10_percent=50, min_12_percent=60, min_ug_cgpa=0.0,
            subjects=['Physics', 'Chemistry', 'Botany', 'Zoology'],
            documents=['Caste Certificate', 'Domicile', 'Birth Certificate', 'Photo', 'Signature', 'Aadhar']
        ),
        Exam(
            exam_id=103, exam_name='UPSC CSE (Civil Services)', conducting_body='UPSC',
            exam_level='National', exam_mode='Offline', website='upsc.gov.in',
            fee_gen_ews=100, total_duration_mins=180,
            min_age=21, max_age=32, min_10_percent=50, min_12_percent=50, min_ug_cgpa=6.0,
            subjects=['General Studies I', 'General Studies II (CSAT)'],
            documents=['Caste Certificate', 'Photo', 'Signature', 'Aadhar', 'UG Degree']
        ),
        Exam(
            exam_id=104, exam_name='GATE (Engineering PG)', conducting_body='IITs/IISc',
            exam_level='National', exam_mode='Online', website='gate.iitk.ac.in',
            fee_gen_ews=1800, total_duration_mins=180,
            min_age=20, max_age=99, min_10_percent=50, min_12_percent=50, min_ug_cgpa=6.5,
            subjects=['General Aptitude', 'Engineering Mathematics', 'Core Engineering Branch Subject'],
            documents=['UG Degree/Marksheet', 'Photo', 'Signature', 'Aadhar']
        ),
        Exam(
            exam_id=105, exam_name='CLAT (Law Entrance)', conducting_body='Consortium of NLUs',
            exam_level='National', exam_mode='Offline', website='consortiumofnlus.ac.in',
            fee_gen_ews=4000, total_duration_mins=120,
            min_age=17, max_age=99, min_10_percent=50, min_12_percent=45, min_ug_cgpa=0.0,
            subjects=['English Language', 'Current Affairs', 'Legal Reasoning', 'Logical Reasoning'],
            documents=['12th Marksheet', 'Caste Certificate', 'Photo', 'Signature']
        ),
        Exam(
            exam_id=106, exam_name='BITSAT (Engineering)', conducting_body='BITS Pilani',
            exam_level='National', exam_mode='Online', website='bitsadmission.com',
            fee_gen_ews=3400, total_duration_mins=180,
            min_age=17, max_age=99, min_10_percent=60, min_12_percent=75, min_ug_cgpa=0.0,
            subjects=['PCM/PCB', 'English Proficiency', 'Logical Reasoning'],
            documents=['12th Marksheet', 'Photo', 'Signature']
        ),
        Exam(
            exam_id=107, exam_name='UGEE (IIIT Hyderabad)', conducting_body='IIIT Hyderabad',
            exam_level='National', exam_mode='Online', website='iiit.ac.in/admissions/ug',
            fee_gen_ews=2500, total_duration_mins=180,
            min_age=17, max_age=99, min_10_percent=60, min_12_percent=60, min_ug_cgpa=0.0,
            subjects=['Subject Proficiency Test', 'Research Aptitude Test'],
            documents=['12th Marksheet', 'Domicile', 'Photo']
        ),
        Exam(
            exam_id=108, exam_name='MHT CET (Engineering/Pharmacy)', conducting_body='CET Cell Maharashtra',
            exam_level='State', exam_mode='Online', website='mahacet.org',
            fee_gen_ews=800, total_duration_mins=180,
            min_age=17, max_age=99, min_10_percent=50, min_12_percent=45, min_ug_cgpa=0.0,
            subjects=['Physics', 'Chemistry', 'Mathematics/Biology'],
            documents=['Domicile', 'Caste Certificate', 'Photo']
        ),
        Exam(
            exam_id=109, exam_name='CUET-UG (Common Univ. Entrance)', conducting_body='NTA',
            exam_level='National', exam_mode='Online', website='nta.ac.in/cuet',
            fee_gen_ews=750, total_duration_mins=180,
            min_age=17, max_age=99, min_10_percent=50, min_12_percent=50, min_ug_cgpa=0.0,
            subjects=['Language', 'Domain Subjects', 'General Test'],
            documents=['12th Marksheet', 'Photo', 'Signature']
        ),
        Exam(
            exam_id=110, exam_name='NDA (National Defence Academy)', conducting_body='UPSC',
            exam_level='National', exam_mode='Offline', website='upsc.gov.in/nda',
            fee_gen_ews=100, total_duration_mins=300,
            min_age=16, max_age=19, min_10_percent=50, min_12_percent=60, min_ug_cgpa=0.0,
            subjects=['Mathematics', 'General Ability Test (GAT)'],
            documents=['Birth Certificate', 'Photo', 'Aadhar']
        ),
        Exam(
            exam_id=111, exam_name='IAT (IISER Aptitude Test)', conducting_body='IISERs',
            exam_level='National', exam_mode='Online', website='iiseradmission.in',
            fee_gen_ews=2000, total_duration_mins=180,
            min_age=17, max_age=99, min_10_percent=60, min_12_percent=60, min_ug_cgpa=0.0,
            subjects=['Physics', 'Chemistry', 'Biology', 'Mathematics'],
            documents=['12th Marksheet', 'Photo', 'Aadhar']
        ),
        Exam(
            exam_id=112, exam_name='ISI Entrance (Maths/Stats)', conducting_body='Indian Statistical Institute',
            exam_level='National', exam_mode='Offline', website='isical.ac.in',
            fee_gen_ews=1500, total_duration_mins=120,
            min_age=17, max_age=99, min_10_percent=70, min_12_percent=75, min_ug_cgpa=0.0,
            subjects=['Mathematics', 'Statistics', 'English'],
            documents=['12th Marksheet', 'Photo']
        ),
        Exam(
            exam_id=113, exam_name='UCEED (Design Entrance)', conducting_body='IIT Bombay',
            exam_level='National', exam_mode='Online/Offline', website='uceed.iitb.ac.in',
            fee_gen_ews=3500, total_duration_mins=180,
            min_age=17, max_age=99, min_10_percent=50, min_12_percent=50, min_ug_cgpa=0.0,
            subjects=['Aptitude', 'Observation', 'Design Sketching'],
            documents=['12th Marksheet', 'Photo', 'Signature']
        ),
        Exam(
            exam_id=114, exam_name='AFCAT (Air Force Common Aptitude)', conducting_body='IAF',
            exam_level='National', exam_mode='Online', website='afcat.cdac.in',
            fee_gen_ews=250, total_duration_mins=120,
            min_age=20, max_age=24, min_10_percent=50, min_12_percent=50, min_ug_cgpa=6.0,
            subjects=['General Awareness', 'Verbal Ability', 'Numerical Ability', 'Reasoning'],
            documents=['UG Degree', 'Photo', 'Aadhar']
        ),
        Exam(
            exam_id=115, exam_name='CDS (Combined Defence Services)', conducting_body='UPSC',
            exam_level='National', exam_mode='Offline', website='upsc.gov.in/cds',
            fee_gen_ews=200, total_duration_mins=360,
            min_age=19, max_age=24, min_10_percent=50, min_12_percent=50, min_ug_cgpa=6.0,
            subjects=['English', 'General Knowledge', 'Elementary Mathematics'],
            documents=['UG Degree', 'Photo', 'Aadhar']
        ),
        Exam(
            exam_id=116, exam_name='NEET-PG (Medical PG)', conducting_body='NBE',
            exam_level='National', exam_mode='Online', website='nbe.edu.in',
            fee_gen_ews=5000, total_duration_mins=210,
            min_age=22, max_age=99, min_10_percent=50, min_12_percent=50, min_ug_cgpa=7.0,
            subjects=['Clinical Subjects', 'Pre/Para-Clinical Subjects'],
            documents=['MBBS Degree', 'Caste Certificate', 'Photo']
        ),
        Exam(
            exam_id=117, exam_name='CUET-PG (Common Univ. Entrance PG)', conducting_body='NTA',
            exam_level='National', exam_mode='Online', website='nta.ac.in/cuetpg',
            fee_gen_ews=800, total_duration_mins=105,
            min_age=20, max_age=99, min_10_percent=50, min_12_percent=50, min_ug_cgpa=5.5,
            subjects=['General Section', 'Domain Specific Knowledge'],
            documents=['UG Degree/Marksheet', 'Photo', 'Signature']
        ),
        Exam(
            exam_id=118, exam_name='SSC-CGL (Govt. Job)', conducting_body='SSC',
            exam_level='National', exam_mode='Online', website='ssc.nic.in',
            fee_gen_ews=100, total_duration_mins=120,
            min_age=18, max_age=32, min_10_percent=50, min_12_percent=50, min_ug_cgpa=5.0,
            subjects=['Quantitative Aptitude', 'General Intelligence', 'English Comprehension'],
            documents=['UG Degree', 'Photo', 'Aadhar']
        ),
        Exam(
            exam_id=119, exam_name='VITEEE (Engineering)', conducting_body='VIT',
            exam_level='University', exam_mode='Online', website='viteee.vit.ac.in',
            fee_gen_ews=1350, total_duration_mins=150,
            min_age=17, max_age=99, min_10_percent=60, min_12_percent=60, min_ug_cgpa=0.0,
            subjects=['PCM/PCB', 'English', 'Aptitude'],
            documents=['12th Marksheet', 'Photo', 'Signature']
        ),
        Exam(
            exam_id=120, exam_name='SRMJEE (Engineering)', conducting_body='SRM Institute',
            exam_level='University', exam_mode='Online', website='srmist.edu.in',
            fee_gen_ews=1200, total_duration_mins=150,
            min_age=17, max_age=99, min_10_percent=50, min_12_percent=50, min_ug_cgpa=0.0,
            subjects=['Physics', 'Chemistry', 'Mathematics/Biology'],
            documents=['12th Marksheet', 'Photo']
        ),
    ]
    
    @classmethod
    def get_all_exams(cls) -> List[Exam]:
        """Get all exams from the repository."""
        return cls.MOCK_EXAMS.copy()
    
    @classmethod
    def get_exam_by_id(cls, exam_id: int) -> Exam:
        """Get an exam by ID."""
        for exam in cls.MOCK_EXAMS:
            if exam.exam_id == exam_id:
                return exam
        raise ValueError(f"Exam with ID {exam_id} not found")

