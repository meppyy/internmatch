import json

from app import create_app


def test_pwa_manifest_is_available():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "pwa-test-secret",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    response = app.test_client().get("/manifest.json")

    assert response.status_code == 200

    manifest = json.loads(response.data)

    assert manifest["name"] == "InternMatch"
    assert manifest["short_name"] == "InternMatch"
    assert manifest["start_url"] == "/"
    assert manifest["display"] == "standalone"

    icon_sizes = {
        icon["sizes"] for icon in manifest["icons"]
    }

    assert "192x192" in icon_sizes
    assert "512x512" in icon_sizes


def test_pwa_icons_are_available():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "pwa-test-secret",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    client = app.test_client()

    for size in ("192", "512"):
        response = client.get(
            f"/static/icons/icon-{size}.png"
        )

        assert response.status_code == 200
        assert response.data.startswith(b"\x89PNG\r\n\x1a\n")


def test_service_worker_is_available():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "pwa-test-secret",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    response = app.test_client().get("/service-worker.js")

    assert response.status_code == 200
    assert b"addEventListener('install'" in response.data
    assert b"addEventListener('fetch'" in response.data


def test_pages_include_pwa_manifest_and_registration():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "pwa-test-secret",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    client = app.test_client()

    for page in ("/", "/auth/login", "/auth/register"):
        response = client.get(page)

        assert response.status_code == 200
        assert b"/manifest.json" in response.data
        assert b"service-worker.js" in response.data