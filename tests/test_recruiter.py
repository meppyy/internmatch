import pytest

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db

from app.models import (
    User, RecruiterProfile, StudentProfile,
    Internship, Application, Resume, Skill
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

        return application.application_id


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

def test_recruiter_can_view_applicant_skill_match(client, app):
    email, internship_id = create_recruiter_internship(
        app,
        "applicant-match@test.com",
        "Python Developer Internship"
    )

    application_id = create_applicant_for_internship(
        app, internship_id
    )

    with app.app_context():
        internship = db.session.get(
            Internship, internship_id
        )
        application = db.session.get(
            Application, application_id
        )

        def get_or_create_skill(skill_name):
            skill = Skill.query.filter_by(
                skill_name=skill_name
            ).first()

            if not skill:
                skill = Skill(skill_name=skill_name)
                db.session.add(skill)
                db.session.flush()

            return skill

        # Internship requirements.
        for skill_name in ["Python", "SQL", "Flask"]:
            internship.skills.append(
                get_or_create_skill(skill_name)
            )

        # Applicant's existing skills.
        for skill_name in ["Python", "SQL", "Git"]:
            application.student.skills.append(
                get_or_create_skill(skill_name)
            )

        db.session.commit()

    login(client, email, "TestPassword123")

    response = client.get(
        f"/recruiter/internships/{internship_id}/applications"
    )

    assert response.status_code == 200
    assert b"Skill Match" in response.data
    assert b"67%" in response.data
    assert b"Matched Skills" in response.data
    assert b"Python" in response.data
    assert b"SQL" in response.data
    assert b"Missing Skills" in response.data
    assert b"Flask" in response.data

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


def test_recruiter_can_update_application_status(client, app):
    email, internship_id = create_recruiter_internship(
        app,
        "status-owner@test.com",
        "Status Test Internship"
    )

    application_id = create_applicant_for_internship(
        app, internship_id
    )

    login(client, email, "TestPassword123")

    response = client.post(
        f"/recruiter/internships/{internship_id}/applications/"
        f"{application_id}/status",
        data={"status": "Shortlisted"}
    )

    assert response.status_code == 302

    with app.app_context():
        application = db.session.get(Application, application_id)
        assert application.status == "Shortlisted"

    page = client.get(
        f"/recruiter/internships/{internship_id}/applications"
    )
    assert b"Shortlisted" in page.data
    assert b"Change Status" in page.data


def test_recruiter_cannot_update_another_recruiters_application(
    client, app
):
    owner_email, _ = create_recruiter_internship(
        app,
        "status-first-owner@test.com",
        "First Owner Internship"
    )

    _, other_internship_id = create_recruiter_internship(
        app,
        "status-second-owner@test.com",
        "Second Owner Internship"
    )

    application_id = create_applicant_for_internship(
        app, other_internship_id
    )

    login(client, owner_email, "TestPassword123")

    response = client.post(
        f"/recruiter/internships/{other_internship_id}/applications/"
        f"{application_id}/status",
        data={"status": "Rejected"}
    )

    assert response.status_code == 404

    with app.app_context():
        application = db.session.get(Application, application_id)
        assert application.status == "Under Review"

def test_recruiter_cannot_set_invalid_application_status(
    client, app
):
    email, internship_id = create_recruiter_internship(
        app,
        "status-invalid-owner@test.com",
        "Invalid Status Internship"
    )

    application_id = create_applicant_for_internship(
        app, internship_id
    )

    login(client, email, "TestPassword123")

    response = client.post(
        f"/recruiter/internships/{internship_id}/applications/"
        f"{application_id}/status",
        data={"status": "Invalid Status"}
    )

    assert response.status_code == 302

    with app.app_context():
        application = db.session.get(Application, application_id)
        assert application.status == "Under Review"


def test_recruiter_can_view_only_authorized_applicant_resumes(
    client, app, tmp_path
):
    owner_email, internship_id = create_recruiter_internship(
        app,
        "resume-owner@test.com",
        "Resume Access Internship"
    )

    _, other_internship_id = create_recruiter_internship(
        app,
        "resume-other-owner@test.com",
        "Other Recruiter's Internship"
    )

    application_id = create_applicant_for_internship(
        app, internship_id
    )

    resume_content = b"%PDF-1.4 test resume content"
    resume_path = tmp_path / "applicant_resume.pdf"
    resume_path.write_bytes(resume_content)

    with app.app_context():
        application = db.session.get(Application, application_id)

        application.resume.file_path = str(resume_path)

        other_application = Application(
            student_id=application.student_id,
            internship_id=other_internship_id,
            resume_id=application.resume_id,
            status="Applied"
        )

        db.session.add(other_application)
        db.session.commit()

        other_application_id = other_application.application_id

    login(client, owner_email, "TestPassword123")

    resume_url = (
        f"/recruiter/internships/{internship_id}/applications/"
        f"{application_id}/resume"
    )

    response = client.get(resume_url)

    assert response.status_code == 200
    assert response.data == resume_content
    assert response.mimetype == "application/pdf"

    applicants_page = client.get(
        f"/recruiter/internships/{internship_id}/applications"
    )
    assert b"View Resume" in applicants_page.data

    # Another recruiter must not access the same student's resume
    # through an internship they do not own.
    other_response = client.get(
        f"/recruiter/internships/{other_internship_id}/applications/"
        f"{other_application_id}/resume"
    )
    assert other_response.status_code == 404

    # An application without an attached resume has no file to serve.
    with app.app_context():
        application = db.session.get(Application, application_id)
        application.resume_id = None
        db.session.commit()
    
    missing_resume_response = client.get(resume_url)
    assert missing_resume_response.status_code == 404

    # Students must not use the recruiter-only resume endpoint.
    student_client = app.test_client()
    login(
        student_client,
        "applicant@example.com",
        "TestPassword123"
    )

    student_response = student_client.get(resume_url)
    assert student_response.status_code == 403