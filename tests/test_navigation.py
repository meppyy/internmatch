import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "navigation-test-secret",
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


def create_user(app, role):
    with app.app_context():
        user = User(
            name=f"Test {role.title()}",
            email=f"{role}@navigation.test",
            password_hash="test-password",
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return user.user_id


def authenticate_as(client, user_id):
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def test_guest_navigation_shows_login_and_registration(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"For Students" in response.data
    assert b"For Recruiters" in response.data
    assert b"Login" in response.data
    assert b"Register" in response.data
    assert b"Log Out" not in response.data


def test_student_navigation_shows_student_links(client, app):
    user_id = create_user(app, "student")
    authenticate_as(client, user_id)

    response = client.get("/")

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Profile" in response.data
    assert b"Skills" in response.data
    assert b"Resume" in response.data
    assert b'action="/auth/logout"' in response.data
    assert b'method="POST"' in response.data
    assert b'name="csrf_token"' in response.data
    assert b"Browse Internships" in response.data
    assert b"My Applications" in response.data


def test_recruiter_navigation_shows_recruiter_links(client, app):
    user_id = create_user(app, "recruiter")
    authenticate_as(client, user_id)

    response = client.get("/")

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Profile" in response.data
    assert b"My Internships" in response.data
    assert b"Create Internship" in response.data
    assert b'action="/auth/logout"' in response.data
    assert b'method="POST"' in response.data