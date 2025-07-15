from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.database import init_db
from app.scheduler import assign_pending_appointments_mongo
import asyncio
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can also allow frontend domain when deployed
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

    asyncio.create_task(scheduler_loop())
    print("✅ Background MongoDB scheduler started")

# ✅ Include API routes
app.include_router(router)

# ✅ For Render deployment: bind to 0.0.0.0 and use PORT from environment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # fallback to 8000 if PORT not set
    uvicorn.run("main:app", host="0.0.0.0", port=port)
