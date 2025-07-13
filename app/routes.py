from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pydantic import BaseModel
import os
import random
from dotenv import load_dotenv
from jose import jwt, JWTError  # ✅ Fixed import
import json
import logging

# Load environment variables
load_dotenv(dotenv_path="./.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .schemas import (
    UserCreate, UserLogin, UserOut,
    VitalsCreate, VitalsOut,
    AppointmentCreate, AppointmentOut
)
from .models import User, Vitals, Appointment, Doctor
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .database import get_db
from .specialization_mapping import get_specialist_for_symptom
import openai

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

router = APIRouter()

class SymptomInput(BaseModel):
    symptoms: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to WebSocket")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {str(e)}")
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        for user_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to user {user_id}: {str(e)}")
                self.disconnect(user_id)

manager = ConnectionManager()

async def get_current_user_websocket(websocket: WebSocket):
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008)
            raise HTTPException(status_code=401, detail="Missing token")

        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            await websocket.close(code=1008)
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"id": user_id, "email": payload.get("email")}
    except JWTError:  # ✅ Fixed error handling
        await websocket.close(code=1008)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        await websocket.close(code=1011)
        raise HTTPException(status_code=500, detail=str(e))

async def get_ai_response(symptoms: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful and friendly medical assistant. "
                        "Provide:\n"
                        "1. Possible non-emergency explanations\n"
                        "2. Self-care recommendations if appropriate\n"
                        "3. When to consult a doctor\n"
                        "4. Red flags to watch for\n\n"
                        "Guidelines:\n"
                        "- Do not diagnose\n"
                        "- Be concise (under 200 words)\n"
                        "- Use simple language\n"
                        "- Show empathy and care"
                    )
                },
                {
                    "role": "user",
                    "content": f"I am experiencing: {symptoms}"
                }
            ],
            temperature=0.6,
            max_tokens=250
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logger.error(f"OpenRouter API Error: {str(e)}")
        raise HTTPException(status_code=503, detail="AI service unavailable.")

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed, role="patient")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(db_user.id),
        "email": db_user.email,
    })
    return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh-token", response_model=TokenRefreshResponse)
async def refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_token = create_access_token({
        "sub": str(db_user.id),
        "email": db_user.email,
        "role": db_user.role
    })
    return {"access_token": new_token, "token_type": "bearer"}

@router.post("/vitals", response_model=VitalsOut)
async def submit_vitals(data: VitalsCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vitals = Vitals(
        user_id=current_user.id,
        heart_rate=data.heart_rate,
        bp_systolic=data.bp_systolic,
        bp_diastolic=data.bp_diastolic,
        oxygen=data.oxygen,
        temperature=data.temperature,
        sugar=data.sugar,
        symptoms=data.symptoms,
        timestamp=datetime.utcnow()
    )
    db.add(vitals)
    db.commit()
    db.refresh(vitals)
    await manager.send_personal_message(
        json.dumps({
            "event": "new_vitals",
            "data": {
                "id": vitals.id,
                "timestamp": vitals.timestamp.isoformat(),
                "heart_rate": vitals.heart_rate,
                "status": "success"
            }
        }),
        str(current_user.id)
    )
    return vitals

@router.get("/vitals", response_model=List[VitalsOut])
def get_vitals(days: Optional[int] = Query(None, ge=1), limit: Optional[int] = Query(None, ge=1, le=1000), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Vitals).filter(Vitals.user_id == current_user.id)
    if days:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Vitals.timestamp >= since)
    query = query.order_by(Vitals.timestamp.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

@router.post("/analyze-symptoms")
async def analyze_symptoms(payload: SymptomInput, current_user: User = Depends(get_current_user)):
    advice = await get_ai_response(payload.symptoms)
    return {"analysis": advice}

@router.post("/appointments", response_model=AppointmentOut)
async def book_appointment(payload: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    specialization = get_specialist_for_symptom(payload.reason)
    doctor = db.query(Doctor).filter_by(specialization=specialization, is_available=True).first()
    doctor_name = doctor.name if doctor else "Dr. Auto Assign"

    appointment = Appointment(
        user_id=current_user.id,
        reason=payload.reason,
        notes=payload.notes,
        doctor_name=doctor_name,
        preferred_date=payload.preferred_date,
        preferred_time=payload.preferred_time,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    await manager.broadcast({
        "event": "new_appointment",
        "data": {
            "id": appointment.id,
            "user_id": current_user.id,
            "status": appointment.status,
            "timestamp": appointment.created_at.isoformat()
        }
    })
    return appointment

@router.get("/appointments", response_model=List[AppointmentOut])
def get_user_appointments(status: Optional[str] = Query(None), upcoming: Optional[bool] = Query(None), doctor: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Appointment).filter(Appointment.user_id == current_user.id)
    if status:
        query = query.filter(Appointment.status.ilike(status))
    if doctor:
        query = query.filter(Appointment.doctor_name.ilike(f"%{doctor}%"))
    if upcoming:
        now = datetime.utcnow()
        query = query.filter((Appointment.preferred_date > now.date()) |
                             ((Appointment.preferred_date == now.date()) & (Appointment.preferred_time > now.time())))
    return query.order_by(Appointment.created_at.desc()).all()

@router.websocket("/ws/vitals")
async def websocket_vitals(websocket: WebSocket):
    try:
        user = await get_current_user_websocket(websocket)
        await manager.connect(websocket, user["id"])
        logger.info(f"WebSocket connected for user {user['email']}")
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                manager.disconnect(user["id"])
                logger.info(f"WebSocket disconnected for user {user['email']}")
                break
            except Exception as e:
                manager.disconnect(user["id"])
                logger.error(f"WebSocket error for user {user['email']}: {str(e)}")
                await websocket.close()
                break
    except HTTPException as e:
        logger.error(f"WebSocket auth failed: {e.detail}")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {str(e)}")
        await websocket.close(code=1011)
