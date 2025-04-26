import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

def generate_unique_filename(filename):
    """Generate a unique filename using UUID and retain the original file extension."""
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def save_profile_picture(profile_picture):
    """Save the uploaded profile picture to the server and return the filename."""
    if profile_picture:
        try:
            filename = generate_unique_filename(secure_filename(profile_picture.filename))
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "profile_pics", filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            profile_picture.save(save_path)
            return filename
        except Exception as e:
            # Log or handle the error as needed (optional)
            return None
    return None

def save_license_file(file, subfolder="licenses"):
    """Save a single license file to the server and return the filename."""
    if file and file.filename:
        try:
            filename = generate_unique_filename(secure_filename(file.filename))
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder, filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            file.save(save_path)
            return filename
        except Exception as e:
            # Log or handle the error as needed (optional)
            return None
    return None

