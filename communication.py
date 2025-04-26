import random
from app import app  # Import your Flask app
from models import db, Doctor, Patient, Message, VideoCall

def send_message_between_doctor_patient():
    with app.app_context():  # Ensure the app context is pushed
        # Fetch all doctors and patients
        doctors = Doctor.query.all()
        patients = Patient.query.all()

        # Check if doctors and patients exist in the database
        if not doctors or not patients:
            print("❌ No doctors or patients found!")
            return

        # Randomly pick a doctor and a patient
        doctor = random.choice(doctors)
        patient = random.choice(patients)

        # Scenario 1: Send message from doctor to patient
        message_content = "Hello, how can I assist you with your health today?"
        # Use the send_message method in Doctor model
        doctor.send_message(patient, message_content)

        # Scenario 2: Send message from patient to doctor
        patient_message_content = "I need some advice regarding my health issues."
        # Use the send_message method in Patient model
        patient.send_message(doctor, patient_message_content)

        # Detailed output with doctor's specialization and email
        print(f"✅ Messages sent between Dr. {doctor.full_name} ({doctor.specialization}) and Patient {patient.full_name} (Patient Email: {patient.email})")

def send_message_patient_to_doctor():
    with app.app_context():  # Ensure the app context is pushed
        # Fetch all doctors and patients
        doctors = Doctor.query.all()
        patients = Patient.query.all()

        # Check if doctors and patients exist in the database
        if not doctors or not patients:
            print("❌ No doctors or patients found!")
            return

        # Randomly pick a doctor and a patient
        doctor = random.choice(doctors)
        patient = random.choice(patients)

        # Send message from patient to doctor
        patient_message_content = "Can you suggest a treatment plan for me?"
        # Use the send_message method in Patient model
        patient.send_message(doctor, patient_message_content)

        # Detailed output with doctor's specialization and email
        print(f"✅ Message sent from Patient {patient.full_name} to Dr. {doctor.full_name} ({doctor.specialization}) - Doctor Email: {doctor.email}")

def start_video_call_between_doctor_patient():
    with app.app_context():  # Ensure the app context is pushed
        # Fetch all doctors and patients
        doctors = Doctor.query.all()
        patients = Patient.query.all()

        # Check if doctors and patients exist in the database
        if not doctors or not patients:
            print("❌ No doctors or patients found!")
            return

        # Randomly pick a doctor and a patient
        doctor = random.choice(doctors)
        patient = random.choice(patients)

        # Start a video call from doctor to patient
        doctor.start_video_call(patient)

        # Detailed output with doctor's specialization and email
        print(f"✅ Video call initiated from Dr. {doctor.full_name} ({doctor.specialization}) to Patient {patient.full_name} - Patient Email: {patient.email}")

def start_video_call_patient_to_doctor():
    with app.app_context():  # Ensure the app context is pushed
        # Fetch all doctors and patients
        doctors = Doctor.query.all()
        patients = Patient.query.all()

        # Check if doctors and patients exist in the database
        if not doctors or not patients:
            print("❌ No doctors or patients found!")
            return

        # Randomly pick a doctor and a patient
        doctor = random.choice(doctors)
        patient = random.choice(patients)

        # Start a video call from patient to doctor
        patient.start_video_call(doctor)

        # Detailed output with doctor's specialization and email
        print(f"✅ Video call initiated from Patient {patient.full_name} to Dr. {doctor.full_name} ({doctor.specialization}) - Doctor Email: {doctor.email}")

def main():
    try:
        # Call functions to send messages and start video calls
        send_message_between_doctor_patient()
        send_message_patient_to_doctor()
        start_video_call_between_doctor_patient()
        start_video_call_patient_to_doctor()
    except Exception as e:
        # Handle any potential errors
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    # Run the script
    main()
