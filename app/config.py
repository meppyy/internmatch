import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    # Use the hosted database URL when available.
    # Otherwise, use the existing local SQLite database.
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql+psycopg://",
                1
            )
        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
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

    # Resume storage configuration
    STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local")

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")

    SUPABASE_STORAGE_BUCKET = os.environ.get(
        "SUPABASE_STORAGE_BUCKET",
        "internmatch-resumes"
    )

    # Match the 10 MB limit configured in Supabase Storage.
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024