from pydantic import BaseModel
import uuid 
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi import Path, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.recruitment_proposal import RecruitmentProposal
from app.models.recruitment_proposal_history import RecruitmentProposalHistory
from app.utils import helpers
from app.models.user import User
from app.utils.auth import get_current_user
from datetime import date
from typing import Optional, Literal


class RecruitmentProposalBase(BaseModel):
    code: str
    title: str
    desc: Optional[str] = None
    skills: Optional[str] = None
    quantity: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None
    status: Optional[str] = "pending"
    job_id: str  
    job_type: Optional[str] = None
    department_id: str  
    salary_start: float
    salary_end: float
    benefits: Optional[str] = None
    user_id: Optional[str] = None

router = APIRouter()

# Create Recruitment Proposal
@router.post("/recruitment_proposal")
def create_recruitment_proposal(proposal: RecruitmentProposalBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Kiểm tra mã proposal đã tồn tại
        existing = db.query(RecruitmentProposal).filter(RecruitmentProposal.code == proposal.code).first()
        if existing:
            return helpers.response(data=None, message="Mã đề xuất đã tồn tại", code="C603", status="Error")
        
        new_proposal = RecruitmentProposal(recruitment_proposal_id=str(uuid.uuid4()), **proposal.dict())
        db.add(new_proposal)

        # Ghi vào bảng lịch sử
        history = RecruitmentProposalHistory(
            recruitment_proposal_id=new_proposal.recruitment_proposal_id,
            status=new_proposal.status 
        )
        db.add(history)

        db.commit()
        return helpers.response(data={"id": new_proposal.recruitment_proposal_id}, message="Tạo đề xuất tuyển dụng thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Get All Recruitment Proposals
@router.get("/recruitment_proposal")
def get_all_recruitment_proposals(
    status: Optional[Literal["approve", "pending", "reject", "done"]] = None, 
    user_ids: Optional[str] = Query(None, description="Danh sách user_id, phân cách bằng dấu ','"),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        query = db.query(RecruitmentProposal)
        
        if status:
            query = query.filter(RecruitmentProposal.status == status)

        if user_ids:
            id_list = user_ids.split(",")
            query = query.filter(RecruitmentProposal.user_id.in_(id_list))
        
        proposals = query.all()

        return helpers.response(data=proposals, message="Thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Get Recruitment Proposal by ID
@router.get("/recruitment_proposal/{recruitment_proposal_id}")
def get_recruitment_proposal_by_id(recruitment_proposal_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        proposal = db.query(RecruitmentProposal).filter(RecruitmentProposal.recruitment_proposal_id == recruitment_proposal_id).first()
        if not proposal:
            return helpers.response(data=None, message="Bản ghi không tồn tại", code="G604", status="Error")
        return helpers.response(data=proposal, message="Lấy thông tin đề xuất tuyển dụng thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Update Recruitment Proposal
@router.put("/recruitment_proposal/{recruitment_proposal_id}")
def update_recruitment_proposal(recruitment_proposal_id: str, update: RecruitmentProposalBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        proposal = db.query(RecruitmentProposal).filter(RecruitmentProposal.recruitment_proposal_id == recruitment_proposal_id).first()
        if not proposal:
            return helpers.response(data=None, message="Bản ghi không tồn tại", code="G604", status="Error")

        old_status = proposal.status
        new_status = update.status
        status_changed = new_status and new_status != old_status    
        if status_changed:
            history = RecruitmentProposalHistory(
                recruitment_proposal_id=recruitment_proposal_id,
                status=new_status
            )
            db.add(history)

        for field, value in update.dict(exclude_unset=True).items():
            setattr(proposal, field, value)
        
        db.commit()
        return helpers.response(data=proposal, message="Cập nhật đề xuất tuyển dụng thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Delete Recruitment Proposal
@router.delete("/recruitment_proposal/{recruitment_proposal_id}")
def delete_recruitment_proposal(recruitment_proposal_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        proposal = db.query(RecruitmentProposal).filter(RecruitmentProposal.recruitment_proposal_id == recruitment_proposal_id).first()
        if not proposal:
            return helpers.response(data=None, message="Bản ghi không tồn tại", code="G604", status="Error")

        db.delete(proposal)
        db.commit()
        return helpers.response(data={"id": recruitment_proposal_id}, message="Xóa đề xuất tuyển dụng thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Delete Multiple Recruitment Proposals
@router.delete("/recruitment_proposal")
def delete_recruitment_proposals(recruitment_proposal_ids: list[str], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if not recruitment_proposal_ids:
            return helpers.response(data=None, message="Danh sách ID không hợp lệ", code="G604", status="Error")
        
        proposals_to_delete = db.query(RecruitmentProposal).filter(RecruitmentProposal.recruitment_proposal_id.in_(recruitment_proposal_ids)).all()
        
        if not proposals_to_delete:
            return helpers.response(data=None, message="Không tìm thấy đề xuất nào trong danh sách", code="G604", status="Error")
        
        for proposal in proposals_to_delete:
            db.delete(proposal)

        db.commit()
        return helpers.response(data={"deleted_proposal_ids": recruitment_proposal_ids}, message="Xóa các đề xuất tuyển dụng thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")


@router.put("/recruitment_proposal/{recruitment_proposal_id}/status")
def change_status(
    recruitment_proposal_id: str = Path(..., description="ID của recruitment proposal"),
    status: str = Query(..., description="Trạng thái mới"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_status = {"approve", "pending", "reject", "done"}
    if status not in allowed_status:
        return helpers.response(
            data=None,
            message="Trạng thái không hợp lệ.",
            code="G605",
            status="Error"
        )

    try:
        proposal = db.query(RecruitmentProposal).filter(
            RecruitmentProposal.recruitment_proposal_id == recruitment_proposal_id
        ).first()

        if not proposal:
            return helpers.response(data=None, message="Proposal không tồn tại!", code="G604", status="Error")

        proposal.status = status
        db.commit()

        return helpers.response(data={"id": recruitment_proposal_id, "new_status": status}, message="Cập nhật trạng thái thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")