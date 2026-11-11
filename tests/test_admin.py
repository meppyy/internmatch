import pytest

from app import create_app
from app.extensions import db
from app.models import (
    User,
    StudentProfile,
    RecruiterProfile,
    Internship,
    Application
)
from werkzeug.security import generate_password_hash


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


def create_user(name, email, role):
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash("TestPassword123"),
        role=role
    )

    db.session.add(user)
    db.session.flush()

    return user


def login_as(client, email):
    return client.post(
        "/auth/login",
        data={
            "email": email,
            "password": "TestPassword123"
        },
        follow_redirects=False
    )


def test_admin_dashboard_requires_login(client):
    response = client.get("/admin/dashboard")

    assert response.status_code == 302


def test_admin_can_view_platform_overview(client, app):
    with app.app_context():
        admin = create_user(
            "Platform Admin",
            "admin@test.com",
            "admin"
        )

        student = create_user(
            "Test Student",
            "student-admin@test.com",
            "student"
        )

        student_profile = StudentProfile(
            user_id=student.user_id
        )
        db.session.add(student_profile)

        recruiter = create_user(
            "Test Recruiter",
            "recruiter-admin@test.com",
            "recruiter"
        )

        recruiter_profile = RecruiterProfile(
            user_id=recruiter.user_id,
            company_name="Test Company"
        )
        db.session.add(recruiter_profile)
        db.session.flush()

        active_internship = Internship(
            recruiter_id=recruiter_profile.recruiter_id,
            title="Active Internship",
            company_name="Test Company",
            status="Active"
        )

        draft_internship = Internship(
            recruiter_id=recruiter_profile.recruiter_id,
            title="Draft Internship",
            company_name="Test Company",
            status="Draft"
        )

        db.session.add_all([
            active_internship,
            draft_internship
        ])
        db.session.flush()

        application = Application(
            student_id=student_profile.student_id,
            internship_id=active_internship.internship_id,
            status="Applied"
        )

        db.session.add(application)
        db.session.commit()

    login_as(client, "admin@test.com")

    response = client.get("/admin/dashboard")

    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data

    assert b"Total Users" in response.data
    assert b"3" in response.data

    assert b"Total Students" in response.data
    assert b"Total Recruiters" in response.data
    assert b"Total Internships" in response.data
    assert b"Active Internships" in response.data
    assert b"Total Applications" in response.data


@pytest.mark.parametrize("role", ["student", "recruiter"])
def test_non_admin_cannot_access_admin_dashboard(
    client, app, role
):
    with app.app_context():
        create_user(
            f"Test {role.title()}",
            f"{role}-blocked@test.com",
            role
        )
        db.session.commit()

    login_response = login_as(
        client,
        f"{role}-blocked@test.com"
    )

    assert login_response.status_code == 302

    response = client.get("/admin/dashboard")

    assert response.status_code == 403