from flask import url_for
import socket  # ✅ Import socket
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import Doctor, Patient  # ✅ Import Doctor and Patient correctly
from extensions import mail  # ✅ Use the existing mail instance from app.py
from flask_mail import Message

def send_email(to, subject, body):
    """Sends an email using Flask-Mail."""
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)

def get_local_ip() -> str:
    """Retrieve the local IP address of the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"❌ Error getting local IP: {e}")
        return "127.0.0.1"

# ✅ Send Verification Email (Supports Patients & Doctors)
def send_verification_email(to_email, user):
    """Sends an email verification link to the user (Patient or Doctor) using Flask-Mail."""
    
    # ✅ Determine User Role
    role = "Doctor" if isinstance(user, Doctor) else "Patient"

    # ✅ Construct Verification Link
    verification_link = f"https://{get_local_ip()}:5001{url_for('auth.verify_account', token=user.verification_token)}"

    # ✅ Email Content
    subject = "Verify Your Email - Online Consultation"
    body = f"""
    Dear {user.full_name},

    Click the link below to verify your email as a {role}:
    {verification_link}

    If you did not sign up, please ignore this email.
    """

    # ✅ Send Email
    try:
        send_email(to_email, subject, body)
        print(f"✅ Verification email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        return False
