from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime,Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="patient")  # patient or doctor

    # Relationships
    vitals = relationship("Vitals", back_populates="user")
    appointments = relationship("Appointment", back_populates="user")

class Vitals(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate = Column(Integer)
    bp_systolic = Column(Integer)
    bp_diastolic = Column(Integer)
    oxygen = Column(Integer)
    temperature = Column(Float)  # Changed to Float for more precise temperature
    sugar = Column(Integer)
    symptoms = Column(String(500))  # Increased length for more detailed symptoms
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="vitals")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(String(500), nullable=False)
    notes = Column(String(1000))  # Added for additional appointment notes
    doctor_name = Column(String(100), default="Dr. Auto Assign")
    status = Column(String(50), default="pending")  # pending, confirmed, cancelled, completed
    preferred_date = Column(DateTime)  # Added for scheduling
    preferred_time = Column(String(50))  # Added for time slots
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="appointments")

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    is_available = Column(Boolean, default=True)
