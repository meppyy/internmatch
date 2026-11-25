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

    with app.app_context():
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


def test_admin_can_view_user_directory(client, app):
    with app.app_context():
        admin = create_user(
            "Platform Admin",
            "directory-admin@test.com",
            "admin"
        )

        create_user(
            "Alice Student",
            "alice@test.com",
            "student"
        )

        create_user(
            "Bob Recruiter",
            "bob@test.com",
            "recruiter"
        )

        db.session.commit()

    login_as(client, "directory-admin@test.com")

    response = client.get("/admin/users")

    assert response.status_code == 200
    assert b"User Management" in response.data
    assert b"Alice Student" in response.data
    assert b"alice@test.com" in response.data
    assert b"Student" in response.data
    assert b"Bob Recruiter" in response.data
    assert b"bob@test.com" in response.data
    assert b"Recruiter" in response.data
    assert b"Platform Admin" in response.data

    # Password hashes must never appear in the user directory.
    assert b"password_hash" not in response.data

def test_admin_user_directory_shows_account_status_and_actions(
    client, app
):
    with app.app_context():
        admin = create_user(
            "Platform Admin",
            "ui-admin@test.com",
            "admin"
        )
        admin_id = admin.user_id

        active_student = create_user(
            "Active Student",
            "active-ui@test.com",
            "student"
        )
        active_student_id = active_student.user_id

        disabled_student = create_user(
            "Disabled Student",
            "disabled-ui@test.com",
            "student"
        )
        disabled_student_id = disabled_student.user_id
        disabled_student.is_active = False

        db.session.commit()

    login_as(client, "ui-admin@test.com")

    response = client.get("/admin/users")

    assert response.status_code == 200
    assert b"Account Status" in response.data
    assert b"Active" in response.data
    assert b"Disabled" in response.data
    assert b"Disable Account" in response.data
    assert b"Enable Account" in response.data

    page = response.data.decode()

    # The currently logged-in administrator must not get
    # a self-disable action.
    assert (
        f'action="/admin/users/{admin_id}/status"'
        not in page
    )

    # Both other accounts must have their management endpoints.
    assert (
        f'action="/admin/users/{active_student_id}/status"'
        in page
    )
    assert (
        f'action="/admin/users/{disabled_student_id}/status"'
        in page
    )

def test_admin_can_disable_and_reenable_user_account(
    client, app
):
    with app.app_context():
        admin = create_user(
            "Platform Admin",
            "account-admin@test.com",
            "admin"
        )
        student = create_user(
            "Test Student",
            "account-student@test.com",
            "student"
        )
        student_id = student.user_id
        db.session.commit()

    login_as(client, "account-admin@test.com")

    response = client.post(
        f"/admin/users/{student_id}/status",
        data={"action": "disable"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Account disabled successfully." in response.data

    with app.app_context():
        student = db.session.get(User, student_id)
        assert student.is_active is False
        assert student.session_version == 1

    response = client.post(
        f"/admin/users/{student_id}/status",
        data={"action": "enable"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Account enabled successfully." in response.data

    with app.app_context():
        student = db.session.get(User, student_id)
        assert student.is_active is True
        assert student.session_version == 1

def test_disabled_user_cannot_log_in(client, app):
    with app.app_context():
        student = create_user(
            "Disabled Student",
            "disabled-student@test.com",
            "student"
        )
        student.is_active = False
        db.session.commit()

    response = login_as(
        client,
        "disabled-student@test.com"
    )

    assert response.status_code == 302

    page = client.get(
        "/auth/login",
        follow_redirects=True
    )

    assert b"This account has been disabled." in page.data

def test_disabling_account_invalidates_existing_session(
    app
):
    with app.app_context():
        create_user(
            "Platform Admin",
            "session-admin@test.com",
            "admin"
        )
        student = create_user(
            "Session Student",
            "session-student@test.com",
            "student"
        )
        student_id = student.user_id
        db.session.commit()

    student_client = app.test_client()
    admin_client = app.test_client()

    student_login = login_as(
        student_client, "session-student@test.com"
    )
    admin_login = login_as(
        admin_client, "session-admin@test.com"
    )


    # The student initially has access.
    response = student_client.get(
        "/student/dashboard",
        follow_redirects=False
    )
    assert response.status_code == 200

    # Admin disables the account.
    admin_client.post(
        f"/admin/users/{student_id}/status",
        data={"action": "disable"}
    )

    response = student_client.get(
        "/student/dashboard",
        follow_redirects=False
    )
    assert response.status_code == 302

    # Re-enabling must not restore the old session.
    admin_client.post(
        f"/admin/users/{student_id}/status",
        data={"action": "enable"}
    )

    response = student_client.get(
        "/student/dashboard",
        follow_redirects=False
    )
    assert response.status_code == 302

def test_admin_cannot_disable_own_account(client, app):
    with app.app_context():
        admin = create_user(
            "Platform Admin",
            "self-disable@test.com",
            "admin"
        )
        admin_id = admin.user_id
        db.session.commit()

    login_as(client, "self-disable@test.com")

    response = client.post(
        f"/admin/users/{admin_id}/status",
        data={"action": "disable"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"You cannot disable your own account." in response.data

    with app.app_context():
        admin = db.session.get(User, admin_id)
        assert admin.is_active is True

def test_non_admin_cannot_disable_user_account(
    client, app
):
    with app.app_context():
        create_user(
            "Test Student",
            "nonadmin-account@test.com",
            "student"
        )
        target = create_user(
            "Target Student",
            "target-account@test.com",
            "student"
        )
        target_id = target.user_id
        db.session.commit()

    login_as(client, "nonadmin-account@test.com")

    response = client.post(
        f"/admin/users/{target_id}/status",
        data={"action": "disable"}
    )

    assert response.status_code == 403

    with app.app_context():
        target = db.session.get(User, target_id)
        assert target.is_active is True

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