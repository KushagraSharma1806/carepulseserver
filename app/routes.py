from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import os
import json
import logging
from jose import jwt, JWTError
from dotenv import load_dotenv
from bson import ObjectId

from .database import db  # MongoDB database client
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .specialization_mapping import get_specialist_for_symptom
import openai

# Load environment variables
load_dotenv(dotenv_path="./.env")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenRouter config
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

router = APIRouter()


# ==== Models ====
class SymptomInput(BaseModel):
    symptoms: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: str
    role: str

class VitalsCreate(BaseModel):
    heart_rate: int
    bp_systolic: int
    bp_diastolic: int
    oxygen: int
    temperature: float
    sugar: int
    symptoms: str

class VitalsOut(VitalsCreate):
    id: str = Field(..., alias="_id")
    timestamp: datetime

class AppointmentCreate(BaseModel):
    reason: str
    notes: Optional[str]
    preferred_date: datetime
    preferred_time: str

class AppointmentOut(AppointmentCreate):
    id: str = Field(..., alias="_id")
    user_id: str
    doctor_name: str
    status: str
    created_at: datetime


# ==== WebSocket Connection Manager ====
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, user_id: str):
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        for uid, ws in list(self.active_connections.items()):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(uid)

manager = ConnectionManager()


# ==== Token auth for WebSocket ====
async def get_current_user_websocket(websocket: WebSocket):
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008)
            raise HTTPException(status_code=401, detail="Missing token")

        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            await websocket.close(code=1008)
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"id": user_id, "email": email}
    except JWTError:
        await websocket.close(code=1008)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        await websocket.close(code=1011)
        raise HTTPException(status_code=500, detail=str(e))


# ==== AI Assistant ====
async def get_ai_response(symptoms: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful medical assistant. Provide possible causes, home remedies, "
                    "and when to see a doctor. Be clear, caring, and under 200 words.")},
                {"role": "user", "content": f"I am experiencing: {symptoms}"}
            ],
            temperature=0.6,
            max_tokens=250
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        raise HTTPException(status_code=503, detail="AI service unavailable.")


# ==== ROUTES ====

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    try:
        existing = await db.users.find_one({"email": user.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = hash_password(user.password)
        new_user = {
            "name": user.name,
            "email": user.email,
            "password": hashed,
            "role": "patient"
        }
        result = await db.users.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)
        return new_user
    except Exception as e:
        print("❌ Error in /register:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": str(db_user["_id"]), "email": db_user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/vitals", response_model=VitalsOut)
async def submit_vitals(data: VitalsCreate, current_user: dict = Depends(get_current_user)):
    vitals = data.dict()
    vitals.update({
        "user_id": str(current_user["_id"]),
        "timestamp": datetime.utcnow()
    })
    result = await db.vitals.insert_one(vitals)
    vitals["_id"] = str(result.inserted_id)

    # 🛠️ FIX: make datetime serializable
    vitals_copy = {**vitals, "timestamp": vitals["timestamp"].isoformat()}

    await manager.send_personal_message(
        json.dumps({"event": "new_vitals", "data": vitals_copy}),
        current_user["_id"]
    )

    return vitals

@router.get("/vitals", response_model=List[VitalsOut])
async def get_vitals(
    days: Optional[int] = Query(None),
    limit: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    filter = {"user_id": str(current_user["_id"])}
    
    if days:
        since = datetime.utcnow() - timedelta(days=days)
        filter["timestamp"] = {"$gte": since}

    cursor = db.vitals.find(filter).sort("timestamp", -1)
    if limit:
        cursor = cursor.limit(limit)

    results = await cursor.to_list(length=limit or 1000)
    for doc in results:
        doc["_id"] = str(doc["_id"])
        doc["timestamp"] = doc["timestamp"].isoformat()  # 🛠️ fix datetime
    return results


@router.post("/analyze-symptoms")
async def analyze_symptoms(payload: SymptomInput, current_user: dict = Depends(get_current_user)):
    analysis = await get_ai_response(payload.symptoms)
    return {"analysis": analysis}

@router.post("/appointments", response_model=AppointmentOut)
async def book_appointment(payload: AppointmentCreate, current_user: dict = Depends(get_current_user)):
    try:
        specialization = get_specialist_for_symptom(payload.reason)
        doctor = await db.doctors.find_one({"specialization": specialization, "is_available": True})
        doctor_name = doctor["name"] if doctor else "Dr. Auto Assign"

        appointment = payload.dict()
        appointment.update({
            "user_id": str(current_user["_id"]),
            "doctor_name": doctor_name,
            "status": "pending",
            "created_at": datetime.utcnow()
        })

        result = await db.appointments.insert_one(appointment)
        appointment["_id"] = str(result.inserted_id)
        appointment["created_at"] = appointment["created_at"].isoformat()  # ✅ Fix datetime serialization

        # Broadcast new appointment (converted to JSON-serializable form)
        await manager.broadcast({
            "event": "new_appointment",
            "data": {
                **appointment
            }
        })

        return appointment
    except Exception as e:
        print("❌ Error in /appointments:", e)
        raise HTTPException(status_code=500, detail="Failed to book appointment")


@router.get("/appointments", response_model=List[AppointmentOut])
async def get_user_appointments(
    status: Optional[str] = None,
    upcoming: Optional[bool] = None,
    doctor: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        filter = {"user_id": str(current_user["_id"])}  # ✅ Ensure it's a string
        if status:
            filter["status"] = status
        if doctor:
            filter["doctor_name"] = {"$regex": doctor, "$options": "i"}
        if upcoming:
            now = datetime.utcnow()
            filter["preferred_date"] = {"$gte": now}

        results = await db.appointments.find(filter).sort("created_at", -1).to_list(100)

        # ✅ Convert ObjectId and datetime for safe JSON response
        cleaned = []
        for doc in results:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            if "preferred_date" in doc and isinstance(doc["preferred_date"], datetime):
                doc["preferred_date"] = doc["preferred_date"].isoformat()
            if "created_at" in doc and isinstance(doc["created_at"], datetime):
                doc["created_at"] = doc["created_at"].isoformat()
            cleaned.append(doc)

        return cleaned

    except Exception as e:
        print("❌ Error in /appointments GET:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch appointments")


from fastapi import WebSocket, WebSocketDisconnect, HTTPException

@router.websocket("/ws/vitals")
async def websocket_vitals(websocket: WebSocket):
    try:
        user = await get_current_user_websocket(websocket)
        user_id = user["id"]
        await manager.connect(websocket, user_id)
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                manager.disconnect(user_id)
                break
            except Exception as e:
                print(f"Unexpected error in WebSocket loop: {e}")
                manager.disconnect(user_id)
                await websocket.close()
                break
    except HTTPException as e:
        print(f"WebSocket closed due to auth issue: {e.detail}")
    except Exception as e:
        print(f"WebSocket closed due to server error: {e}")
        await websocket.close(code=1011)
