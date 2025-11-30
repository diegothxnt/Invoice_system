import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Tesseract OCR
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    # Database
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME = "invoice_system"
    
    # Email - GMAIL
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    
    # API
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    
    # File Upload
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Email del aprobador por defecto
    DEFAULT_APPROVER_EMAIL = "rojas.diego3011@gmail.com"

print("✅ Sistema Gmail configurado")
print(f"📧 Email: {Config.EMAIL_USER}")