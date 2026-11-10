from app import create_app


def test_internal_pages_load_shared_responsive_stylesheet():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "responsive-test-secret",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    client = app.test_client()

    login_response = client.get("/auth/login")
    register_response = client.get("/auth/register")
    css_response = client.get("/static/css/app.css")

    assert login_response.status_code == 200
    assert register_response.status_code == 200

    assert b"css/app.css" in login_response.data
    assert b"css/app.css" in register_response.data

    assert css_response.status_code == 200
    assert b"@media (max-width: 640px)" in css_response.data