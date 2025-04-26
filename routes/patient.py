import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from models import db, Patient
from config.config import UPLOAD_FOLDER
from datetime import datetime
from .forms import DoctorRegistrationForm, PatientRegistrationForm, LoginForm, ResetPasswordForm
from flask_wtf import FlaskForm


patient_bp = Blueprint('patient', __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Load city data from the JSON file
with open('C:/Users/63963/Desktop/online_consultation/city.json', 'r') as f:
    cities_data = json.load(f)

# Populate the SelectField choices with city names, latitude, and longitude
cities = [(city["id"], city["city"], city["latitude"], city["longitude"]) for city in cities_data]

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@patient_bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    patient_id = session.get('user_id')
    patient = Patient.query.get(patient_id)

    if not patient:
        flash("Patient not found!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        country = request.form.get('country')
        city_id = request.form.get('city')
        city_name = next((city[1] for city in cities if str(city[0]) == city_id), None)
        latitude = next((city[2] for city in cities if str(city[0]) == city_id), None)
        longitude = next((city[3] for city in cities if str(city[0]) == city_id), None)
        blood_type = request.form.get('blood_type')
        current_medication = request.form.get('current_medication')
        past_surgeries = request.form.get('past_surgeries')
        emergency_contact_name = request.form.get('emergency_contact_name')
        emergency_contact_phone = request.form.get('emergency_contact_phone')
        preferred_language = request.form.get('preferred_language')
        date_of_birth = request.form.get('date_of_birth')

        # Ensure date is in YYYY-MM-DD format
        if date_of_birth:
            try:
                formatted_dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                patient.dob = formatted_dob
            except ValueError:
                flash("Invalid date format! Use YYYY-MM-DD.", "danger")
                return redirect(url_for('patient.edit_profile'))

        # Update patient data
        patient.full_name = full_name
        patient.phone = phone
        patient.gender = gender
        patient.country = country
        patient.city = city_name  # Store city name
        patient.latitude = latitude  # Store latitude
        patient.longitude = longitude  # Store longitude
        patient.blood_type = blood_type
        patient.current_medication = current_medication
        patient.past_surgeries = past_surgeries
        patient.emergency_contact_name = emergency_contact_name
        patient.emergency_contact_phone = emergency_contact_phone
        patient.preferred_language = preferred_language

        # Handle Profile Picture Upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"patient_{patient_id}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                patient.profile_picture = filename

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")

        return redirect(url_for('patient.edit_profile'))

    return render_template('patient/edit_profile_patient.html', patient=patient, cities=cities)