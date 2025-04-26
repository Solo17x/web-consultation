from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models here to prevent circular imports
from .models import Admin, Doctor, Patient, Message, VideoCall  # Import from models.py
