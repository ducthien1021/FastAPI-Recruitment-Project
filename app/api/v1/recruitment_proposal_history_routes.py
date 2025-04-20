from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.recruitment_proposal_history import RecruitmentProposalHistory
from app.utils import helpers
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter()

# Lấy tất cả lịch sử đề xuất tuyển dụng
@router.get("/recruitment_proposal_history")
def get_all_proposal_histories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        histories = db.query(RecruitmentProposalHistory).all()
        return helpers.response(data=histories, message="Lấy tất cả lịch sử đề xuất tuyển dụng thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")

# Lấy lịch sử theo recruitment_proposal_id
@router.get("/recruitment_proposal_history/{recruitment_proposal_id}")
def get_history_by_proposal_id(recruitment_proposal_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        histories = db.query(RecruitmentProposalHistory).filter(
            RecruitmentProposalHistory.recruitment_proposal_id == recruitment_proposal_id
        ).order_by(RecruitmentProposalHistory.change_at.desc()).all()

        if not histories:
            return helpers.response(data=[], message="Không có lịch sử nào cho đề xuất này", code="G604", status="Warning")

        return helpers.response(data=histories, message="Lấy lịch sử đề xuất thành công")
    except Exception as e:
        return helpers.response(data=None, message=f"Lỗi: {str(e)}", code="G600", status="Error")
