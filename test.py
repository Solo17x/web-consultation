import random
from models import db, Doctor, Patient, Message, VideoCall
from app import app

def create_sample_chats_and_calls(num_messages=5, num_video_calls=3):
    with app.app_context():
        doctors = Doctor.query.all()
        patients = Patient.query.all()
        
        if not doctors or not patients:
            print("❌ No doctors or patients found!")
            return

        for _ in range(num_messages):
            doctor = random.choice(doctors)
            patient = random.choice(patients)

            # Create sample messages
            message1 = Message(
                sender_id=doctor.id,
                receiver_id=patient.id,
                content="Hello, how can I assist you today?"
            )
            message2 = Message(
                sender_id=patient.id,
                receiver_id=doctor.id,
                content="I need some advice regarding my health issue."
            )

            db.session.add_all([message1, message2])

        for _ in range(num_video_calls):
            doctor = random.choice(doctors)
            patient = random.choice(patients)

            # Create sample video calls
            video_call = VideoCall(doctor_id=doctor.id, patient_id=patient.id, call_status='Pending')
            db.session.add(video_call)

        db.session.commit()
        print("✅ Sample data created successfully!")
