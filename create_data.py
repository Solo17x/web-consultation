from models import db, Admin, Doctor, Patient
from app import app
from datetime import datetime
import random
import json

# ---------------- RESET DATABASE ---------------------
def reset_database():
    db.drop_all()
    db.create_all()
    print("🗑️ Database reset successfully!")

# ---------------- ADMIN ---------------------
def create_admin():
    admin = Admin(
        full_name="Admin User",
        email="admin@example.com",
        active=False
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin created successfully!")

# ---------------- LOAD CLINICS ---------------------
def load_clinics_data():
    with open("C:/Users/63963/Desktop/online_consultation/clinics.json", "r") as file:
        return json.load(file)

# ---------------- DOCTOR ---------------------
def create_doctors():
    clinics_data = load_clinics_data()

    doctor_details = [
        ("Dr. John Doe", "doctor1@gmail.com", "Cardiology", 10),
        ("Dr. Jane Smith", "doctor2@gmail.com", "Dermatology", 7),
        ("Dr. Michael Brown", "doctor3@gmail.com", "Orthopedics", 12),
        ("Dr. Sarah Wilson", "doctor4@gmail.com", "Pediatrics", 6),
        ("Dr. David Lee", "doctor5@gmail.com", "Neurology", 8),
    ]

    for name, email, specialization, experience in doctor_details:
        selected_clinic = random.choice(clinics_data)
        hospital_name = selected_clinic["name"]
        hospital_latitude = selected_clinic["latitude"]
        hospital_longitude = selected_clinic["longitude"]

        print(f"Assigning {hospital_name} to {name} located at {hospital_latitude}, {hospital_longitude}")

        doctor = Doctor(
            full_name=name,
            email=email,
            phone=f"{random.randint(1000000000, 9999999999)}",
            dob=datetime.strptime(f"{random.randint(1975, 1990)}-06-15", "%Y-%m-%d").date(),
            gender=random.choice(["Male", "Female"]),
            medical_license=f"MED{random.randint(100000, 999999)}",
            specialization=specialization,
            experience=experience,
            qualifications="MBBS, MD",
            hospital_clinic=hospital_name,
            availability="Monday-Friday 9AM-5PM",
            profile_picture="uploads/profile_pics/th.jpg",
            country="Philippines",
            city="Laoag City",
            short_bio=f"Experienced {specialization.lower()} with {experience} years of practice.",
            linkedin="https://www.linkedin.com",
            clinic_latitude=hospital_latitude,
            clinic_longitude=hospital_longitude,
            email_verified=True,
            is_approved=True,
            active=False,

                    
            # NEW DOCUMENT FIELDS
            license_front="uploads/licenses/prc_front.jpg",
            license_back="uploads/licenses/prc_back.jpg",
            board_cert="uploads/licenses/board_cert.jpg",
        )
        doctor.set_password("doctor123")
        db.session.add(doctor)
        db.session.commit()
        print(f"✅ {name} created successfully!")

# ---------------- PATIENT ---------------------
def create_patients():
    patient_details = [
        ("Alice Johnson", "patient1@gmail.com", "O+", "None", "None", "None"),
        ("Bob Williams", "patient2@gmail.com", "A-", "Asthma", "Inhaler", "None"),
        ("Charlie Davis", "patient3@gmail.com", "B+", "Diabetes", "Insulin", "None"),
        ("David Martinez", "patient4@gmail.com", "AB+", "Hypertension", "Beta Blockers", "None"),
        ("Eva Thomas", "patient5@gmail.com", "O-", "None", "None", "Appendectomy"),
    ]

    laoag_coordinates = [
        (18.1978, 120.5953),
        (18.2005, 120.5912),
        (18.1906, 120.5969),
        (18.2035, 120.5899),
        (18.2092, 120.5970),
    ]
    
    for index, (full_name, email, blood_type, existing_conditions, current_medication, past_surgeries) in enumerate(patient_details):
        latitude, longitude = laoag_coordinates[index]

        patient = Patient(
            full_name=full_name,
            email=email,
            phone=f"{random.randint(1000000000, 9999999999)}",
            dob=datetime.strptime(f"{random.randint(1990, 2000)}-08-20", "%Y-%m-%d").date(),
            gender=random.choice(["Male", "Female"]),
            city="Laoag City",
            country="Ilocos Norte",
            blood_type=blood_type,
            existing_conditions=existing_conditions,
            current_medication=current_medication,
            past_surgeries=past_surgeries,
            emergency_contact_name="John Doe",
            emergency_contact_phone="0123456789",
            preferred_language="English",
            profile_picture="uploads/profile_pics/th.jpg",
            latitude=latitude,
            longitude=longitude,
            email_verified=True,
            active=False
        )
        patient.set_password("patient123")
        db.session.add(patient)
        db.session.commit()
        print(f"✅ {full_name} created successfully!")

# ---------------- RUN SCRIPT ---------------------
if __name__ == "__main__":
    with app.app_context():
        reset_database()
        create_admin()
        create_doctors()
        create_patients()
