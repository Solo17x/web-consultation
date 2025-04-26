import os
from dotenv import load_dotenv

load_dotenv()

print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))  # Should print your email
print("MAIL_PASSWORD:", os.getenv("MAIL_PASSWORD"))  # Should print app password
