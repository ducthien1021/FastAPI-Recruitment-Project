from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import date
import os

from app.models.candidates import Candidate
from app.db.database import get_db
from app.utils import helpers
from app.utils.auth import get_current_user
from app.models.user import User

UPLOAD_DIR = "uploads\cv"

# Pydantic Schema
class CandidateModel(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    recruitment_proposal_id: str

router = APIRouter()

# Create Candidate
@router.post("/candidate")
def create_candidate(    
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    recruitment_proposal_id: str = Form(...),
    cv_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        # Lưu file nếu có
        filename = None
        if cv_file:
            ext = os.path.splitext(cv_file.filename)[1]
            if ext.lower() != ".pdf":
                return helpers.response(
                    data=None,
                    message="Vui lòng chọn file PDF.",
                    code="G601",
                    status="Error"
                )

            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            with open(filepath, "wb") as buffer:
                buffer.write(cv_file.file.read())

        # Tạo ứng viên
        new_candidate = Candidate(
            candidate_id=str(uuid.uuid4()),
            full_name=full_name,
            email=email,
            phone=phone,
            gender=gender,
            date_of_birth=date_of_birth,
            recruitment_proposal_id=recruitment_proposal_id,
            cv_file=filename
        )
        db.add(new_candidate)
        db.commit()
        return helpers.response(data={"id": new_candidate.candidate_id}, message="Tạo ứng viên thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Get All Candidates
@router.get("/candidate")
def get_all_candidates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        candidates = db.query(Candidate).all()
        result = [
            {
                **candidate.__dict__,
                "cv_url": f"/static/cv/{candidate.cv_file}" if candidate.cv_file else None
            }
            for candidate in candidates
        ]

        return helpers.response(data=result, message="Thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

@router.get("/candidates/by-proposals")
def get_candidates_by_proposals(
    recruitment_proposal_ids: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        ids = recruitment_proposal_ids.split(',')
        candidates = db.query(Candidate).filter(Candidate.recruitment_proposal_id.in_(ids)).all()
        for c in candidates:
            if c.cv_file:
                c.cv_url = f"/static/cv/{c.cv_file}"

        return helpers.response(data=candidates, message="Thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Get Candidate by ID
@router.get("/candidate/{candidate_id}")
def get_candidate_by_id(candidate_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        if not candidate:
            return helpers.response(data=None, message="Bản ghi không tồn tại!", code="G604", status="Error")

        # Nếu có file CV thì tạo đường dẫn công khai
        if candidate.cv_file:
            candidate.cv_url = f"/static/cv/{candidate.cv_file}"

        return helpers.response(data=candidate, message="Lấy thông tin ứng viên thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Delete Candidate
@router.delete("/candidate/{candidate_id}")
def delete_candidate(candidate_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        return helpers.response(data=None, message="Bản ghi không tồn tại!", code="G604", status="Error")
    try:
        # Xoá file CV nếu tồn tại
        if candidate.cv_file:
            file_path = os.path.join(UPLOAD_DIR, candidate.cv_file)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.delete(candidate)
        db.commit()
        return helpers.response(data={"id": candidate_id}, message="Xóa thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Delete Multiple Candidates
@router.delete("/candidate")
def delete_candidates(candidate_ids: List[str], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if not candidate_ids:
            return helpers.response(data=None, message="Danh sách candidate_id không hợp lệ!", code="G604", status="Error")

        candidates_to_delete = db.query(Candidate).filter(Candidate.candidate_id.in_(candidate_ids)).all()
        if not candidates_to_delete:
            return helpers.response(data=None, message="Không tìm thấy ứng viên nào trong danh sách!", code="G604", status="Error")

        for candidate in candidates_to_delete:
            if candidate.cv_file:
                file_path = os.path.join(UPLOAD_DIR, candidate.cv_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.delete(candidate)

        db.commit()
        return helpers.response(data={"deleted_candidate_ids": candidate_ids}, message="Xóa các ứng viên thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")
