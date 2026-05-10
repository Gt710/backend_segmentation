import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from database import SessionLocal, Scan, Patient

db = SessionLocal()
print("--- Patients ---")
for p in db.query(Patient).all():
    print(f"ID: {p.id}, First Name: {p.first_name}, Last Name: {p.last_name}")

print("--- Scans ---")
for s in db.query(Scan).all():
    print(f"ID: {s.id}, Patient ID: {s.patient_id}, Scan Number: {s.scan_number}, Status: {s.status}")
