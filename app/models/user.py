from sqlalchemy import Column, String, Integer, TIMESTAMP, CHAR
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    # Cột user_id: GUID
    user_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)

    # Cột username
    username = Column(String(100), unique=True, nullable=False)

    # Cột password
    password = Column(String(255), nullable=False)

    # Cột email
    email = Column(String(255), unique=True, nullable=False)

    # Cột fullname
    fullname = Column(String(255))

    # Cột role_code
    role_code = Column(String(50), nullable=False, default="HR")

    # Cột created_at: Thời gian tạo
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
