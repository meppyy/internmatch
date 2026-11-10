from app import create_app


def test_homepage_renders_landing_page():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"InternMatch" in response.data
    assert b"Your next chapter starts with" in response.data
    assert b"For Students" in response.data
    assert b"For Recruiters" in response.data
    assert b"Create Your Account" in response.data
    assert b"Log In" in response.data