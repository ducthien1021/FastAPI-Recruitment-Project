from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from pydantic import BaseModel
from app.models.job import Job
from app.db.database import get_db
from app.utils import helpers
from typing import List, Optional
from app.utils.auth import get_current_user
from app.models.user import User

# Định nghĩa schema Pydantic
class JobModel(BaseModel):
    name: str
    code: str
    desc: Optional[str] = None

router = APIRouter()

@router.post("/job")
def create_job(job: JobModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Kiểm tra code đã tồn tại?
        if job.code:
            existing = db.query(Job).filter(
                Job.code == job.code
            ).first()
            if existing:
                return helpers.response(
                    data=None,
                    message="Code đã tồn tại",
                    code="C603",
                    status="Error"
                )

        new_job = Job(job_id=str(uuid.uuid4()), **job.dict())
        db.add(new_job)
        db.commit()
        return helpers.response(data={"id": new_job.job_id}, message="Tạo thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

@router.get("/job")
def get_all_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        jobs = db.query(Job).all()
        return helpers.response(data=jobs, message="Thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

@router.get("/job/{job_id}")
def get_job_by_id(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Truy vấn tìm job theo job_id
        job = db.query(Job).filter(Job.job_id == job_id).first()
        
        # Nếu không tìm thấy job, trả về lỗi
        if not job:
            return helpers.response(
                data=None,
                message="Bản ghi không tồn tại!",
                code="G604",
                status="Error"
            )

        # Trả về thông tin Job
        return helpers.response(data=job, message="Lấy thông tin job thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")


@router.put("/job/{job_id}")
def update_job(job_id: str, update: JobModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return helpers.response(
                    data=None,
                    message="Bản ghi không tồn tại!",
                    code="G604",
                    status="Error"
                )

        # Kiểm tra code đã tồn tại?
        if update.code:
            existing = db.query(Job).filter(
                Job.code == update.code,
                Job.job_id != job_id
            ).first()
            if existing:
                return helpers.response(
                    data=None,
                    message="Code đã tồn tại",
                    code="C603",
                    status="Error"
                )

        for field, value in update.dict(exclude_unset=True).items():
            setattr(job, field, value)
        db.commit()
        return helpers.response(data={"id": job_id}, message="Cập nhật thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

@router.delete("/job/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        return helpers.response(
                data=None,
                message="Bản ghi không tồn tại!",
                code="G604",
                status="Error"
            )

    try:
        db.delete(job)
        db.commit()
        return helpers.response(data={"id": job_id}, message="Xóa thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")


@router.delete("/job")
def delete_jobs(job_ids: list[str], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Kiểm tra xem có job nào trong danh sách không
        if not job_ids:
            return helpers.response(
                data=None,
                message="Danh sách job_id không hợp lệ!",
                code="G604",
                status="Error"
            )

        # Truy vấn các job có trong danh sách job_ids
        jobs_to_delete = db.query(Job).filter(Job.job_id.in_(job_ids)).all()
        
        # Kiểm tra nếu không tìm thấy job nào trong danh sách
        if not jobs_to_delete:
            return helpers.response(
                data=None,
                message="Không tìm thấy job nào trong danh sách!",
                code="G604",
                status="Error"
            )

        # Xóa các job tìm được
        for job in jobs_to_delete:
            db.delete(job)

        # Commit thay đổi vào cơ sở dữ liệu
        db.commit()

        return helpers.response(
            data={"deleted_job_ids": job_ids},
            message="Xóa các job thành công"
        )
    
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

