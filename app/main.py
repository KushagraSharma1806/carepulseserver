from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.database import init_db
from app.scheduler import assign_pending_appointments_mongo
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Background coroutine
async def scheduler_loop():
    while True:
        try:
            await assign_pending_appointments_mongo()
        except Exception as e:
            print(f"❌ Error during MongoDB appointment assignment: {e}")
        await asyncio.sleep(60)

@app.on_event("startup")
async def app_startup():
    await init_db()
    print("✅ Beanie initialized with MongoDB")

    asyncio.create_task(scheduler_loop())  # ✅ No new thread, stays in FastAPI loop
    print("✅ Background MongoDB scheduler started")

# Include routes
app.include_router(router)
