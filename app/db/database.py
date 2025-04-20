from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Cập nhật URL kết nối MySQL
DATABASE_URL = "sqlite:///./fast_api.db" 

# Tạo engine và session cho MySQL
engine = create_engine(DATABASE_URL, echo=True)  # echo=True sẽ log các câu lệnh SQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Hàm lấy session DB
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
