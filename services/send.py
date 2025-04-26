from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Flask-Mail
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

@app.route("/send_email")
def send_email():
    try:
        msg = Message(
            "Test Email from Flask", 
            sender=app.config["MAIL_USERNAME"], 
            recipients=["arjay.bacudio223x@gmail.com"]  # Change this to your recipient email
        )
        msg.body = "This is a test email sent from a Flask app."
        mail.send(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

if __name__ == "__main__":
    app.run(debug=True)