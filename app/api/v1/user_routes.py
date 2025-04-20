from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, load_only, defer
from app.db.database import get_db
from app.models.user import User
from app.utils import helpers
from pydantic import BaseModel
from sqlalchemy import text
from typing import List, Optional
import uuid
from app.utils.auth import get_current_user

# Định nghĩa schema Pydantic
class UserModel(BaseModel):
    username: str
    email: str
    password: str
    fullname: Optional[str] = None
    role_code: Optional[str] = "user"
    

# Tạo router FastAPI
router = APIRouter()

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        users = db.query(User).all()
        users_dict = [{**user.__dict__, "password": None} for user in users] 
        return helpers.response(data=users_dict, message="Lấy danh sách user thành công")
    except Exception  as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

@router.post("/users")
def create_user(user: UserModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            return helpers.response(
                data=None,
                message="Username đã tồn tại",
                code="C603",
                status="Error"
            )

        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            return helpers.response(
                data=None,
                message="Email đã tồn tại",
                code="C603",
                status="Error"
            )

        new_user = User(
            user_id=str(uuid.uuid4()),
            username=user.username,
            password=helpers.hash_password(user.password),  
            email=user.email,
            fullname=user.fullname,
            role_code=user.role_code
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return helpers.response(data={"id": new_user.user_id}, message="Tạo user thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

@router.get("/users/{user_id}")
def get_user_by_id(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return helpers.response(
                data=None,
                message="Bản ghi không tồn tại!",
                code="G604",
                status="Error"
            )
        user.password = None
        return helpers.response(
            data=user,
            message="Lấy thông tin user thành công"
        )
    except Exception as e:
        return helpers.response(
            data=None,
            message=f"Lỗi: {str(e)}",
            code="G600",
            status="Error"
        )

@router.put("/users/{user_id}")
def update_user(user_id: str, user_update: UserModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return helpers.response(data=None, message=f"Bản ghi không tồn tại!", code="G604", status="Error")

        # Kiểm tra username đã tồn tại ở user khác chưa
        if user_update.username:
            existing = db.query(User).filter(
                User.username == user_update.username,
                User.user_id != user_id
            ).first()
            if existing:
                return helpers.response(
                    data=None,
                    message="Username đã tồn tại",
                    code="C603",
                    status="Error"
                )

        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = helpers.hash_password(update_data["password"])

        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        return helpers.response(data={"id": user_id}, message="Thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return helpers.response(data=None, message=f"Bản ghi không tồn tại!", code="G604", status="Error")

    try:
        db.delete(user)
        db.commit()
        return helpers.response(data={"id": user_id}, message="Thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")
