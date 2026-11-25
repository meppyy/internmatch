import os
from io import BytesIO

from werkzeug.datastructures import FileStorage

from app import create_app
from app.services.storage import (
    save_resume_file,
    read_resume_file,
    delete_resume_file,
    copy_resume_file
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

def test_local_resume_copy_is_independent(tmp_path):
    app = create_app({
        "TESTING": True,
        "STORAGE_BACKEND": "local",
        "UPLOAD_FOLDER": str(tmp_path)
    })

    with app.app_context():
        content = b"original resume document"

        uploaded_file = FileStorage(
            stream=BytesIO(content),
            filename="student_resume.pdf",
            content_type="application/pdf"
        )

        original_path = save_resume_file(
            uploaded_file,
            student_id=42,
            original_filename="student_resume.pdf"
        )

        copied_path = copy_resume_file(
            original_path,
            student_id=42,
            original_filename="student_resume.pdf"
        )

        assert copied_path != original_path
        assert os.path.isfile(copied_path)
        assert read_resume_file(copied_path) == content

        # Deleting the original must not affect the copy.
        delete_resume_file(original_path)

        assert not os.path.exists(original_path)
        assert os.path.exists(copied_path)
        assert read_resume_file(copied_path) == content

def test_supabase_resume_copy_is_independent(monkeypatch):
    from app.services import storage as storage_service

    class FakeBucket:
        def __init__(self):
            self.files = {}

        def upload(self, path, file, file_options):
            self.files[path] = file

        def download(self, path):
            return self.files[path]

        def remove(self, paths):
            for path in paths:
                self.files.pop(path, None)

    class FakeStorage:
        def __init__(self, bucket):
            self.bucket = bucket

        def from_(self, bucket_name):
            assert bucket_name == "internmatch-resumes"
            return self.bucket

    class FakeClient:
        def __init__(self, bucket):
            self.storage = FakeStorage(bucket)

    bucket = FakeBucket()

    monkeypatch.setattr(
        storage_service,
        "create_client",
        lambda url, key: FakeClient(bucket)
    )

    app = create_app({
        "TESTING": True,
        "STORAGE_BACKEND": "supabase",
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_SECRET_KEY": "test-secret",
        "SUPABASE_STORAGE_BUCKET": "internmatch-resumes"
    })

    content = b"original cloud resume"

    with app.app_context():
        uploaded_file = FileStorage(
            stream=BytesIO(content),
            filename="student_resume.pdf",
            content_type="application/pdf"
        )

        original_path = save_resume_file(
            uploaded_file,
            student_id=42,
            original_filename="student_resume.pdf"
        )

        copied_path = copy_resume_file(
            original_path,
            student_id=42,
            original_filename="student_resume.pdf"
        )

        assert original_path.startswith("supabase://")
        assert copied_path.startswith("supabase://")
        assert copied_path != original_path

        # Database paths include the Supabase prefix.
        # Bucket keys contain only the actual object paths.
        original_object_path = original_path[
            len(storage_service.SUPABASE_PATH_PREFIX):
        ]

        copied_object_path = copied_path[
            len(storage_service.SUPABASE_PATH_PREFIX):
        ]

        assert original_object_path in bucket.files
        assert copied_object_path in bucket.files

        assert len(bucket.files) == 2
        assert read_resume_file(copied_path) == content

        # Deleting the original must not affect the snapshot copy.
        delete_resume_file(original_path)

        assert original_object_path not in bucket.files
        assert copied_object_path in bucket.files
        assert read_resume_file(copied_path) == content