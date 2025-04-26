from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, Admin, Doctor, Patient
from .forms import DoctorRegistrationForm, PatientRegistrationForm, LoginForm, ResetPasswordForm
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Mail, Message
import os, re
import uuid  # 🔹 Import for generating verification tokens
import random 
from utils.image_check import is_blurry
import string 
import json
import traceback
from services.email_service import send_verification_email , send_email # ✅ Import email function
from datetime import datetime
from dotenv import load_dotenv
from utils.file_saver import (
    save_profile_picture,
    save_license_file,
)
# from services.email_service import mail 

load_dotenv()

# Create Blueprint
auth = Blueprint("auth", __name__)

# Initialize Flask-Mail
mail = Mail()

# Set upload folder
UPLOAD_FOLDER = "static/uploads"

RESET_CODES = {}

def generate_reset_code(length=6):
    """Generate a secure 6-character reset code."""
    return ''.join(random.choices(string.digits, k=length))

def is_valid_email(email):
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


@auth.route("/check-email", methods=["GET"])
def check_email():
    email = request.args.get("email", "").strip().lower()
    existing_user = (
        Admin.query.filter_by(email=email).first()
        or Doctor.query.filter_by(email=email).first()
        or Patient.query.filter_by(email=email).first()
    )
    
    return {"exists": bool(existing_user)}


def get_serializer():
    """Initialize a URLSafeTimedSerializer for email verification tokens."""
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])



# Login route
@auth.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id") and session.get("user_role"):
        return redirect_dashboard()

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()  # Normalize email
        password = form.password.data

        # Find user from Admin, Doctor, or Patient
        user = Admin.query.filter_by(email=email).first() or \
               Doctor.query.filter_by(email=email).first() or \
               Patient.query.filter_by(email=email).first()

        if user and user.check_password(password):  # ✅ Uses the correct password check method
            # ✅ Doctor Verification & Approval Check
            if isinstance(user, Doctor):
                if not user.email_verified:  # ✅ Corrected field name
                    flash("Your email is not verified. Please check your email.", "warning")
                    return redirect(url_for("auth.login"))
                if not user.is_approved:  # ✅ Ensures admin approval
                    session.clear()  # 🚨 Prevent doctor from staying logged in
                    flash("Your account is pending admin approval.", "warning")
                    return redirect(url_for("auth.login"))

            # ✅ Patient Email Verification Check
            elif isinstance(user, Patient):
                if not user.email_verified:  # ✅ Corrected field name
                    flash("Your email is not verified. Please check your email.", "warning")
                    return redirect(url_for("auth.login"))

            # ✅ Set session for logged-in user
            session["user_id"] = user.id
            session["user_role"] = (
                "admin" if isinstance(user, Admin) else
                "doctor" if isinstance(user, Doctor) else
                "patient"
            )

            # ✅ Store user name in session
            if isinstance(user, Patient):
                session["patient_name"] = user.full_name  # Store patient's full name
            if isinstance(user, Doctor):
                session["doctor_name"] = user.full_name  # Store full name when logging in
                session["doctor_id"] = user.id  # Store doctor ID when doctor logs in

            session.permanent = True

            # Set the user's status to Active
            user.mark_active()  # This will mark the doctor/patient as 'Active'

            flash("Login successful!", "success")
            return redirect_dashboard()

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


# ✅ LOGOUT ROUTE
@auth.route("/logout")
def logout():
    # Fetch the user based on session data
    user = None
    if session.get("user_id") and session.get("user_role"):
        user_id = session["user_id"]
        user_role = session["user_role"]
        
        if user_role == "doctor":
            user = Doctor.query.get(user_id)
        elif user_role == "patient":
            user = Patient.query.get(user_id)
        elif user_role == "admin":
            user = Admin.query.get(user_id)

    if user:
        # Set the user's status to Offline when logging out
        user.mark_offline()  # This will mark the user as 'Offline'

    # Clear the session and logout
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))




