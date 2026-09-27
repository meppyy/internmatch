import pytest

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User


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
        create_user(
            db.session,
            name="Test Recruiter",
            email="recruiter@test.com",
            password="TestPassword123",
            role="recruiter",
        )

    login(
        client,
        "recruiter@test.com",
        "TestPassword123",
    )

    response = client.get("/recruiter/dashboard")

    assert response.status_code == 200
    assert response.data == b"Recruiter Dashboard"


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