import os
from io import BytesIO

from werkzeug.datastructures import FileStorage

from app import create_app
from app.services.storage import (
    save_resume_file,
    read_resume_file,
    delete_resume_file
)


def test_local_resume_storage_round_trip(tmp_path):
    app = create_app({
        "TESTING": True,
        "STORAGE_BACKEND": "local",
        "UPLOAD_FOLDER": str(tmp_path)
    })

    with app.app_context():
        uploaded_file = FileStorage(
            stream=BytesIO(b"test resume content"),
            filename="sample_resume.pdf",
            content_type="application/pdf"
        )

        stored_path = save_resume_file(
            uploaded_file,
            student_id=42,
            original_filename=uploaded_file.filename
        )

        assert stored_path.endswith("sample_resume.pdf")
        assert os.path.isfile(stored_path)

        content = read_resume_file(stored_path)

        assert content == b"test resume content"

        delete_resume_file(stored_path)

        assert not os.path.exists(stored_path)