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
    css_response = client.get("/static/css/style.css")

    assert login_response.status_code == 200
    assert register_response.status_code == 200

    # Both authentication pages should load the shared stylesheet.
    assert b"css/style.css" in login_response.data
    assert b"css/style.css" in register_response.data

    # Verify the shared stylesheet is served successfully.
    assert css_response.status_code == 200

    # Verify responsive authentication styling exists.
    assert b"@media (max-width: 600px)" in css_response.data
    assert b".auth-page" in css_response.data
    assert b".auth-form" in css_response.data