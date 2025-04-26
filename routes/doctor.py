import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from models import db, Doctor
from config.config import UPLOAD_FOLDER
from datetime import datetime
import json
from werkzeug.security import generate_password_hash

doctor_bp = Blueprint('doctor', __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Load clinic data from the JSON file
with open('C:/Users/63963/Desktop/online_consultation/clinics.json', 'r') as f:
    clinics_data = json.load(f)

# Function to get the latitude and longitude based on clinic name
def get_clinic_coordinates(clinic_name):
    for clinic in clinics_data:
        if clinic["name"] == clinic_name:
            return clinic["id"], clinic["name"], clinic["latitude"], clinic["longitude"]
    return None, None, None, None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@doctor_bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        flash("Doctor not found!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        medical_license_number = request.form.get('medical_license')
        specialization = request.form.get('specialization')
        years_of_experience = request.form.get('experience')
        qualifications = request.form.get('qualifications')
        hospital_clinic = request.form.get('hospital_clinic')
        availability_schedule = request.form.get('availability')
        country = request.form.get('country')
        city = request.form.get('city')
        short_bio = request.form.get('short_bio')
        linkedin = request.form.get('linkedin')

        # Get the latitude and longitude of the selected clinic
        clinic_id, clinic_name, clinic_latitude, clinic_longitude = get_clinic_coordinates(hospital_clinic)

        # Debugging: Print received form data
        print(request.form)
        print(f"Clinic Coordinates: {clinic_latitude}, {clinic_longitude}")

        # Ensure date is correctly formatted
        if dob:
            try:
                doctor.dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid date format! Use YYYY-MM-DD.", "danger")
                return redirect(url_for('doctor.edit_profile'))

        # Update fields
        doctor.full_name = full_name
        doctor.phone = phone
        doctor.gender = gender
        doctor.medical_license = medical_license_number
        doctor.specialization = specialization
        doctor.experience = years_of_experience
        doctor.qualifications = qualifications
        doctor.hospital_clinic = hospital_clinic
        doctor.clinic_latitude = clinic_latitude
        doctor.clinic_longitude = clinic_longitude
        doctor.availability = availability_schedule
        doctor.country = country
        doctor.city = city
        doctor.short_bio = short_bio
        doctor.linkedin = linkedin

        # Handle Profile Picture Upload
        profile_picture = request.files.get('profile_picture')
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(f"doctor_{doctor_id}_{profile_picture.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            profile_picture.save(filepath)
            doctor.profile_picture = filename  

        # Handle Password Update
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password and confirm_password:
            if password == confirm_password:
                doctor.set_password(password)  # Hash the new password
            else:
                flash("Passwords do not match!", "danger")
                return redirect(url_for('doctor.edit_profile'))

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
            print(f"Error: {str(e)}")

        return redirect(url_for('doctor.edit_profile'))

    return render_template('doctor/edit_profile_doctor.html', doctor=doctor, clinics_data=clinics_data)
