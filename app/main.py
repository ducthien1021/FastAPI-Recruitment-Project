from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.api.v1 import user_routes, auth_routes, job_routes, department_routes, recruitment_proposal_routes, recruitment_proposal_history_routes, candidates_routes

app = FastAPI()
app.include_router(user_routes.router, prefix="/v1", tags=["Users"])
app.include_router(auth_routes.router, prefix="/v1", tags=["Auth"])
app.include_router(job_routes.router, prefix="/v1", tags=["Job"])
app.include_router(department_routes.router, prefix="/v1", tags=["Department"])
app.include_router(recruitment_proposal_routes.router, prefix="/v1", tags=["Recruitment Proposal"])
app.include_router(recruitment_proposal_history_routes.router, prefix="/v1", tags=["Recruitment Proposal History"])
app.include_router(candidates_routes.router, prefix="/v1", tags=["Candidates"])

# Mount thư mục chứa file upload
app.mount("/static", StaticFiles(directory="/uploads"), name="static")

# (Tùy chọn) Cho phép CORS nếu bạn cần
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health/db", tags=["Health"])
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Kết nối cơ sở dữ liệu thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Không thể kết nối cơ sở dữ liệu")