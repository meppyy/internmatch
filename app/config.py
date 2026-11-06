import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    # Use the hosted database URL when available.
    # Otherwise, use the existing local SQLite database.
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql://", 1
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or (
        "sqlite:///" + os.path.join(
            BASE_DIR,
            "instance",
            "internmatch.db"
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Allow the upload directory to be configured by the hosting service.
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(BASE_DIR, "uploads")
    )

    ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx"}