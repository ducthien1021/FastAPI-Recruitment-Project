from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid 
from app.db.database import get_db
from app.models.department import Department
from app.utils import helpers
from app.models.user import User
from typing import List, Optional
from pydantic import BaseModel
from app.utils.auth import get_current_user

# Định nghĩa schema Pydantic
class DepartmentModel(BaseModel):
    name: str
    code: str
    desc: Optional[str] = None


router = APIRouter()

# Create Department
@router.post("/department")
def create_department(department: DepartmentModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Kiểm tra code đã tồn tại
        existing = db.query(Department).filter(Department.code == department.code).first()
        if existing:
            return helpers.response(data=None, message="Code phòng ban đã tồn tại", code="C603", status="Error")
        
        new_department = Department(department_id=str(uuid.uuid4()), **department.dict())
        db.add(new_department)
        db.commit()
        return helpers.response(data={"id": new_department.department_id}, message="Tạo phòng ban thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Get All Departments
@router.get("/department")
def get_all_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        departments = db.query(Department).all()
        return helpers.response(data=departments, message="Thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Get Department by ID
@router.get("/department/{department_id}")
def get_department_by_id(department_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        department = db.query(Department).filter(Department.department_id == department_id).first()
        if not department:
            return helpers.response(data=None, message="Bản ghi không tồn tại", code="G604", status="Error")
        return helpers.response(data=department, message="Lấy phòng ban thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Update Department
@router.put("/department/{department_id}")
def update_department(department_id: str, update: DepartmentModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        department = db.query(Department).filter(Department.department_id == department_id).first()
        if not department:
            return helpers.response(data=None, message="Bản ghi không tồn tại!", code="G604", status="Error")
        
        # Kiểm tra code đã tồn tại?
        if update.code:
            existing = db.query(Department).filter(
                Department.code == update.code,
                Department.department_id != department_id
            ).first()
            if existing:
                return helpers.response(data=None, message="Code phòng ban đã tồn tại", code="C603", status="Error")
        
        for field, value in update.dict(exclude_unset=True).items():
            setattr(department, field, value)
        
        db.commit()
        return helpers.response(data=department, message="Cập nhật phòng ban thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Delete Department
@router.delete("/department/{department_id}")
def delete_department(department_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        department = db.query(Department).filter(Department.department_id == department_id).first()
        if not department:
            return helpers.response(data=None, message="Bản ghi không tồn tại!", code="G604", status="Error")
        
        db.delete(department)
        db.commit()
        return helpers.response(data={"id": department_id}, message="Xóa phòng ban thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Delete Multiple Departments
@router.delete("/department")
def delete_departments(department_ids: list[str], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if not department_ids:
            return helpers.response(data=None, message="Danh sách department_id không hợp lệ!", code="G604", status="Error")
        
        departments_to_delete = db.query(Department).filter(Department.department_id.in_(department_ids)).all()
        
        if not departments_to_delete:
            return helpers.response(data=None, message="Không tìm thấy phòng ban nào trong danh sách!", code="G604", status="Error")
        
        for department in departments_to_delete:
            db.delete(department)

        db.commit()
        return helpers.response(data={"deleted_department_ids": department_ids}, message="Xóa các phòng ban thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")
