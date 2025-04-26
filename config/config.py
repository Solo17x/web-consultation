import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Instance directory (for storing database files)
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)  # ✅ Ensure instance directory exists

# Uploads directory (for storing profile pictures, documents, etc.)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # ✅ Ensure uploads folder exists

class Config:
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

    # ✅ Main database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'main.db')}"

    # ✅ Separate databases for patients & doctors
    SQLALCHEMY_BINDS = {
        "patients": f"sqlite:///{os.path.join(INSTANCE_DIR, 'patients.db')}",
        "doctors": f"sqlite:///{os.path.join(INSTANCE_DIR, 'doctors.db')}",
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ File Uploads
    UPLOAD_FOLDER = UPLOAD_FOLDER
