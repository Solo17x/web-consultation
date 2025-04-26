from models import db, Admin, Doctor, Patient
from app import app  # Import your Flask app

with app.app_context():  # Ensure the database is linked to Flask app
    admins = Admin.query.all()
    doctors = Doctor.query.all()
    patients = Patient.query.all()

    print("\n🔹 Admins:")
    if not admins:
        print("❌ No admins found!")
    for admin in admins:
        print(f"- {admin.full_name} | {admin.email}")

    print("\n🔹 Doctors:")
    if not doctors:
        print("❌ No doctors found!")
    for doctor in doctors:
        print(f"- {doctor.full_name} | {doctor.email} | {doctor.specialization}")

    print("\n🔹 Patients:")
    if not patients:
        print("❌ No patients found!")
    for patient in patients:
        print(f"- {patient.full_name} | {patient.email} | {patient.blood_type}")
