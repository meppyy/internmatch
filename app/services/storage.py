
import mimetypes
import os
from uuid import uuid4

from flask import current_app
from supabase import create_client
from werkzeug.utils import secure_filename


SUPABASE_PATH_PREFIX = "supabase://"


def _get_supabase_bucket():
    """Return the configured private Supabase Storage bucket."""

    client = current_app.extensions.get("supabase_client")

    if client is None:
        supabase_url = current_app.config.get("SUPABASE_URL")
        secret_key = current_app.config.get("SUPABASE_SECRET_KEY")

        if not supabase_url or not secret_key:
            raise RuntimeError(
                "Supabase Storage credentials are not configured."
            )

        client = create_client(supabase_url, secret_key)
        current_app.extensions["supabase_client"] = client

    bucket_name = current_app.config["SUPABASE_STORAGE_BUCKET"]

    return client.storage.from_(bucket_name)


def save_resume_file(file_storage, student_id, original_filename):
    """Save a resume locally or in Supabase Storage."""

    filename = secure_filename(original_filename)

    if not filename:
        raise ValueError("Invalid resume filename.")

    object_path = (
        f"students/{student_id}/{uuid4().hex}_{filename}"
    )

    backend = current_app.config.get(
        "STORAGE_BACKEND", "local"
    ).lower()

    if backend == "supabase":
        content_type = (
            file_storage.mimetype
            or mimetypes.guess_type(filename)[0]
            or "application/octet-stream"
        )

        content = file_storage.read()

        if not content:
            raise ValueError("The uploaded resume is empty.")

        _get_supabase_bucket().upload(
            path=object_path,
            file=content,
            file_options={
                "content-type": content_type,
                "upsert": "false"
            }
        )

        # Store the backend alongside the object path.
        return SUPABASE_PATH_PREFIX + object_path

    if backend == "local":
        destination = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            *object_path.split("/")
        )

        os.makedirs(os.path.dirname(destination), exist_ok=True)
        file_storage.save(destination)

        return destination

    raise ValueError(f"Unsupported storage backend: {backend}")


def read_resume_file(stored_path):
    """Read a resume using the backend recorded in its stored path."""

    if stored_path.startswith(SUPABASE_PATH_PREFIX):
        object_path = stored_path[len(SUPABASE_PATH_PREFIX):]
        return _get_supabase_bucket().download(object_path)

    # Existing local filesystem paths continue working.
    with open(stored_path, "rb") as resume_file:
        return resume_file.read()


def delete_resume_file(stored_path):
    """Delete a resume from the backend recorded in its stored path."""

    if not stored_path:
        return

    if stored_path.startswith(SUPABASE_PATH_PREFIX):
        object_path = stored_path[len(SUPABASE_PATH_PREFIX):]
        _get_supabase_bucket().remove([object_path])
        return

    # Existing local filesystem paths continue working.
    if os.path.isfile(stored_path):
        os.remove(stored_path)
