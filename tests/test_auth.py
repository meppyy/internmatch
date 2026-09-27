import pytest

from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from app.extensions import db
from app.models import (
    RecruiterProfile,
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


def test_register_student(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "New Student",
            "email": "newstudent@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "role": "student",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(
            email="newstudent@example.com"
        ).first()

        assert user is not None
        assert user.name == "New Student"
        assert user.role == "student"
        assert user.password_hash != "TestPassword123"
        assert check_password_hash(
            user.password_hash,
            "TestPassword123",
        )

        student = StudentProfile.query.filter_by(
            user_id=user.user_id
        ).first()

        assert student is not None


def test_register_duplicate_email(client, app):
    client.post(
        "/auth/register",
        data={
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "role": "student",
        },
    )

    response = client.post(
        "/auth/register",
        data={
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "TestPassword456",
            "confirm_password": "TestPassword456",
            "role": "student",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        users = User.query.filter_by(
            email="duplicate@example.com"
        ).all()

        assert len(users) == 1


def test_login_success(client, app):
    with app.app_context():
        create_user(
            db.session,
            email="login@example.com",
            password="TestPassword123",
            role="student",
        )

    response = login(
        client,
        "login@example.com",
        "TestPassword123",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_wrong_password(client, app):
    with app.app_context():
        create_user(
            db.session,
            email="wrongpassword@example.com",
            password="TestPassword123",
            role="student",
        )

    response = login(
        client,
        "wrongpassword@example.com",
        "WrongPassword",
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_login_unknown_email(client):
    response = login(
        client,
        "doesnotexist@example.com",
        "TestPassword123",
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_logout(client, app):
    with app.app_context():
        create_user(
            db.session,
            email="logout@example.com",
            password="TestPassword123",
            role="student",
        )

    login(
        client,
        "logout@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/auth/logout",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_protected_route_requires_login(client):
    response = client.get(
        "/auth/student-test",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_student_role_authorization(client, app):
    with app.app_context():
        create_user(
            db.session,
            email="student@example.com",
            password="TestPassword123",
            role="student",
        )

    login(
        client,
        "student@example.com",
        "TestPassword123",
    )

    response = client.get("/auth/student-test")
    assert response.status_code == 200
    assert b"Student access granted!" in response.data


def test_student_blocked_from_recruiter_route(client, app):
    with app.app_context():
        create_user(
            db.session,
            email="student2@example.com",
            password="TestPassword123",
            role="student",
        )

    login(
        client,
        "student2@example.com",
        "TestPassword123",
    )

    response = client.get("/auth/recruiter-test")

    assert response.status_code == 403


def test_student_blocked_from_admin_route(client, app):
    with app.app_context():
        create_user(
            db.session,
            email="student3@example.com",
            password="TestPassword123",
            role="student",
        )

    login(
        client,
        "student3@example.com",
        "TestPassword123",
    )

    response = client.get("/auth/admin-test")

    assert response.status_code == 403