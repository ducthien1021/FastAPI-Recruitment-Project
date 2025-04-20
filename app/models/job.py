from sqlalchemy import Column, String, Integer, TIMESTAMP, CHAR
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Job(Base):
    __tablename__ = "job"

    job_id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True)
    desc = Column(String(500))
