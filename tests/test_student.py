import pytest
from io import BytesIO

from app import create_app
from app.extensions import db
from app.models import User, StudentProfile
from app.models import Internship, RecruiterProfile, Application, Resume


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def student_user(app):
    user = User(
        name="Test Student",
        email="student@test.com",
        password_hash="test-password",
        role="student"
    )

    db.session.add(user)
    db.session.flush()

    profile = StudentProfile(user_id=user.user_id)

    db.session.add(profile)
    db.session.commit()

    return user


def login_student(client, student_user):
    with client.session_transaction() as session:
        session["_user_id"] = str(student_user.user_id)
        session["_fresh"] = True


def test_student_dashboard_requires_login(client):
    response = client.get("/student/dashboard")

    assert response.status_code == 302


def test_student_profile_requires_login(client):
    response = client.get("/student/profile")

    assert response.status_code == 302

def test_student_can_edit_profile(client, student_user):
    login_student(client, student_user)

    response = client.post(
        "/student/profile/edit",
        data={
            "phone": "9876543210",
            "education": "B.Sc. (Hons) Computer Science",
            "profile_summary": "Software engineering student.",
            "experience": "AI/ML Intern",
            "projects": "InternMatch",
            "certifications": "Python Certification",
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    with client.application.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        assert profile.phone == "9876543210"
        assert profile.education == "B.Sc. (Hons) Computer Science"
        assert profile.profile_summary == "Software engineering student."
        assert profile.experience == "AI/ML Intern"
        assert profile.projects == "InternMatch"
        assert profile.certifications == "Python Certification"

def test_student_can_add_skill(client, student_user):
    login_student(client, student_user)

    response = client.post(
        "/student/skills",
        data={"skill_name": "Python"},
        follow_redirects=True
    )

    assert response.status_code == 200

    with client.application.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        assert len(profile.skills) == 1
        assert profile.skills[0].skill_name == "Python"

def test_student_can_remove_skill(client, student_user):
    login_student(client, student_user)

    client.post(
        "/student/skills",
        data={"skill_name": "Python"},
        follow_redirects=True
    )

    with client.application.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        skill = profile.skills[0]
        skill_id = skill.skill_id

    response = client.post(
        f"/student/skills/remove/{skill_id}",
        follow_redirects=True
    )

    assert response.status_code == 200

    with client.application.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        assert len(profile.skills) == 0

def test_student_can_upload_resume(client, student_user):
    login_student(client, student_user)

    response = client.post(
        "/student/resume/upload",
        data={
            "resume": (
                BytesIO(b"fake pdf content"),
                "test_resume.pdf"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200

    with client.application.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        assert profile.resume is not None
        assert profile.resume.file_name == "test_resume.pdf"

def test_student_cannot_upload_invalid_resume(client, student_user):
    login_student(client, student_user)

    response = client.post(
        "/student/resume/upload",
        data={
            "resume": (
                BytesIO(b"not a resume"),
                "malicious.exe"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert b"Invalid file type" in response.data

    with client.application.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        assert profile.resume is None

def test_student_can_replace_resume(client, student_user):
    login_student(client, student_user)

    first_response = client.post(
        "/student/resume/upload",
        data={
            "resume": (
                BytesIO(b"first resume"),
                "resume_one.pdf"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/student/resume/upload",
        data={
            "resume": (
                BytesIO(b"second resume"),
                "resume_two.pdf"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert second_response.status_code == 200

    with client.application.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        assert profile.resume is not None
        assert profile.resume.file_name == "resume_two.pdf"
        assert profile.resume.file_path.endswith("resume_two.pdf")

def test_student_can_access_resume(client, student_user):
    login_student(client, student_user)

    upload_response = client.post(
        "/student/resume/upload",
        data={
            "resume": (
                BytesIO(b"resume content"),
                "access_test.pdf"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert upload_response.status_code == 200

    response = client.get("/student/resume")

    assert response.status_code == 200
    assert response.data == b"resume content"

def test_student_profile_completion(client, student_user):
    login_student(client, student_user)

    response = client.get("/student/profile/completion")

    assert response.status_code == 200
    assert b"0% Complete" in response.data


def test_student_resume_routes_use_supabase_storage(
    client, student_user, monkeypatch
):
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

    client.application.config.update({
        "STORAGE_BACKEND": "supabase",
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_SECRET_KEY": "test-secret",
        "SUPABASE_STORAGE_BUCKET": "internmatch-resumes"
    })

    login_student(client, student_user)

    # Upload the first resume.
    first_response = client.post(
        "/student/resume/upload",
        data={
            "resume": (
                BytesIO(b"first cloud resume"),
                "first_resume.pdf"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert first_response.status_code == 200
    assert len(bucket.files) == 1

    old_path = next(iter(bucket.files))

    # Replace it with a second resume.
    second_response = client.post(
        "/student/resume/upload",
        data={
            "resume": (
                BytesIO(b"second cloud resume"),
                "second_resume.pdf"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert second_response.status_code == 200
    assert len(bucket.files) == 1
    assert old_path not in bucket.files

    # Verify that the student can view the replacement.
    response = client.get("/student/resume")

    assert response.status_code == 200
    assert response.data == b"second cloud resume"

def test_student_can_browse_active_internships(
    client, student_user, app
):
    with app.app_context():
        recruiter_user = User(
            name="Test Recruiter",
            email="browse-recruiter@test.com",
            password_hash="test-password",
            role="recruiter"
        )

        db.session.add(recruiter_user)
        db.session.flush()

        recruiter = RecruiterProfile(
            user_id=recruiter_user.user_id,
            company_name="Test Company"
        )

        db.session.add(recruiter)
        db.session.flush()

        internships = [
            Internship(
                recruiter_id=recruiter.recruiter_id,
                title="Active Python Internship",
                company_name="Test Company",
                status="Active"
            ),
            Internship(
                recruiter_id=recruiter.recruiter_id,
                title="Draft Python Internship",
                company_name="Test Company",
                status="Draft"
            ),
            Internship(
                recruiter_id=recruiter.recruiter_id,
                title="Closed Python Internship",
                company_name="Test Company",
                status="Closed"
            )
        ]

        db.session.add_all(internships)
        db.session.commit()

    login_student(client, student_user)

    response = client.get("/student/internships")

    assert response.status_code == 200
    assert b"Active Python Internship" in response.data
    assert b"Draft Python Internship" not in response.data
    assert b"Closed Python Internship" not in response.data

def test_student_sees_empty_state_when_no_active_internships(
    client, student_user
):
    login_student(client, student_user)

    response = client.get("/student/internships")

    assert response.status_code == 200
    assert b"No active internships are available right now." in response.data

def create_test_internships(app, email, records):
    with app.app_context():
        recruiter_user = User(
            name="Test Recruiter",
            email=email,
            password_hash="test-password",
            role="recruiter"
        )

        db.session.add(recruiter_user)
        db.session.flush()

        recruiter = RecruiterProfile(
            user_id=recruiter_user.user_id,
            company_name="Test Company"
        )

        db.session.add(recruiter)
        db.session.flush()

        internship_ids = []

        for record in records:
            internship = Internship(
                recruiter_id=recruiter.recruiter_id,
                company_name="Test Company",
                **record
            )

            db.session.add(internship)
            db.session.flush()
            internship_ids.append(internship.internship_id)

        db.session.commit()

        return internship_ids

def test_student_can_search_and_filter_internships(
    client, student_user, app
):
    create_test_internships(
        app,
        "search-recruiter@test.com",
        [
            {
                "title": "Remote Python Internship",
                "description": "Python development",
                "location": "Delhi",
                "work_mode": "Remote",
                "status": "Active"
            },
            {
                "title": "Hybrid Python Internship",
                "description": "Python development",
                "location": "Delhi",
                "work_mode": "Hybrid",
                "status": "Active"
            },
            {
                "title": "Remote Data Analyst",
                "description": "SQL analysis",
                "location": "Mumbai",
                "work_mode": "Remote",
                "status": "Active"
            },
            {
                "title": "Closed Python Internship",
                "description": "Python development",
                "location": "Delhi",
                "work_mode": "Remote",
                "status": "Closed"
            }
        ]
    )

    login_student(client, student_user)

    response = client.get(
        "/student/internships?q=Python&work_mode=Remote"
    )

    assert response.status_code == 200
    assert b"Remote Python Internship" in response.data
    assert b"Hybrid Python Internship" not in response.data
    assert b"Remote Data Analyst" not in response.data
    assert b"Closed Python Internship" not in response.data


def test_student_can_view_active_internship_details(
    client, student_user, app
):
    internship_ids = create_test_internships(
        app,
        "details-recruiter@test.com",
        [
            {
                "title": "Active Detail Internship",
                "description": "Build Flask applications.",
                "location": "Delhi",
                "work_mode": "Remote",
                "status": "Active"
            },
            {
                "title": "Closed Detail Internship",
                "description": "Closed listing",
                "location": "Delhi",
                "work_mode": "Remote",
                "status": "Closed"
            }
        ]
    )

    login_student(client, student_user)

    response = client.get(
        f"/student/internships/{internship_ids[0]}"
    )

    assert response.status_code == 200
    assert b"Active Detail Internship" in response.data
    assert b"Build Flask applications." in response.data

    closed_response = client.get(
        f"/student/internships/{internship_ids[1]}"
    )

    assert closed_response.status_code == 404

def test_student_can_apply_without_resume(client, student_user, app):
    internship_ids = create_test_internships(
        app,
        "apply-no-resume@test.com",
        [{
            "title": "Application Test Internship",
            "status": "Active"
        }]
    )

    internship_id = internship_ids[0]
    login_student(client, student_user)

    response = client.post(
        f"/student/internships/{internship_id}/apply"
    )

    assert response.status_code == 302

    with app.app_context():
        application = Application.query.filter_by(
            student_id=StudentProfile.query.filter_by(
                user_id=student_user.user_id
            ).first().student_id,
            internship_id=internship_id
        ).one()

        assert application.resume_id is None
        assert application.status == "Applied"

def test_student_application_attaches_existing_resume(
    client, student_user, app
):
    internship_ids = create_test_internships(
        app,
        "apply-with-resume@test.com",
        [{
            "title": "Resume Application Internship",
            "status": "Active"
        }]
    )

    with app.app_context():
        profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        resume = Resume(
            student_id=profile.student_id,
            file_name="student_resume.pdf",
            file_path="uploads/student_resume.pdf"
        )

        db.session.add(resume)
        db.session.commit()
        resume_id = resume.resume_id

    login_student(client, student_user)

    response = client.post(
        f"/student/internships/{internship_ids[0]}/apply"
    )

    assert response.status_code == 302

    with app.app_context():
        application = Application.query.filter_by(
            internship_id=internship_ids[0]
        ).one()

        assert application.resume_id == resume_id

def test_student_cannot_apply_twice(
    client, student_user, app
):
    internship_ids = create_test_internships(
        app,
        "apply-duplicate@test.com",
        [{
            "title": "Duplicate Application Internship",
            "status": "Active"
        }]
    )

    login_student(client, student_user)

    url = f"/student/internships/{internship_ids[0]}/apply"

    first_response = client.post(url)
    second_response = client.post(url)

    assert first_response.status_code == 302
    assert second_response.status_code == 302

    with app.app_context():
        student_profile = StudentProfile.query.filter_by(
            user_id=student_user.user_id
        ).first()

        count = Application.query.filter_by(
            student_id=student_profile.student_id,
            internship_id=internship_ids[0]
        ).count()

        assert count == 1