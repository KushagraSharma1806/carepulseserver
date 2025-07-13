SYMPTOM_TO_SPECIALIZATION = {
    # Dermatology
    "skin": "Dermatologist",
    "rash": "Dermatologist",
    "acne": "Dermatologist",
    "eczema": "Dermatologist",
    "psoriasis": "Dermatologist",
    "hives": "Dermatologist",
    
    # General Medicine
    "fever": "General Physician",
    "cough": "General Physician",
    "fatigue": "General Physician",
    "flu": "General Physician",
    "cold": "General Physician",
    "nausea": "General Physician",
    
    # Cardiology
    "chest pain": "Cardiologist",
    "palpitations": "Cardiologist",
    "shortness of breath": "Cardiologist",
    "high blood pressure": "Cardiologist",
    "heart murmur": "Cardiologist",
    
    # Neurology
    "headache": "Neurologist",
    "dizziness": "Neurologist",
    "seizures": "Neurologist",
    "numbness": "Neurologist",
    "tingling": "Neurologist",
    "migraine": "Neurologist",
    
    # Ophthalmology
    "vision": "Ophthalmologist",
    "eye pain": "Ophthalmologist",
    "red eye": "Ophthalmologist",
    "blurry vision": "Ophthalmologist",
    "dry eyes": "Ophthalmologist",
    
    # Gastroenterology
    "stomach pain": "Gastroenterologist",
    "diarrhea": "Gastroenterologist",
    "constipation": "Gastroenterologist",
    "heartburn": "Gastroenterologist",
    "bloating": "Gastroenterologist",
    
    # Orthopedics
    "joint pain": "Orthopedist",
    "back pain": "Orthopedist",
    "swollen joint": "Orthopedist",
    "fracture": "Orthopedist",
    "sports injury": "Orthopedist",
    
    # ENT
    "ear pain": "ENT Specialist",
    "sore throat": "ENT Specialist",
    "sinus pain": "ENT Specialist",
    "hearing loss": "ENT Specialist",
    "tinnitus": "ENT Specialist",
    
    # Additional mappings
    "depression": "Psychiatrist",
    "anxiety": "Psychiatrist",
    "asthma": "Pulmonologist",
    "allergy": "Allergist",
    "diabetes": "Endocrinologist",
    "thyroid": "Endocrinologist",
    "urinary": "Urologist",
    "kidney": "Nephrologist"
}

# Case-insensitive matching function
def get_specialist_for_symptom(symptom):
    symptom_lower = symptom.lower()
    for key, value in SYMPTOM_TO_SPECIALIZATION.items():
        if key in symptom_lower:
            return value
    return "General Physician"  # Default fallback