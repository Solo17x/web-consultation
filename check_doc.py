from app import app, db  # Assuming you have app and db initialized directly in app.py
from models import Doctor  # Adjust the import based on your project structure

# Fetch all doctors and check the hospital_clinic field
def check_doctors_clinic():
    with app.app_context():  # Manually push the app context
        doctors = Doctor.query.all()  # Get all doctors from the database
        for doctor in doctors:
            print(f"Doctor ID: {doctor.id}, Name: {doctor.full_name}, Hospital/Clinic: {doctor.hospital_clinic}")

# Run the function
check_doctors_clinic()
