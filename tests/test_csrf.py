import re

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "csrf-test-secret",
        "WTF_CSRF_ENABLED": True,
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


def test_post_without_csrf_token_is_rejected(client):
    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "password123",
        }
    )

    assert response.status_code == 400
    assert b"CSRF" in response.data


def test_auth_forms_render_csrf_tokens(client):
    login_response = client.get("/auth/login")
    register_response = client.get("/auth/register")

    assert login_response.status_code == 200
    assert register_response.status_code == 200

    assert b'name="csrf_token"' in login_response.data
    assert b'name="csrf_token"' in register_response.data


def test_valid_csrf_token_allows_post(client):
    response = client.get("/auth/login")

    match = re.search(
        rb'name="csrf_token"[^>]*value="([^"]+)"',
        response.data
    )

    assert match is not None

    token = match.group(1).decode()

    response = client.post(
        "/auth/login",
        data={
            "csrf_token": token,
            "email": "unknown@example.com",
            "password": "password123",
        }
    )

    # The request passes CSRF validation and reaches the login route.
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]