@auth.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    form = PatientRegistrationForm()

    if form.validate_on_submit():
        # Check if email already exists
        existing_patient = Patient.query.filter_by(email=form.email.data).first()
        if existing_patient:
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register_patient"))

        try:
            # Convert DOB to date object
            dob_obj = datetime.strptime(form.dob.data, "%Y-%m-%d").date()

            # Handle profile picture upload
            profile_picture_filename = save_profile_picture(form.profile_picture.data) if form.profile_picture.data else None

            # Generate verification token
            verification_token = str(uuid.uuid4())

            # Retrieve the selected city’s details (name, latitude, longitude)
            with open('C:/Users/63963/Desktop/online_consultation/city.json', 'r') as f:
                cities_data = json.load(f)

            # Retrieve the selected city ID from the form
            city_id = form.city.data  # This should be an ID (integer)
            print(f"Selected City ID from form: {city_id}")  # Debug log

            # Find the city object from cities_data based on the selected city ID
            city_data = next((city for city in cities_data if city["id"] == city_id), None)

            if city_data:
                city_name = city_data["city"]
                latitude = city_data["latitude"]
                longitude = city_data["longitude"]

                print(f"City Name: {city_name}")
                print(f"City Latitude: {latitude}")
                print(f"City Longitude: {longitude}")
            else:
                flash("City not found in the data.", "danger")
                return redirect(url_for("auth.register_patient"))

            # Save new patient
            new_patient = Patient(
                full_name=form.full_name.data,
                email=form.email.data,
                phone=form.phone.data,
                dob=dob_obj,
                gender=form.gender.data,
                country=form.country.data,
                city=city_name,  # Store city name
                latitude=latitude,  # Latitude from city
                longitude=longitude,  # Longitude from city
                blood_type=form.blood_type.data,
                existing_conditions=form.existing_conditions.data.strip() or "N/A",
                current_medication=form.current_medication.data.strip() or "N/A",
                past_surgeries=form.past_surgeries.data.strip() or "N/A",
                emergency_contact_name=form.emergency_contact_name.data,
                emergency_contact_phone=form.emergency_contact_phone.data,
                preferred_language=form.preferred_language.data,
                profile_picture=profile_picture_filename,
                password_hash=generate_password_hash(form.password.data),
                email_verified=False,  # Email is initially unverified
                verification_token=verification_token  # Store token for email verification
            )

            # Add the new patient to the database
            db.session.add(new_patient)
            db.session.commit()

            # Send verification email
            send_verification_email(new_patient.email, new_patient)

            flash("Registration successful! Please check your email for verification.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()  # Prevent bad entries in DB
            flash("An error occurred during registration. Please try again.", "danger")
            print(f"Error during registration: {e}")  # Debugging log for errors

    return render_template("register_patient.html", form=form)






@auth.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    form = DoctorRegistrationForm()

    if request.method == "POST":
        print("Form POST request received.")
        print("Form data:", request.form)
        print("Files:", request.files)

    if form.validate_on_submit():
        print("Form validated successfully!")


        # ⬇️ Blur check BEFORE saving files
        if is_blurry(form.license_front.data):
            flash("Front license image is too blurry. Please upload a clearer version.", "danger")
            print("✅ Front license image detected as blurry.")
            return redirect(request.url)

        if is_blurry(form.license_back.data):
            flash("Back license image is too blurry. Please upload a clearer version.", "danger")
            print("✅ Back license image detected as blurry.")
            return redirect(request.url)

        if is_blurry(form.board_cert.data):
            flash("Board certificate image is too blurry. Please upload a clearer version.", "danger")
            print("✅ Board cert image detected as blurry.")
            return redirect(request.url)

        existing_doctor = Doctor.query.filter_by(email=form.email.data).first()
        if existing_doctor:
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register_doctor"))

        try:
            dob_obj = datetime.strptime(form.dob.data, "%Y-%m-%d").date()
            verification_token = str(uuid.uuid4())

            # Save files
            profile_picture_filename = save_profile_picture(request.files.get("profile_picture"))

            license_front_filename = save_license_file(request.files.get("license_front"))
            license_back_filename = save_license_file(request.files.get("license_back"))
            board_cert_filename = save_license_file(request.files.get("board_cert"))

            # Load clinic data
            with open(os.path.join(current_app.root_path, 'clinics.json'), 'r') as f:
                clinics_data = json.load(f)

            clinic_id = str(form.hospital_clinic.data)
            clinic_data = next((c for c in clinics_data if c["id"] == clinic_id), None)

            clinic_name = clinic_data["name"] if clinic_data else None
            clinic_latitude = clinic_data["latitude"] if clinic_data else None
            clinic_longitude = clinic_data["longitude"] if clinic_data else None

            new_doctor = Doctor(
                full_name=form.full_name.data,
                email=form.email.data,
                phone=form.phone.data,
                dob=dob_obj,
                gender=form.gender.data,
                country=form.country.data,
                city=form.city.data,
                medical_license=form.medical_license.data,
                specialization=form.specialization.data,
                experience=form.experience.data,
                qualifications=form.qualifications.data,
                hospital_clinic=clinic_name,
                availability=form.availability.data,
                profile_picture=profile_picture_filename,
                license_front=license_front_filename,
                license_back=license_back_filename,
                board_cert=board_cert_filename,
                short_bio=form.short_bio.data,
                linkedin=form.linkedin.data,
                password_hash=generate_password_hash(form.password.data),
                email_verified=False,
                is_approved=False,
                verification_token=verification_token,
                clinic_latitude=clinic_latitude,
                clinic_longitude=clinic_longitude
            )

            db.session.add(new_doctor)
            db.session.commit()

            send_verification_email(new_doctor.email, new_doctor)

            flash("Registration successful! Please check your email for verification.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash("An error occurred during registration. Please try again.", "danger")

    else:
        if request.method == "POST":
            print("Form failed to validate!")
            print("Errors:", form.errors)

    return render_template("register_doctor.html", form=form)






#==================REGISTRATION DOCTOR UP====================


@auth.route("/verify/<token>")
def verify_account(token):
    # Check if token belongs to a patient
    patient = Patient.query.filter_by(verification_token=token).first()
    doctor = Doctor.query.filter_by(verification_token=token).first()  # ✅ Check for doctors too

    if not patient and not doctor:
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for("auth.login"))

    # ✅ If a patient is found, verify them
    if patient:
        if patient.email_verified:
            flash("Your email is already verified. You can log in now.", "info")
        else:
            patient.email_verified = True
            patient.verification_token = None
            db.session.commit()
            flash("Patient email verified successfully! You can now log in.", "success")

    # ✅ If a doctor is found, verify them
    elif doctor:
        if doctor.email_verified:
            flash("Your email is already verified. You can log in now.", "info")
        else:
            doctor.email_verified = True
            doctor.verification_token = None
            db.session.commit()
            flash("Doctor email verified successfully! Please wait for admin approval.", "success")

    return redirect(url_for("auth.login"))




@auth.route("/approve_doctor/<int:doctor_id>", methods=["POST"])
def approve_doctor(doctor_id):
    if session.get("user_role") != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("auth.login"))

    doctor = Doctor.query.get_or_404(doctor_id)  # Ensures valid ID or 404 error
    
    if doctor.is_approved:
        flash("Doctor is already approved.", "info")
    elif not doctor.email_verified:  # ✅ Correct attribute check
        flash("Doctor must verify email before approval.", "danger")
    else:
        doctor.is_approved = True
        db.session.commit()
        flash(f"Doctor {doctor.full_name} has been approved!", "success")

    return redirect(url_for("dashboard.admin_dashboard"))  # Redirects back to admin panel



