from pydantic import BaseModel
from datetime import datetime

class AttendanceCreate(BaseModel):
    student_id: str

class AttendanceDaily(BaseModel):
    student_id: str      # real student ID like STD001
    qr_code: str         # the scanned daily code

class AttendanceResponse(BaseModel):
    message: str
    student_name: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True