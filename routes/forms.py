from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, SelectField, FileField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp
from flask_wtf.file import FileAllowed, FileRequired
from datetime import datetime
from werkzeug.utils import secure_filename
import json


# ✅ Login Form
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")



class PatientRegistrationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", 
                        validators=[
                            DataRequired(), 
                            Regexp(r"^09\d{9}$", message="Phone number must be 11 digits and start with 09")
                        ])
    dob = StringField("Date of Birth (YYYY-MM-DD)", validators=[DataRequired()])
    gender = SelectField("Gender", choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], validators=[DataRequired()])
    country = SelectField("Country", choices=[("Ilocos Norte", "Ilocos Norte")], validators=[DataRequired()])
    
    # City dropdown (dynamically loaded)
    city = SelectField("City", coerce=int, validators=[DataRequired()])
    
    blood_type = SelectField(
            "Blood Type", 
            validators=[Optional()], 
            choices=[
                ('', 'Select Blood Type'),  # Default empty option
                ('A+', 'A+'),
                ('A-', 'A-'),
                ('B+', 'B+'),
                ('B-', 'B-'),
                ('AB+', 'AB+'),
                ('AB-', 'AB-'),
                ('O+', 'O+'),
                ('O-', 'O-')
            ]
        )
    existing_conditions = TextAreaField("Allergies", validators=[Optional()], default="N/A")
    current_medication = TextAreaField("Current Medication", validators=[Optional()], default="N/A")
    past_surgeries = TextAreaField("Past Surgeries", validators=[Optional()], default="N/A")
    emergency_contact_name = StringField("Emergency Contact Name", validators=[DataRequired()])
    emergency_contact_phone = StringField("Emergency Contact Phone", 
                                          validators=[
                                              DataRequired(), 
                                              Regexp(r"^09\d{9}$", message="Emergency contact phone number must be 11 digits and start with 09")
                                          ])

    # ✅ Add Preferred Language Field
    preferred_language = SelectField(
        "Preferred Language",
        choices=[("English", "English"), ("Spanish", "Spanish"), ("French", "French"), ("Tagalog", "Tagalog")],
        validators=[DataRequired()],
    )

    profile_picture = FileField("Profile Picture", validators=[Optional(), FileAllowed(["jpg", "png", "jpeg"])])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Register")

    # Initialize city dropdown and ensure dynamic population of city data
    def __init__(self, *args, **kwargs):
        super(PatientRegistrationForm, self).__init__(*args, **kwargs)

        # Load city data from the JSON file
        with open('C:/Users/63963/Desktop/online_consultation/city.json', 'r') as f:
            cities_data = json.load(f)

        # Populate the SelectField choices with city names and their IDs
        self.city.choices = [(city["id"], city["city"]) for city in cities_data]
        
    # Method to handle file upload securely
    def save_profile_picture(self, file_storage):
        if file_storage:
            filename = secure_filename(file_storage.filename)
            file_storage.save(f'uploads/profile_pics/{filename}')
            return filename
        return None




class DoctorRegistrationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=11)])
    dob = StringField("Date of Birth (YYYY-MM-DD)", validators=[DataRequired()])
    
    # Gender dropdown
    gender = SelectField("Gender", choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], validators=[DataRequired()])

    # Profile picture upload
    profile_picture = FileField("Profile Picture", validators=[Optional(), FileAllowed(["jpg", "png", "jpeg"])])
    
    # Medical and professional details
    medical_license = StringField("Medical License", validators=[DataRequired()])
    specialization = SelectField("Specialization",choices=[("General Medical Doctor", "General Medical Doctor")], validators=[DataRequired()])
    experience = StringField("Years of Experience", validators=[DataRequired()])
    qualifications = SelectField("Qualifications", choices=[
        ("Masteral", "Masteral"),
        ("Doctorate", "Doctorate"),
        ("Other", "Other")  # Option for any other qualification if needed
    ], validators=[DataRequired()])
    
    # Hospital/Clinic dropdown (this will dynamically load from a JSON file or a database)
    hospital_clinic = SelectField("Hospital/Clinic", coerce=int, validators=[DataRequired()])
    
    # Availability
    availability = StringField("Availability Schedule", validators=[DataRequired()])

    # Official document uploads

    license_front = FileField("Medical License (Front)", validators=[
        FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDFs only!')
    ])
    license_back = FileField("Medical License (Back)", validators=[
        FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDFs only!')
    ])
    board_cert = FileField("Board Certificate", validators=[
        FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDFs only!')
    ])



    # Location details
    country = SelectField("Country",choices=[("Ilocos Norte", "Ilocos Norte")], validators=[DataRequired()])
    city = SelectField("City", choices=[
        ("Laoag City", "Laoag City"),
        ("Batac City", "Batac City"),
        ("Adams", "Adams"),
        ("Bacarra", "Bacarra"),
        ("Badoc", "Badoc"),
        ("Bangui", "Bangui"),
        ("Banna", "Banna"),
        ("Burgos", "Burgos"),
        ("Carasi", "Carasi"),
        ("Currimao", "Currimao"),
        ("Dingras", "Dingras"),
        ("Dumalneg", "Dumalneg"),
        ("Marcos", "Marcos"),
        ("Nueva Era", "Nueva Era"),
        ("Pagudpud", "Pagudpud"),
        ("Paoay", "Paoay"),
        ("Pasuquin", "Pasuquin"),
        ("Piddig", "Piddig"),
        ("Pinili", "Pinili"),
        ("San Nicolas", "San Nicolas"),
        ("Sarrat", "Sarrat"),
        ("Solsona", "Solsona"),
        ("Vintar", "Vintar")
    ], validators=[DataRequired()])
    
    # Short bio
    short_bio = TextAreaField("Short Bio", validators=[DataRequired(), Length(min=10, max=500)])
    
    # LinkedIn Profile (optional)
    linkedin = StringField("LinkedIn Profile (Optional)", validators=[Optional()])
    
    # Password and confirm password
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    
    # Submit button
    submit = SubmitField("Register")
    
    # Initialize hospital/clinic dropdown and ensure dynamic population of clinic data
    def __init__(self, *args, **kwargs):
        super(DoctorRegistrationForm, self).__init__(*args, **kwargs)

        # Load clinic data from the JSON file
        with open('C:/Users/63963/Desktop/online_consultation/clinics.json', 'r') as f:
            clinics_data = json.load(f)

        # Populate the SelectField choices with clinic names and their IDs
        self.hospital_clinic.choices = [(clinic["id"], clinic["name"]) for clinic in clinics_data]
        
    # Method to handle file upload securely
    def save_profile_picture(self, file_storage):
        if file_storage:
            filename = secure_filename(file_storage.filename)
            file_storage.save(f'uploads/profile_pics/{filename}')
            return filename
        return None



class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField("Reset Password")
