import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Створюємо директорію для БД якщо її немає
os.makedirs("data", exist_ok=True)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/segmentation.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    dob = Column(String) # YYYY-MM-DD
    phone = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    scans = relationship("Scan", back_populates="patient")

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    status = Column(String) # e.g., "completed", "failed"
    tumor_volume_cm3 = Column(Float)
    conclusion = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    patient = relationship("Patient", back_populates="scans")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Створення таблиць
def init_db():
    Base.metadata.create_all(bind=engine)
