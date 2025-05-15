from pydantic import BaseModel

class ReportCreate(BaseModel):
    reported_id: int
    reason: str
    