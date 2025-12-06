from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import qrcode
from io import BytesIO
import hashlib

import models
from database import engine, SessionLocal
from schemas import AttendanceCreate, AttendanceResponse

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Daily QR Attendance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Generate deterministic daily code: "ATTEND-YYYY-MM-DD"
def get_today_code() -> str:
    today = date.today().isoformat()
    return f"ATTEND-{today}"

# Optional: Add secret salt for extra security
# def get_today_code() -> str:
#     today = date.today().isoformat()
#     secret = "my-school-secret-2025"
#     return hashlib.sha256(f"{today}{secret}".encode()).hexdigest()[:12].upper()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    today_code = get_today_code()
    return templates.TemplateResponse("home.html", {
        "request": request,
        "today_code": today_code,
        "date": date.today().strftime("%A, %B %d, %Y")
    })

# Today's QR Code (big & beautiful for projector)
@app.get("/today-qr", response_class=HTMLResponse)
def today_qr_page(request: Request):
    code = get_today_code()
    return templates.TemplateResponse("today_qr.html", {
        "request": request,
        "code": code,
        "date": date.today().strftime("%d %B %Y"),
        "day": date.today().strftime("%A")
    })

# API: Get today's code as JSON (for Android app if needed)
@app.get("/api/today-code")
def api_today_code():
    return {"code": get_today_code(), "date": date.today().isoformat()}

# Raw QR Image
@app.get("/qr-image")
def get_qr_image():
    code = get_today_code()
    qr = qrcode.QRCode(version=1, box_size=20, border=4)
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")

# MARK ATTENDANCE – Now checks daily code + one per day per student
@app.post("/attendance", response_model=AttendanceResponse)
def mark_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    scanned_code = payload.student_id.strip()  # We reuse student_id field for QR content
    today_code = get_today_code()

    if scanned_code != today_code:
        raise HTTPException(status_code=400, detail="Invalid or expired QR code")

    # Find student by actual student_id (you can pass it separately or embed in app)
    # For now, we'll assume you send real student_id in a new field
    # Let's fix the schema – we'll accept both

    raise HTTPException(status_code=400, detail="Use new /attendance2 endpoint")

# NEW BETTER ENDPOINT
class AttendanceDaily(BaseModel):
    student_id: str      # real student ID like STD001
    qr_code: str         # the scanned daily code

@app.post("/attendance2", response_model=AttendanceResponse)
def mark_attendance_daily(payload: AttendanceDaily, db: Session = Depends(get_db)):
    if payload.qr_code != get_today_code():
        raise HTTPException(status_code=400, detail="QR code is expired or invalid")

    student = db.query(models.Student).filter(models.Student.student_id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check if already attended today
    today_start = datetime.combine(date.today(), datetime.min.time())
    already = db.query(models.Attendance).filter(
        models.Attendance.student_id == payload.student_id,
        models.Attendance.timestamp >= today_start
    ).first()

    if already:
        raise HTTPException(status_code=400, detail="Already marked attendance today")

    attendance = models.Attendance(student_id=payload.student_id)
    db.add(attendance)
    db.commit()

    return AttendanceResponse(
        message="Attendance marked successfully!",
        student_name=student.name,
        timestamp=attendance.timestamp
    )