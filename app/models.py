# app/models.py

from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ✅ USER
class User(Document):
    name: str
    email: EmailStr
    password: str
    role: str = "patient"

    class Settings:
        name = "users"  # MongoDB collection name

# ✅ VITALS
class Vitals(Document):
    user_id: str  # Reference to User._id as string
    heart_rate: int
    bp_systolic: int
    bp_diastolic: int
    oxygen: int
    temperature: float
    sugar: int
    symptoms: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "vitals"

# ✅ APPOINTMENT
class Appointment(Document):
    user_id: str
    reason: str
    notes: Optional[str]
    doctor_name: str = "Dr. Auto Assign"
    status: str = "pending"
    preferred_date: Optional[datetime]
    preferred_time: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime]

    class Settings:
        name = "appointments"

# ✅ DOCTOR
class Doctor(Document):
    name: str
    specialization: str
    is_available: bool = True

    class Settings:
        name = "doctors"
