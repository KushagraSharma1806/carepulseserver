import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("⚠️ MONGO_URI is not set in the .env file!")

client = AsyncIOMotorClient(MONGO_URI)
db = client["carepulse"]  # Change if you use a different database name

doctors = [
    {"name": "Dr. Meera Shah", "specialization": "Dermatologist", "is_available": True},
    {"name": "Dr. Arjun Kapoor", "specialization": "Dermatologist", "is_available": True},
    
    {"name": "Dr. Rohan Gupta", "specialization": "General Physician", "is_available": True},
    {"name": "Dr. Priya Desai", "specialization": "General Physician", "is_available": True},

    {"name": "Dr. Vikram Joshi", "specialization": "Cardiologist", "is_available": True},
    {"name": "Dr. Neha Reddy", "specialization": "Cardiologist", "is_available": True},

    {"name": "Dr. Anjali Menon", "specialization": "Neurologist", "is_available": True},
    {"name": "Dr. Karthik Nair", "specialization": "Neurologist", "is_available": True},

    {"name": "Dr. Sameer Khan", "specialization": "Ophthalmologist", "is_available": True},
    {"name": "Dr. Divya Patel", "specialization": "Ophthalmologist", "is_available": True},

    {"name": "Dr. Amit Sharma", "specialization": "Gastroenterologist", "is_available": True},
    {"name": "Dr. Sneha Iyer", "specialization": "Gastroenterologist", "is_available": True},

    {"name": "Dr. Rahul Verma", "specialization": "Orthopedist", "is_available": True},
    {"name": "Dr. Ananya Das", "specialization": "Orthopedist", "is_available": True},

    {"name": "Dr. Sanjay Rao", "specialization": "ENT Specialist", "is_available": True},
    {"name": "Dr. Nandini Choudhary", "specialization": "ENT Specialist", "is_available": True},

    {"name": "Dr. Aditya Malhotra", "specialization": "Psychiatrist", "is_available": True},
    {"name": "Dr. Swati Banerjee", "specialization": "Pulmonologist", "is_available": True},
    {"name": "Dr. Varun Sethi", "specialization": "Allergist", "is_available": True},
    {"name": "Dr. Deepika Srinivasan", "specialization": "Endocrinologist", "is_available": True},
    {"name": "Dr. Harish Prabhu", "specialization": "Urologist", "is_available": True},
    {"name": "Dr. Gayatri Menon", "specialization": "Nephrologist", "is_available": True},
]

async def seed_doctors():
    try:
        existing_count = await db.doctors.count_documents({})
        if existing_count > 0:
            print("Doctors already seeded.")
            return

        result = await db.doctors.insert_many(doctors)
        print(f"✅ Successfully seeded {len(result.inserted_ids)} doctors.")
    except Exception as e:
        print(f"❌ Error seeding doctors: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_doctors())