# ✅ HELPER FUNCTIONS
def redirect_dashboard():
    role = session.get("user_role")
    if role == "admin":
        return redirect(url_for("dashboard.admin_dashboard"))
    elif role == "doctor":
        return redirect(url_for("dashboard.doctor_dashboard"))
    elif role == "patient":
        return redirect(url_for("dashboard.patient_dashboard"))
    return redirect(url_for("auth.login"))


#=============FILE UPLOADS =====================================================

def save_profile_picture(profile_picture):
    if profile_picture:
        filename = secure_filename(profile_picture.filename)
        profile_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        profile_picture.save(profile_path)
        return filename
    return None



#====================================================================================



@auth.route("/request_password_reset", methods=["POST", "GET"])
def request_password_reset():
    if request.method == "POST":
        email = request.form.get('email')
        user = Patient.query.filter_by(email=email).first() or Doctor.query.filter_by(email=email).first()
        if not user:
            flash("Email not found.", "danger")
            return redirect(url_for('auth.login'))
        
        reset_code = generate_reset_code()
        RESET_CODES[reset_code] = {"user_id": user.id, "role": "patient" if isinstance(user, Patient) else "doctor"}
        send_email(email, "Password Reset Code", f"Use this code to reset your password: {reset_code}")
        
        flash("A password reset code has been sent to your email.", "info")
        return redirect(url_for('auth.reset_password'))  # ✅ Redirect to reset password page
    
    return render_template("request_password_reset.html")  # ✅ Renders the correct template




@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        reset_code = request.form.get("reset_code")
        new_password = request.form.get("password")

        print(f"[DEBUG] Received Reset Code: {reset_code}")  # ✅ Debug: Print received reset code

        if not reset_code or reset_code not in RESET_CODES:
            flash("Invalid reset code.", "danger")
            print("[ERROR] Invalid or expired reset code.")  # ✅ Debug: Print error
            return redirect(url_for("auth.reset_password"))

        user_id = RESET_CODES[reset_code]["user_id"]
        role = RESET_CODES[reset_code]["role"]
        print(f"[DEBUG] User ID: {user_id}, Role: {role}")  # ✅ Debug: Print user ID and role

        user = Patient.query.get(user_id) if role == "patient" else Doctor.query.get(user_id)

        if not user:
            flash("User not found.", "danger")
            print("[ERROR] No user found with given ID.")  # ✅ Debug: Print error
            return redirect(url_for("auth.login"))

        # ✅ Debugging: Print password hash before update
        print(f"[DEBUG] Before update - {role.capitalize()} Password Hash: {user.password_hash}")

        # ✅ Update password
        user.set_password(new_password)  # Ensure correct hashing
        db.session.add(user)  # Force SQLAlchemy to detect changes
        db.session.commit()

        # ✅ Debugging: Print password hash after update
        print(f"[DEBUG] After update - {role.capitalize()} Password Hash: {user.password_hash}")

        # ✅ Double-check in the database
        user_check = Patient.query.get(user_id) if role == "patient" else Doctor.query.get(user_id)
        print(f"[DEBUG] Database Check - {role.capitalize()} Password Hash: {user_check.password_hash}")

        # ✅ Remove the used reset code
        del RESET_CODES[reset_code]

        flash("Password reset successfully. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")


