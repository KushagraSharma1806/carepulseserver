# Mapping of symptom keywords to specializations
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

    # Psychiatry / Mental Health
    "depression": "Psychiatrist",
    "anxiety": "Psychiatrist",

    # Pulmonology / Respiratory
    "asthma": "Pulmonologist",

    # Immunology / Allergies
    "allergy": "Allergist",

    # Endocrinology / Hormonal
    "diabetes": "Endocrinologist",
    "thyroid": "Endocrinologist",

    # Urology
    "urinary": "Urologist",

    # Nephrology
    "kidney": "Nephrologist"
}

def get_specialist_for_symptom(symptom: str) -> str:
    """
    Returns the appropriate specialist for a given symptom using substring matching.
    Falls back to 'General Physician' if no match is found.
    """
    symptom_lower = symptom.lower()

    for keyword, specialization in SYMPTOM_TO_SPECIALIZATION.items():
        if keyword in symptom_lower:
            return specialization

    return "General Physician"
