import pytest

from app import create_app
from app.extensions import db
from app.models import (
    User,
    StudentProfile,
    RecruiterProfile,
    Internship,
    Application,
    Resume
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

def create_recruiter_internship(
    email, title, status="Draft"
):
    recruiter_user = create_user(
        title + " Recruiter",
        email,
        "recruiter"
    )

    profile = RecruiterProfile(
        user_id=recruiter_user.user_id,
        company_name=title + " Company"
    )
    db.session.add(profile)
    db.session.flush()

    internship = Internship(
        recruiter_id=profile.recruiter_id,
        title=title,
        company_name=profile.company_name,
        status=status
    )

    db.session.add(internship)
    db.session.commit()

    return internship.internship_id

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

def test_admin_can_delete_disabled_student_and_resume(
    client, app, tmp_path
):
    with app.app_context():
        create_user(
            "Platform Admin", "delete-admin@test.com", "admin"
        )

        student = create_user(
            "Student To Delete", "delete-student@test.com", "student"
        )
        student_id = student.user_id
        student.is_active = False

        profile = StudentProfile(user_id=student_id)
        db.session.add(profile)
        db.session.flush()

        resume_path = tmp_path / "student_resume.pdf"
        resume_path.write_bytes(b"test resume")

        resume = Resume(
            student_id=profile.student_id,
            file_name="student_resume.pdf",
            file_path=str(resume_path)
        )
        db.session.add(resume)
        db.session.commit()

    login_as(client, "delete-admin@test.com")

    delete_url = f"/admin/users/{student_id}/delete"

    assert client.get(delete_url).status_code == 405

    response = client.post(
        delete_url,
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Account deleted successfully." in response.data
    assert not resume_path.exists()

    with app.app_context():
        assert db.session.get(User, student_id) is None
        assert StudentProfile.query.filter_by(
            user_id=student_id
        ).first() is None
        assert Resume.query.filter_by(
            student_id=student_id
        ).first() is None

def test_admin_cannot_delete_student_with_applications(
    client, app, tmp_path
):
    with app.app_context():
        create_user(
            "Platform Admin", "history-admin@test.com", "admin"
        )

        student_user = create_user(
            "Student With History",
            "history-student@test.com",
            "student"
        )
        student_user.is_active = False

        recruiter_user = create_user(
            "Recruiter", "history-recruiter@test.com", "recruiter"
        )

        student = StudentProfile(user_id=student_user.user_id)
        recruiter = RecruiterProfile(
            user_id=recruiter_user.user_id,
            company_name="History Company"
        )

        db.session.add_all([student, recruiter])
        db.session.flush()

        internship = Internship(
            recruiter_id=recruiter.recruiter_id,
            title="Historical Internship",
            company_name="History Company",
            status="Closed"
        )
        db.session.add(internship)
        db.session.flush()

        resume_path = tmp_path / "protected_resume.pdf"
        resume_path.write_bytes(b"protected resume")

        resume = Resume(
            student_id=student.student_id,
            file_name="protected_resume.pdf",
            file_path=str(resume_path)
        )
        db.session.add(resume)
        db.session.flush()

        application = Application(
            student_id=student.student_id,
            internship_id=internship.internship_id,
            resume_id=resume.resume_id,
            status="Rejected"
        )
        db.session.add(application)
        db.session.commit()

        application_id = application.application_id
        student_id = student_user.user_id

    login_as(client, "history-admin@test.com")

    response = client.post(
        f"/admin/users/{student_id}/delete",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert (
        b"This student has application history and cannot be deleted."
        in response.data
    )

    with app.app_context():
        assert db.session.get(User, student_id) is not None
        assert db.session.get(
            Application, application_id
        ) is not None
        assert resume_path.exists()

def test_admin_cannot_delete_recruiter_with_internships(
    client, app
):
    with app.app_context():
        create_user(
            "Platform Admin", "listing-admin@test.com", "admin"
        )

        recruiter_user = create_user(
            "Recruiter With Listings",
            "listing-recruiter@test.com",
            "recruiter"
        )
        recruiter_user.is_active = False

        profile = RecruiterProfile(
            user_id=recruiter_user.user_id,
            company_name="Protected Company"
        )
        db.session.add(profile)
        db.session.flush()

        internship = Internship(
            recruiter_id=profile.recruiter_id,
            title="Protected Internship",
            company_name="Protected Company",
            status="Closed"
        )
        db.session.add(internship)
        db.session.commit()

        recruiter_id = recruiter_user.user_id
        internship_id = internship.internship_id

    login_as(client, "listing-admin@test.com")

    response = client.post(
        f"/admin/users/{recruiter_id}/delete",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert (
        b"This recruiter has internship listings and cannot be deleted."
        in response.data
    )

    with app.app_context():
        assert db.session.get(User, recruiter_id) is not None
        assert db.session.get(Internship, internship_id) is not None

def test_admin_cannot_delete_active_user_account(
    client, app
):
    with app.app_context():
        create_user(
            "Platform Admin", "active-delete-admin@test.com", "admin"
        )
        student = create_user(
            "Active Student",
            "active-delete-student@test.com",
            "student"
        )
        student_id = student.user_id
        db.session.commit()

    login_as(client, "active-delete-admin@test.com")

    response = client.post(
        f"/admin/users/{student_id}/delete",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Disable the account before deleting it." in response.data

    with app.app_context():
        assert db.session.get(User, student_id) is not None

def test_admin_cannot_delete_own_account(client, app):
    with app.app_context():
        admin = create_user(
            "Platform Admin", "self-delete@test.com", "admin"
        )
        admin_id = admin.user_id
        db.session.commit()

    login_as(client, "self-delete@test.com")

    response = client.post(
        f"/admin/users/{admin_id}/delete",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"You cannot delete your own account." in response.data

    with app.app_context():
        assert db.session.get(User, admin_id) is not None


def test_non_admin_cannot_delete_user_account(client, app):
    with app.app_context():
        student = create_user(
            "Student", "delete-blocked@test.com", "student"
        )
        target = create_user(
            "Target", "delete-target@test.com", "student"
        )
        target.is_active = False
        target_id = target.user_id
        db.session.commit()

    login_as(client, "delete-blocked@test.com")

    response = client.post(
        f"/admin/users/{target_id}/delete"
    )

    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(User, target_id) is not None

def test_admin_can_delete_disabled_admin_while_another_active_admin_remains(
    client, app
):
    with app.app_context():
        active_admin = create_user(
            "Active Admin",
            "remaining-admin@test.com",
            "admin"
        )
        active_admin_id = active_admin.user_id

        disabled_admin = create_user(
            "Disabled Admin",
            "disabled-admin@test.com",
            "admin"
        )
        disabled_admin_id = disabled_admin.user_id
        disabled_admin.is_active = False

        db.session.commit()

    login_as(client, "remaining-admin@test.com")

    response = client.post(
        f"/admin/users/{disabled_admin_id}/delete",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Account deleted successfully." in response.data

    with app.app_context():
        assert db.session.get(User, disabled_admin_id) is None

        remaining = db.session.get(User, active_admin_id)
        assert remaining is not None
        assert remaining.is_active is True

        assert User.query.filter_by(
            role="admin",
            is_active=True
        ).count() == 1

def test_admin_user_directory_shows_delete_action_only_for_disabled_accounts(
    client, app
):
    with app.app_context():
        admin = create_user(
            "Platform Admin",
            "delete-ui-admin@test.com",
            "admin"
        )
        admin_id = admin.user_id

        active_student = create_user(
            "Active Student",
            "delete-ui-active@test.com",
            "student"
        )
        active_id = active_student.user_id

        disabled_student = create_user(
            "Disabled Student",
            "delete-ui-disabled@test.com",
            "student"
        )
        disabled_id = disabled_student.user_id
        disabled_student.is_active = False

        db.session.commit()

    login_as(client, "delete-ui-admin@test.com")

    response = client.get("/admin/users")

    assert response.status_code == 200

    page = response.data.decode()

    assert "Delete Account" in page

    assert (
        f'action="/admin/users/{disabled_id}/delete"'
        in page
    )

    assert (
        f'action="/admin/users/{active_id}/delete"'
        not in page
    )

    assert (
        f'action="/admin/users/{admin_id}/delete"'
        not in page
    )

def test_admin_can_view_all_platform_internships(
    client, app
):
    with app.app_context():
        create_user(
            "Platform Admin", "global-admin@test.com", "admin"
        )

        first_id = create_recruiter_internship(
            "global-recruiter-1@test.com",
            "First Recruiter Internship",
            "Active"
        )

        second_id = create_recruiter_internship(
            "global-recruiter-2@test.com",
            "Second Recruiter Internship",
            "Draft"
        )

    login_as(client, "global-admin@test.com")

    response = client.get("/admin/internships")

    assert response.status_code == 200
    assert b"Internship Management" in response.data
    assert b"First Recruiter Internship" in response.data
    assert b"Second Recruiter Internship" in response.data

    with app.app_context():
        assert db.session.get(Internship, first_id) is not None
        assert db.session.get(Internship, second_id) is not None

def test_admin_can_update_any_internship_status(
    client, app
):
    with app.app_context():
        create_user(
            "Platform Admin", "global-status-admin@test.com", "admin"
        )

        internship_id = create_recruiter_internship(
            "global-status-recruiter@test.com",
            "Recruiter Owned Internship",
            "Draft"
        )

    login_as(client, "global-status-admin@test.com")

    response = client.post(
        f"/admin/internships/{internship_id}/status",
        data={"status": "Active"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Internship status updated successfully." in response.data

    with app.app_context():
        internship = db.session.get(Internship, internship_id)
        assert internship.status == "Active"

        # Administrative management must not change ownership.
        recruiter = RecruiterProfile.query.get(
            internship.recruiter_id
        )
        assert recruiter.company_name == "Recruiter Owned Internship Company"

def test_admin_cannot_set_invalid_internship_status(
    client, app
):
    with app.app_context():
        create_user(
            "Platform Admin", "invalid-status-admin@test.com", "admin"
        )

        internship_id = create_recruiter_internship(
            "invalid-status-recruiter@test.com",
            "Protected Status Internship",
            "Draft"
        )

    login_as(client, "invalid-status-admin@test.com")

    response = client.post(
        f"/admin/internships/{internship_id}/status",
        data={"status": "Invalid Status"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Invalid internship status." in response.data

    with app.app_context():
        internship = db.session.get(Internship, internship_id)
        assert internship.status == "Draft"

def test_admin_can_delete_internship_without_applications(
    client, app
):
    with app.app_context():
        create_user(
            "Platform Admin", "delete-listing-admin@test.com", "admin"
        )

        internship_id = create_recruiter_internship(
            "delete-listing-recruiter@test.com",
            "Deletable Admin Internship",
            "Draft"
        )

    login_as(client, "delete-listing-admin@test.com")

    delete_url = f"/admin/internships/{internship_id}/delete"

    assert client.get(delete_url).status_code == 405

    response = client.post(
        delete_url,
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Internship deleted successfully." in response.data

    with app.app_context():
        assert db.session.get(Internship, internship_id) is None

def test_admin_cannot_delete_internship_with_applications(
    client, app
):
    with app.app_context():
        create_user(
            "Platform Admin", "protected-listing-admin@test.com", "admin"
        )

        internship_id = create_recruiter_internship(
            "protected-listing-recruiter@test.com",
            "Internship With History",
            "Closed"
        )

        student_user = create_user(
            "Historical Applicant",
            "historical-applicant@test.com",
            "student"
        )

        profile = StudentProfile(user_id=student_user.user_id)
        db.session.add(profile)
        db.session.flush()

        application = Application(
            student_id=profile.student_id,
            internship_id=internship_id,
            status="Rejected"
        )
        db.session.add(application)
        db.session.commit()

        application_id = application.application_id

    login_as(client, "protected-listing-admin@test.com")

    response = client.post(
        f"/admin/internships/{internship_id}/delete",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert (
        b"This internship has application history and cannot be deleted."
        in response.data
    )

    with app.app_context():
        assert db.session.get(Internship, internship_id) is not None
        assert db.session.get(Application, application_id) is not None

def test_non_admin_cannot_manage_platform_internships(
    client, app
):
    with app.app_context():
        create_user(
            "Regular Student", "global-blocked@test.com", "student"
        )

        internship_id = create_recruiter_internship(
            "blocked-listing-recruiter@test.com",
            "Protected Global Listing",
            "Draft"
        )

    login_as(client, "global-blocked@test.com")

    assert client.get("/admin/internships").status_code == 403

    assert client.post(
        f"/admin/internships/{internship_id}/status",
        data={"status": "Closed"}
    ).status_code == 403

    assert client.post(
        f"/admin/internships/{internship_id}/delete"
    ).status_code == 403

    with app.app_context():
        internship = db.session.get(Internship, internship_id)
        assert internship is not None
        assert internship.status == "Draft"