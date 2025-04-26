from flask import Flask, render_template, redirect, url_for, session, send_from_directory, current_app, g
from models import db
from routes.dashboard import dashboard_bp
from routes.auth import auth
from routes.patient import patient_bp
from routes.doctor import doctor_bp
from config.config import Config
from flask_mail import Mail
from dotenv import load_dotenv
import pymysql
import os
import random

# Load .env variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# ✅ Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)
db.init_app(app)

# ✅ Register Blueprints
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(doctor_bp, url_prefix='/doctor')


# ✅ MySQL Manual Connection Setup for External News DB
def get_db():
    if not hasattr(g, 'db'):
        g.db = pymysql.connect(
            host='127.0.0.1',
            port=3333,
            user='root',
            password='143214sadasd',
            database='data_mining',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# ✅ Home Route (redirects or index)
@app.route("/")
def home():
    if "user_id" in session and "user_role" in session:
        return redirect_dashboard()
    return render_template("index.html")

# ✅ Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
# Serve license files from the licenses subfolder
@app.route('/uploads/licenses/<path:filename>')
def license_file(filename):
    license_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'licenses')
    return send_from_directory(license_folder, filename)
# ✅ Role-based redirection
def redirect_dashboard():
    role = session.get("user_role")
    if role == "admin":
        return redirect(url_for("dashboard.admin_dashboard"))
    elif role == "doctor":
        return redirect(url_for("dashboard.doctor_dashboard"))
    elif role == "patient":
        return redirect(url_for("dashboard.patient_dashboard"))
    return redirect(url_for("auth.login"))


@app.route('/features')
def feature():
    return render_template('feature.html')

@app.route("/medical-news")
def show_medical_news():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM medical_news ORDER BY scraped_at DESC")
        articles = cursor.fetchall()

        if articles:  # Ensure we have articles to sample
            random_articles = random.sample(articles, len(articles))
        else:
            random_articles = []

        cursor.close()  # Close the cursor after use
        return render_template("news.html", articles=random_articles)
    
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return "Error fetching articless", 500

# ✅ Create tables if needed
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001, ssl_context=('cert.pem', 'key.pem'))

