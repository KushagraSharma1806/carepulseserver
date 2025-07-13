from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import router
from .scheduler import assign_pending_appointments
import threading
import time

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update to match your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
models.Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)

# Background job to assign doctors to pending appointments
def run_scheduler():
    while True:
        assign_pending_appointments()
        time.sleep(60)  # Runs every 60 seconds

@app.on_event("startup")
def start_background_worker():
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("✅ Background task for auto-assigning appointments started.")

