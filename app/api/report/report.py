from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.token import verify_token, get_token_from_header
from api.chat import websocket
from models.auth import User
from models.report import Report
from models.chat import ChatMessage
from schemas.report import ReportCreate
from datetime import datetime

router = APIRouter()

@router.post("/report", tags=["Report"])
def report_user(report: ReportCreate, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    email = verify_token(token, db)
    reporter = db.query(User).filter(User.email == email).first()

    if reporter.id == report.reported_id:
        raise HTTPException(status_code=400, detail="자기 자신은 신고할 수 없습니다.")
    
    existing_report = db.query(Report).filter(Report.reporter_id == reporter.id, Report.reported_id == report.reported_id).first()

    if existing_report:
        raise HTTPException(status_code=400, detail="이미 신고한 사용자 입니다.")
    
    db.query(ChatMessage).filter(ChatMessage.match_id == report.match_id).update({"keep_log": True})
    
    new_report = Report(
        reporter_id = reporter.id,
        reported_id = report.reported_id,
        reason = report.reason,
        created_at = datetime.utcnow()
    )

    db.add(new_report)
    db.commit()

    if hasattr(websocket, 'deletion_tasks'):
        if report.match_id in websocket.deletion_tasks:
            websocket.deletion_tasks[report.match_id].cancel()
            websocket.deletion_tasks.pop(report.match_id, None)

    return {"message": "신고가 접수되었습니다. 대화 기록은 보존됩니다."}