import pytest

from app import create_app


def test_production_requires_secret_key():
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({
            "APP_ENV": "production",
            "SECRET_KEY": None
        })


def test_production_enables_secure_cookies():
    app = create_app({
        "APP_ENV": "production",
        "SECRET_KEY": "test-only-secret"
    })

    assert app.config["DEBUG"] is False
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["REMEMBER_COOKIE_SECURE"] is True


def test_development_keeps_local_configuration():
    app = create_app({
        "APP_ENV": "development"
    })

    assert app.config["DEBUG"] is True
    assert app.config["SESSION_COOKIE_SECURE"] is False