from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv
import os

from app.models import User, Vitals, Appointment, Doctor  # ✅ Import your Beanie models

# Load environment variables
load_dotenv()

# MongoDB URI from .env
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("⚠️ MONGO_URI is not set in the .env file!")

# Create Motor client
client = AsyncIOMotorClient(MONGO_URI)
db = client["carepulse"]  # You can rename this if needed

# ✅ Beanie Initialization function
async def init_db():
    await init_beanie(
        database=db,
        document_models=[User, Vitals, Appointment, Doctor]
    )

# ✅ Dependency for FastAPI routes
async def get_db():
    return db
