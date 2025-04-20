from sqlalchemy import Column, String, Date, ForeignKey
from app.db.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(String(36), primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    gender = Column(String(10))
    date_of_birth = Column(Date)
    recruitment_proposal_id = Column(String(36), nullable=False)
    cv_file = Column(String(255))
