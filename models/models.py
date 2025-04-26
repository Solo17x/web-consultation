import os
from . import db  # Import db from __init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=False)  # Add 'active' field

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def mark_active(self):
        """Mark the admin as active."""
        self.active = True
        db.session.commit()

    def mark_offline(self):
        """Mark the admin as offline."""
        self.active = False
        db.session.commit()



class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    medical_license = db.Column(db.String(50), unique=True, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    qualifications = db.Column(db.Text, nullable=False)

    hospital_clinic = db.Column(db.String(255), nullable=False)
    clinic_latitude = db.Column(db.Float)  # Add latitude for the clinic
    clinic_longitude = db.Column(db.Float)  # Add longitude for the clinic
    
    availability = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)

        # Uploaded document paths
    license_front = db.Column(db.String(100), nullable=True)
    license_back = db.Column(db.String(100), nullable=True)
    board_cert = db.Column(db.String(100), nullable=True)
    
    # New Fields
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    short_bio = db.Column(db.Text, nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    
    active = db.Column(db.Boolean, default=False)  # New 'active' field

    def send_message(self, recipient, content):
        message = Message(sender=self, recipient=recipient, content=content)
        db.session.add(message)
        db.session.commit()
        print(f"✅ Message sent from Dr. {self.full_name} to {recipient.full_name if isinstance(recipient, Patient) else recipient.full_name}")

    def start_video_call(self, patient):       
        video_call = VideoCall(doctor_id=self.id, patient_id=patient.id, call_status='Pending')
        print(f"✅ Video call started from Dr. {self.full_name} to Patient {patient.full_name}")
        db.session.add(video_call)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        """
        Generate a password reset token.
        """
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'doctor_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """
        Verify the reset token and return the doctor if valid.
        """
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
        except:
            return None
        return Doctor.query.get(data['doctor_id'])

    def mark_active(self):
        """Mark the doctor as active."""
        self.active = True
        db.session.commit()

    def mark_offline(self):
        """Mark the doctor as offline."""
        self.active = False
        db.session.commit()


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    blood_type = db.Column(db.String(5))
    existing_conditions = db.Column(db.Text)
    current_medication = db.Column(db.Text)
    past_surgeries = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(150), nullable=False)
    emergency_contact_phone = db.Column(db.String(20), nullable=False)
    preferred_language = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255))
    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), unique=True)
    
    latitude = db.Column(db.Float)  # Patient latitude
    longitude = db.Column(db.Float)  # Patient longitude


    active = db.Column(db.Boolean, default=False)  # New 'active' field

    def send_message(self, recipient, content):
        message = Message(sender=self, recipient=recipient, content=content)
        db.session.add(message)
        db.session.commit()
        print(f"✅ Message sent from {self.full_name} to Dr. {recipient.full_name if isinstance(recipient, Doctor) else recipient.full_name}")

    def start_video_call(self, doctor):
        video_call = VideoCall(doctor_id=doctor.id, patient_id=self.id, call_status='Pending')
        print(f"✅ Video call started from Patient {self.full_name} to Dr. {doctor.full_name}")
        db.session.add(video_call)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        """
        Generate a password reset token.
        """
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'patient_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """
        Verify the reset token and return the patient if valid.
        """
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
        except:
            return None
        return Patient.query.get(data['patient_id'])

    def mark_active(self):
        """Mark the patient as active."""
        self.active = True
        db.session.commit()

    def mark_offline(self):
        """Mark the patient as offline."""
        self.active = False
        db.session.commit()


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender_id = db.Column(db.Integer, nullable=False)
    recipient_id = db.Column(db.Integer, nullable=False)

    sender_type = db.Column(db.String(50), nullable=False)
    recipient_type = db.Column(db.String(50), nullable=False)

    # Relationships
    sender = db.relationship('Doctor', backref='sent_messages', foreign_keys=[sender_id], primaryjoin="and_(Message.sender_type == 'doctor', Message.sender_id == Doctor.id)", uselist=False)
    recipient = db.relationship('Patient', backref='received_messages', foreign_keys=[recipient_id], primaryjoin="and_(Message.recipient_type == 'patient', Message.recipient_id == Patient.id)", uselist=False)

    def __repr__(self):
        return f'<Message from {self.sender.full_name if self.sender else self.sender_type} to {self.recipient.full_name if self.recipient else self.recipient_type}>'

    def __init__(self, sender, recipient, content):
        self.content = content
        self.timestamp = datetime.utcnow()

        if isinstance(sender, Doctor):
            self.sender_id = sender.id
            self.sender_type = 'doctor'
        elif isinstance(sender, Patient):
            self.sender_id = sender.id
            self.sender_type = 'patient'

        if isinstance(recipient, Doctor):
            self.recipient_id = recipient.id
            self.recipient_type = 'doctor'
        elif isinstance(recipient, Patient):
            self.recipient_id = recipient.id
            self.recipient_type = 'patient'


class VideoCall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    call_time = db.Column(db.DateTime, default=datetime.utcnow)
    call_duration = db.Column(db.Integer, nullable=True)  # Duration in seconds, optional
    call_status = db.Column(db.String(50), nullable=False, default='Pending')  # e.g., 'Pending', 'Completed', 'Cancelled'
    
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    doctor = db.relationship('Doctor', backref='video_calls')
    patient = db.relationship('Patient', backref='video_calls')

    def __repr__(self):
        return f'<VideoCall between {self.doctor.full_name} and {self.patient.full_name}>'
    
        #BASE ON THE MESSAGE
