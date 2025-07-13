from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import Optional, List

# ---------- USER SCHEMAS ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


# ---------- VITALS SCHEMAS ----------

class VitalsCreate(BaseModel):
    heart_rate: int
    bp_systolic: int
    bp_diastolic: int
    oxygen: int
    temperature: int
    sugar: int
    symptoms: str

class VitalsOut(VitalsCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


# ---------- APPOINTMENT SCHEMAS ----------

class AppointmentCreate(BaseModel):
    reason: str
    notes: Optional[str] = None
    preferred_date: Optional[date] = None
    preferred_time: Optional[time] = None

class AppointmentOut(BaseModel):
    id: int
    reason: str
    notes: Optional[str] = None
    doctor_name: str
    preferred_date: Optional[date] = None
    preferred_time: Optional[time] = None
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    preferred_date: date
    preferred_time: time