from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pytz import timezone
import random

from .models import Appointment, Doctor
from .database import SessionLocal
from .specialization_mapping import get_specialist_for_symptom

def assign_pending_appointments():
    db: Session = SessionLocal()
    try:
        pending_appointments = db.query(Appointment).filter(Appointment.status == "pending").all()

        IST = timezone("Asia/Kolkata")
        now_ist = datetime.now(IST)

        for appt in pending_appointments:
            specialist = get_specialist_for_symptom(appt.reason or "")
            doctor = (
                db.query(Doctor)
                .filter(Doctor.specialization == specialist)
                .filter(Doctor.is_available == True)
                .first()
            )

            if doctor:
                appt.status = "confirmed"
                appt.doctor_id = doctor.id
                appt.doctor_name = doctor.name
                appt.updated_at = datetime.utcnow()  # Stored in UTC for backend consistency

                # Only assign preferred time if not already set
                if not appt.preferred_date or not appt.preferred_time:
                    appt.preferred_date = now_ist.date() + timedelta(days=1)
                    appt.preferred_time = now_ist.replace(
                        hour=random.randint(9, 17),
                        minute=random.choice([0, 15, 30, 45]),
                        second=0, microsecond=0
                    ).time()

                # Optionally mark doctor unavailable (uncomment if needed)
                # doctor.is_available = False

        db.commit()
        print(f"✅ Auto-assigned doctors to {len(pending_appointments)} pending appointments.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error while assigning appointments: {str(e)}")
    finally:
        db.close()
