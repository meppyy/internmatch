import pytest
from io import BytesIO

from app import create_app
from app.extensions import db
from app.models import User, StudentProfile


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
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