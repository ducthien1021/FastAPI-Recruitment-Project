# app/models/recruitment_proposal_model.py
from sqlalchemy import Column, String, Date, Integer, Text, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import date

class RecruitmentProposal(Base):
    __tablename__ = "recruitment_proposal"

    recruitment_proposal_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    desc = Column(Text, nullable=True)
    skills = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False)
    start_date = Column(Date, default=date.today)
    end_date = Column(Date, nullable=True)
    location = Column(String(255), nullable=True)
    status = Column(String(50), default='pending')
    job_id = Column(String(36), nullable=False)
    job_type = Column(String(255), nullable=True)
    department_id = Column(String(36), nullable=False)
    salary_start = Column(Float, nullable=False)
    salary_end = Column(Float, nullable=False)
    benefits = Column(Text, nullable=True)
    user_id = Column(Text, nullable=True)

