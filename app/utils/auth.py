from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.utils import helpers

SECRET_KEY = "your-secret-key__12345678@ABC_NDTHIEN"  
ALGORITHM = "HS256"  # Thuật toán mã hóa
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24  # Thời gian hết hạn của token 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/login")  # Dùng để lấy token trong header

# Hàm tạo token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})  # Đặt thời gian hết hạn vào payload
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Hàm kiểm tra và giải mã JWT
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Payload chứa thông tin user (vd: user_id)
    except JWTError:
        return None

# Hàm để lấy user từ token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            message="Not authenticated"
        )
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            message="Not authenticated"
        )
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            message="Not authenticated"
        )
    return user
