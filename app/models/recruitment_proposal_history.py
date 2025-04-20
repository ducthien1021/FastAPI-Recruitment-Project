from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class RecruitmentProposalHistory(Base):
    __tablename__ = "recruitment_proposal_history"

    recruitment_proposal_history_id = Column(Integer, primary_key=True, autoincrement=True)
    recruitment_proposal_id = Column(String(36), nullable=False)
    status = Column(String(100))
    change_at = Column(DateTime, default=func.now())
