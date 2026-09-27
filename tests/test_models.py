import pytest

from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import (
    Application,
    Internship,
    RecruiterProfile,
    Resume,
    Skill,
    StudentProfile,
    User,
)


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    return db.session


def test_user_creation(session):
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash="test-hash",
        role="student",
    )

    session.add(user)
    session.commit()

    assert user.user_id is not None
    assert user.email == "test@example.com"
    assert user.role == "student"

def test_user_email_must_be_unique(session):
    user1 = User(
        name="User One",
        email="same@example.com",
        password_hash="hash",
        role="student",
    )

    user2 = User(
        name="User Two",
        email="same@example.com",
        password_hash="hash",
        role="student",
    )

    session.add(user1)
    session.commit()

    session.add(user2)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

def test_student_profile(session):
    user = User(
        name="Student",
        email="student@example.com",
        password_hash="hash",
        role="student",
    )

    session.add(user)
    session.flush()

    student = StudentProfile(
        user_id=user.user_id,
        education="B.Sc. Computer Science",
    )

    session.add(student)
    session.commit()

    assert student.student_id is not None
    assert student.user_id == user.user_id


def test_recruiter_profile(session):
    user = User(
        name="Recruiter",
        email="recruiter@example.com",
        password_hash="hash",
        role="recruiter",
    )

    session.add(user)
    session.flush()

    recruiter = RecruiterProfile(
        user_id=user.user_id,
        company_name="Test Company",
    )

    session.add(recruiter)
    session.commit()

    assert recruiter.recruiter_id is not None
    assert recruiter.company_name == "Test Company"


def test_resume(session):
    user = User(
        name="Student",
        email="resume@example.com",
        password_hash="hash",
        role="student",
    )

    session.add(user)
    session.flush()

    student = StudentProfile(user_id=user.user_id)
    session.add(student)
    session.flush()

    resume = Resume(
        student_id=student.student_id,
        file_name="resume.pdf",
        file_path="uploads/resume.pdf",
    )

    session.add(resume)
    session.commit()

    assert resume.resume_id is not None
    assert resume.student_id == student.student_id


def test_internship(session):
    user = User(
        name="Recruiter",
        email="internship@example.com",
        password_hash="hash",
        role="recruiter",
    )

    session.add(user)
    session.flush()

    recruiter = RecruiterProfile(
        user_id=user.user_id,
        company_name="Test Company",
    )

    session.add(recruiter)
    session.flush()

    internship = Internship(
        recruiter_id=recruiter.recruiter_id,
        title="Python Intern",
        company_name="Test Company",
        status="Open",
    )

    session.add(internship)
    session.commit()

    assert internship.internship_id is not None
    assert internship.recruiter_id == recruiter.recruiter_id


def test_skill_relationships(session):
    student_user = User(
        name="Student",
        email="skillstudent@example.com",
        password_hash="hash",
        role="student",
    )

    recruiter_user = User(
        name="Recruiter",
        email="skillrecruiter@example.com",
        password_hash="hash",
        role="recruiter",
    )

    session.add_all([student_user, recruiter_user])
    session.flush()

    student = StudentProfile(user_id=student_user.user_id)
    recruiter = RecruiterProfile(
        user_id=recruiter_user.user_id,
        company_name="Test Company",
    )

    session.add_all([student, recruiter])
    session.flush()

    internship = Internship(
        recruiter_id=recruiter.recruiter_id,
        title="Python Intern",
        company_name="Test Company",
        status="Open",
    )

    skill = Skill(skill_name="Python")

    session.add_all([internship, skill])
    session.flush()

    student.skills.append(skill)
    internship.skills.append(skill)

    session.commit()

    assert skill in student.skills
    assert skill in internship.skills
    assert student in skill.students
    assert internship in skill.internships


def test_application(session):
    student_user = User(
        name="Student",
        email="applicationstudent@example.com",
        password_hash="hash",
        role="student",
    )

    recruiter_user = User(
        name="Recruiter",
        email="applicationrecruiter@example.com",
        password_hash="hash",
        role="recruiter",
    )

    session.add_all([student_user, recruiter_user])
    session.flush()

    student = StudentProfile(user_id=student_user.user_id)
    recruiter = RecruiterProfile(
        user_id=recruiter_user.user_id,
        company_name="Test Company",
    )

    session.add_all([student, recruiter])
    session.flush()

    resume = Resume(
        student_id=student.student_id,
        file_name="resume.pdf",
        file_path="uploads/resume.pdf",
    )

    internship = Internship(
        recruiter_id=recruiter.recruiter_id,
        title="Python Intern",
        company_name="Test Company",
        status="Open",
    )

    session.add_all([resume, internship])
    session.flush()

    application = Application(
        student_id=student.student_id,
        internship_id=internship.internship_id,
        resume_id=resume.resume_id,
        status="Applied",
    )

    session.add(application)
    session.commit()

    assert application.application_id is not None
    assert application.student_id == student.student_id
    assert application.internship_id == internship.internship_id
    assert application.resume_id == resume.resume_id
    assert application.status == "Applied"