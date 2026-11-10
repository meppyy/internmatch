import pytest

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db

from app.models import (
    User, RecruiterProfile, StudentProfile,
    Internship, Application, Resume
)


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


def create_user(
    session,
    name="Test User",
    email="test@example.com",
    password="TestPassword123",
    role="student",
):
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )

    session.add(user)
    session.commit()

    return user


def login(client, email, password):
    return client.post(
        "/auth/login",
        data={
            "email": email,
            "password": password,
        },
        follow_redirects=False,
    )


def test_recruiter_dashboard_requires_login(client):
    response = client.get(
        "/recruiter/dashboard",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_recruiter_can_access_dashboard(client, app):
    with app.app_context():
        recruiter = create_user(
            db.session,
            name="Test Recruiter",
            email="recruiter@test.com",
            password="TestPassword123",
            role="recruiter",
        )

        db.session.add(
            RecruiterProfile(
                user_id=recruiter.user_id,
                company_name="Test Company",
            )
        )
        db.session.commit()

    login(
        client,
        "recruiter@test.com",
        "TestPassword123",
    )

    response = client.get("/recruiter/dashboard")

    assert response.status_code == 200
    assert b"Recruiter Dashboard" in response.data
    assert b"Test Recruiter" in response.data


def test_student_cannot_access_recruiter_dashboard(client, app):
    with app.app_context():
        create_user(
            db.session,
            name="Test Student",
            email="student@test.com",
            password="TestPassword123",
            role="student",
        )

    login(
        client,
        "student@test.com",
        "TestPassword123",
    )

    response = client.get("/recruiter/dashboard")

    assert response.status_code == 403

def create_recruiter_internship(app, email, title):
    with app.app_context():
        recruiter_user = create_user(
            db.session,
            name="Test Recruiter",
            email=email,
            role="recruiter"
        )

        profile = RecruiterProfile(
            user_id=recruiter_user.user_id,
            company_name="Test Company"
        )
        db.session.add(profile)
        db.session.flush()

        internship = Internship(
            recruiter_id=profile.recruiter_id,
            title=title,
            company_name="Test Company",
            status="Active"
        )
        db.session.add(internship)
        db.session.commit()

        return recruiter_user.email, internship.internship_id

def create_applicant_for_internship(app, internship_id):
    with app.app_context():
        student_user = create_user(
            db.session,
            name="Applicant Name",
            email="applicant@example.com",
            role="student"
        )

        profile = StudentProfile(
            user_id=student_user.user_id,
            phone="9876543210",
            education="B.Sc. Computer Science"
        )
        db.session.add(profile)
        db.session.flush()

        resume = Resume(
            student_id=profile.student_id,
            file_name="applicant_resume.pdf",
            file_path="uploads/applicant_resume.pdf"
        )
        db.session.add(resume)
        db.session.flush()

        application = Application(
            student_id=profile.student_id,
            internship_id=internship_id,
            resume_id=resume.resume_id,
            status="Under Review"
        )
        db.session.add(application)
        db.session.commit()


def test_recruiter_can_view_applicants_for_own_internship(
    client, app
):
    email, internship_id = create_recruiter_internship(
        app,
        "applicant-owner@test.com",
        "Python Developer Internship"
    )

    create_applicant_for_internship(app, internship_id)

    login(client, email, "TestPassword123")

    response = client.get(
        f"/recruiter/internships/{internship_id}/applications"
    )

    assert response.status_code == 200
    assert b"Python Developer Internship" in response.data
    assert b"Applicant Name" in response.data
    assert b"applicant@example.com" in response.data
    assert b"B.Sc. Computer Science" in response.data
    assert b"Under Review" in response.data
    assert b"applicant_resume.pdf" in response.data

    internships_response = client.get("/recruiter/internships")
    assert b"View Applicants" in internships_response.data


def test_recruiter_cannot_view_another_recruiters_applicants(
    client, app
):
    owner_email, _ = create_recruiter_internship(
        app,
        "first-owner@test.com",
        "First Recruiter Internship"
    )

    _, other_internship_id = create_recruiter_internship(
        app,
        "second-owner@test.com",
        "Second Recruiter Internship"
    )

    create_applicant_for_internship(app, other_internship_id)

    login(client, owner_email, "TestPassword123")

    response = client.get(
        f"/recruiter/internships/{other_internship_id}/applications"
    )

    assert response.status_code == 404


def test_recruiter_sees_empty_applicant_list(
    client, app
):
    email, internship_id = create_recruiter_internship(
        app,
        "empty-owner@test.com",
        "Internship Without Applicants"
    )

    login(client, email, "TestPassword123")

    response = client.get(
        f"/recruiter/internships/{internship_id}/applications"
    )

    assert response.status_code == 200
    assert b"No applications have been submitted yet." in response.data