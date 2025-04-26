from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from models import db, Doctor, Patient, Message, VideoCall
from services.communication import get_conversation_history, send_message
from datetime import datetime
from utils.geolocation import calculate_distance
from math import radians, cos, sin, asin, sqrt, atan2
from geopy.distance import geodesic
import socket

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


# ✅ Admin Dashboard
@dashboard_bp.route("/admin")
def admin_dashboard():
    if session.get("user_role") != "admin":
        flash("Unauthorized access. Please log in as an admin.", "danger")
        return redirect(url_for("auth.login"))  # Protect route

    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()

    doctors = Doctor.query.all()
    patients = Patient.query.all()

    return render_template("admin_dashboard.html", 
                           doctors=doctors, 
                           patients=patients, 
                           total_patients=total_patients, 
                           total_doctors=total_doctors)


# ✅ Search Users (Admin)
@dashboard_bp.route('/search_users', methods=['GET'])
def search_users():
    if session.get("user_role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403  # Secure search

    query = request.args.get('query', '').strip()

    doctors = Doctor.query.filter(
        (Doctor.full_name.ilike(f"%{query}%")) | (Doctor.email.ilike(f"%{query}%"))
    ).all()
    patients = Patient.query.filter(
        (Patient.full_name.ilike(f"%{query}%")) | (Patient.email.ilike(f"%{query}%"))
    ).all()

    results = {
        "doctors": [{"id": doc.id, "name": doc.full_name, "email": doc.email} for doc in doctors],
        "patients": [{"id": pat.id, "name": pat.full_name, "email": pat.email} for pat in patients]
    }
    return jsonify(results)


# ✅ View Doctor Profile
@dashboard_bp.route("/view_doctor/<int:doctor_id>")
def view_doctor(doctor_id):
    if session.get("user_role") != "admin":
        flash("Unauthorized access. Only admins can view doctor profiles.", "danger")
        return redirect(url_for("auth.login"))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template("admin/view_doctor.html", doctor=doctor)


# ✅ View Patient Profile
@dashboard_bp.route("/view_patient/<int:patient_id>")
def view_patient(patient_id):
    if session.get("user_role") != "admin":
        flash("Unauthorized access. Only admins can view patient profiles.", "danger")
        return redirect(url_for("auth.login"))
    
    patient = Patient.query.get_or_404(patient_id)
    return render_template("admin/view_patient.html", patient=patient)


# ✅ Approve Doctor (Admin)
@dashboard_bp.route("/approve_doctor/<int:doctor_id>", methods=["POST"])
def approve_doctor(doctor_id):
    if session.get("user_role") != "admin":
        flash("Unauthorized access. Only admins can approve doctors.", "danger")
        return redirect(url_for("auth.login"))

    doctor = Doctor.query.get_or_404(doctor_id)
    
    if doctor.is_approved:
        flash("Doctor is already approved.", "info")
    elif not doctor.email_verified:
        flash("Doctor must verify email before approval.", "danger")
    else:
        doctor.is_approved = True
        db.session.commit()
        flash(f"Doctor {doctor.full_name} has been approved!", "success")

    return redirect(url_for("dashboard.admin_dashboard"))



#----------------------------------------------------------------------------------------
@dashboard_bp.route("/doctor", methods=["GET", "POST"])
def doctor_dashboard():
    if session.get("user_role") != "doctor":
        return redirect(url_for("auth.login"))

    if "user_id" not in session:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    doctor_id = session.get("user_id")
    doctor_name = session.get("doctor_name", "Doctor")
    patients = Patient.query.all()
    conversation_history = []

    patient_id = request.args.get('patient_id')
    if patient_id:
        conversation_history = get_conversation_history(doctor_id, int(patient_id), 'doctor', 'patient')

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        message_content = request.form.get("message")

        if doctor_id and patient_id and message_content:
            send_message(doctor_id, int(patient_id), message_content, 'doctor', 'patient')
            return redirect(url_for("dashboard.doctor_dashboard", patient_id=patient_id))
        else:
            flash("Please ensure all fields are filled out.", "warning")

    return render_template("doctor_dashboard.html", doctor_name=doctor_name, patients=patients, 
                           conversation_history=conversation_history, doctor_id=doctor_id)



# Haversine Formula
def haversine(lat1, lon1, lat2, lon2):
    # Earth radius in kilometers (mean radius)
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return distance

# Geopy Geodesic Formula (more accurate for larger distances)
def geopy_distance(lat1, lon1, lat2, lon2):
    # Using geopy's geodesic method for accurate distance calculation
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

@dashboard_bp.route("/patient", methods=["GET", "POST"])
def patient_dashboard():
    if session.get("user_role") != "patient":
        return redirect(url_for("auth.login"))

    if "user_id" not in session:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    # Get patient ID and name from session
    patient_id = session.get("user_id")
    patient_name = session.get("patient_name", "Patient")

    # Retrieve the patient's information and location
    patient = Patient.query.get(patient_id)
    if patient is None:
        flash("Patient not found. Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    patient_lat, patient_lon = patient.latitude, patient.longitude

    # Get all doctors and calculate distances from patient
    all_doctors = Doctor.query.all()
    doctors_with_distance = []

    if patient_lat is not None and patient_lon is not None:
        for doc in all_doctors:
            if doc.clinic_latitude is not None and doc.clinic_longitude is not None:
                # Use geopy for distance calculation, you can also use haversine if preferred
                distance = geopy_distance(patient_lat, patient_lon, doc.clinic_latitude, doc.clinic_longitude)
            else:
                distance = float('inf')  # For doctors without coordinates, set distance to infinity

            doctors_with_distance.append({
                'id': doc.id,
                'full_name': doc.full_name,
                'hospital_clinic': doc.hospital_clinic,  # Add hospital/clinic name here
                'active': doc.active,
                'distance': round(distance, 2)  # Round for cleaner output
            })

        # Sort doctors by distance (nearest first)
        doctors_with_distance.sort(key=lambda d: d['distance'])
    else:
        # If patient has no location, list doctors without distance
        doctors_with_distance = [{
            'id': doc.id,
            'full_name': doc.full_name,
            'hospital_clinic': doc.hospital_clinic,  # Add hospital/clinic name here
            'active': doc.active,
            'distance': None
        } for doc in all_doctors]

    # Handle conversation history with selected doctor
    conversation_history = []
    doctor_id = request.args.get('doctor_id')
    if doctor_id:
        conversation_history = get_conversation_history(patient_id, int(doctor_id), 'patient', 'doctor')

    # Handle message sending
    if request.method == "POST":
        doctor_id = request.form.get("doctor_id")
        message_content = request.form.get("message")

        if patient_id and doctor_id and message_content:
            send_message(patient_id, int(doctor_id), message_content, 'patient', 'doctor')
            return redirect(url_for("dashboard.patient_dashboard", doctor_id=doctor_id))
        else:
            flash("Please ensure all fields are filled out.", "warning")

    return render_template(
        "patient_dashboard.html",
        patient_name=patient_name,
        doctors=doctors_with_distance,
        conversation_history=conversation_history,
        patient_id=patient_id
    )


@dashboard_bp.route('/view_doctor_patient/<int:doctor_id>')
def view_doctor_patient(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('patient/view_doctor.html', doctor=doctor)


@dashboard_bp.route('/view_patient_doctor/<int:patient_id>')
def view_patient_doctor(patient_id):
    # Fetch patient details from the database
    patient = Patient.query.get_or_404(patient_id)
    # Pass patient data to the template
    return render_template('doctor/view_patient.html', patient=patient)




@dashboard_bp.route("/meeting", methods=["GET", "POST"])
def meeting():
    doctor_name = session.get("doctor_name", "Doctor")
    room_id = request.args.get("roomID")

    print(f"[MEETING PAGE] Doctor name: {doctor_name}")
    print(f"[MEETING PAGE] Room ID from query string: {room_id}")

    return render_template("meeting.html", doctor_name=doctor_name, room_id=room_id)


@dashboard_bp.route("/join", methods=["GET", "POST"])
def join_meeting():
    local_ip = socket.gethostbyname(socket.gethostname())
    external_ip = "0.0.0.0"

    print(f"[JOIN PAGE] Local IP: {local_ip}")
    print(f"[JOIN PAGE] External IP placeholder: {external_ip}")

    if request.method == "POST":
        room_id = request.form.get("roomID")
        print(f"[JOIN PAGE] POST request received. Room ID: {room_id}")
        
        redirect_url = f"https://192.168.1.21:5001/dashboard/meeting?roomID={room_id}"
        print(f"[JOIN PAGE] Redirecting to: {redirect_url}")
        
        return redirect(redirect_url)

    print("[JOIN PAGE] Rendering join_meeting.html template")
    return render_template("join_meeting.html")

