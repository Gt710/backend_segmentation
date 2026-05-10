import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Створюємо директорію для БД якщо її немає
os.makedirs("data", exist_ok=True)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/segmentation_v2.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) # "Admin", "Radiologist"

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    # Ці поля будуть зберігатися в зашифрованому вигляді (AES)
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
    scan_number = Column(String) # BraTS scan number (e.g., "00005")
    status = Column(String) # e.g., "completed", "failed"
    tumor_volume_cm3 = Column(Float)
    conclusion = Column(String)
    tumor_nature = Column(String) # "Доброякісна", "Злоякісна", "Недостатньо даних"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    patient = relationship("Patient", back_populates="scans")


class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    previous_hash = Column(String)
    current_hash = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Створення таблиць
def init_db():
    Base.metadata.create_all(bind=engine)
