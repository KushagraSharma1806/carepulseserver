from .database import SessionLocal

try:
    db = SessionLocal()
    print("✅ MySQL connection successful!")
    db.close()
except Exception as e:
    print("❌ Connection error:", e)