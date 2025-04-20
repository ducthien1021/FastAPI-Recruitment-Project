from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.utils.auth import create_access_token
from app.utils import helpers
from pydantic import BaseModel
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Xử lý đăng nhập, tạo và trả về JWT token
    """
    # Tìm người dùng trong cơ sở dữ liệu
    user = db.query(User).filter(User.username == form_data.username).first()

    # Kiểm tra nếu không tìm thấy user hoặc mật khẩu sai
    if not user or not helpers.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Tạo JWT token với thông tin người dùng
    token = create_access_token({
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "fullname": user.fullname,
        "role_code": user.role_code
    })

    return {"access_token": token, "token_type": "bearer"} # Lưu ý phải trả đúng kiểu này cho framework

    
