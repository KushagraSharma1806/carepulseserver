from datetime import datetime, timedelta
from pytz import timezone
import random
from .database import db
from .specialization_mapping import get_specialist_for_symptom

async def assign_pending_appointments_mongo():
    try:
        pending_appointments_cursor = db.appointments.find({"status": "pending"})
        pending_appointments = await pending_appointments_cursor.to_list(length=1000)

        IST = timezone("Asia/Kolkata")
        now_ist = datetime.now(IST)

        updated_count = 0

        for appt in pending_appointments:
            specialization = get_specialist_for_symptom(appt.get("reason", ""))
            doctor = await db.doctors.find_one({
                "specialization": specialization,
                "is_available": True
            })

            doctor_name = doctor["name"] if doctor else "Dr. Auto Assign"

            # Determine preferred date/time if not already set
            preferred_date = appt.get("preferred_date")
            preferred_time = appt.get("preferred_time")

            if not preferred_date:
                preferred_date = now_ist.date().isoformat()

            if not preferred_time:
                preferred_time = now_ist.replace(
                    hour=random.randint(9, 17),
                    minute=random.choice([0, 15, 30, 45]),
                    second=0, microsecond=0
                ).time().isoformat()

            update_data = {
                "status": "confirmed",
                "doctor_name": doctor_name,
                "updated_at": datetime.utcnow(),
                "preferred_date": preferred_date,
                "preferred_time": preferred_time
            }

            await db.appointments.update_one(
                {"_id": appt["_id"]},
                {"$set": update_data}
            )

            updated_count += 1

        print(f"✅ Auto-assigned {updated_count} pending appointments.")
    except Exception as e:
        print(f"❌ Error during MongoDB appointment assignment: {str(e)}")
