from .database import SessionLocal
from .models import Doctor

db = SessionLocal()

# Expanded list of doctors covering all specializations from the mapping
doctors = [
    # Dermatologists
    Doctor(name="Dr. Meera Shah", specialization="Dermatologist"),
    Doctor(name="Dr. Arjun Kapoor", specialization="Dermatologist"),
    
    # General Physicians
    Doctor(name="Dr. Rohan Gupta", specialization="General Physician"),
    Doctor(name="Dr. Priya Desai", specialization="General Physician"),
    
    # Cardiologists
    Doctor(name="Dr. Vikram Joshi", specialization="Cardiologist"),
    Doctor(name="Dr. Neha Reddy", specialization="Cardiologist"),
    
    # Neurologists
    Doctor(name="Dr. Anjali Menon", specialization="Neurologist"),
    Doctor(name="Dr. Karthik Nair", specialization="Neurologist"),
    
    # Ophthalmologists
    Doctor(name="Dr. Sameer Khan", specialization="Ophthalmologist"),
    Doctor(name="Dr. Divya Patel", specialization="Ophthalmologist"),
    
    # Gastroenterologists
    Doctor(name="Dr. Amit Sharma", specialization="Gastroenterologist"),
    Doctor(name="Dr. Sneha Iyer", specialization="Gastroenterologist"),
    
    # Orthopedists
    Doctor(name="Dr. Rahul Verma", specialization="Orthopedist"),
    Doctor(name="Dr. Ananya Das", specialization="Orthopedist"),
    
    # ENT Specialists
    Doctor(name="Dr. Sanjay Rao", specialization="ENT Specialist"),
    Doctor(name="Dr. Nandini Choudhary", specialization="ENT Specialist"),
    
    # Psychiatrists
    Doctor(name="Dr. Aditya Malhotra", specialization="Psychiatrist"),
    
    # Pulmonologists
    Doctor(name="Dr. Swati Banerjee", specialization="Pulmonologist"),
    
    # Allergists
    Doctor(name="Dr. Varun Sethi", specialization="Allergist"),
    
    # Endocrinologists
    Doctor(name="Dr. Deepika Srinivasan", specialization="Endocrinologist"),
    
    # Urologists
    Doctor(name="Dr. Harish Prabhu", specialization="Urologist"),
    
    # Nephrologists
    Doctor(name="Dr. Gayatri Menon", specialization="Nephrologist")
]

try:
    db.add_all(doctors)
    db.commit()
    print(f"Successfully seeded {len(doctors)} doctors.")
except Exception as e:
    db.rollback()
    print(f"Error seeding doctors: {str(e)}")
finally:
    db.close()