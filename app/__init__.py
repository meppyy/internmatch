import os

from flask import Flask, render_template
from datetime import datetime

from app import admin

from .config import Config
from .extensions import db, login_manager, migrate, csrf


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    # Apply environment-dependent settings.
    app_environment = app.config.get(
        "APP_ENV", "development"
    ).strip().lower()

    is_production = app_environment == "production"

    app.config.update({
        "APP_ENV": app_environment,
        "DEBUG": not is_production,
        "SESSION_COOKIE_SECURE": is_production,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "REMEMBER_COOKIE_SECURE": is_production,
        "REMEMBER_COOKIE_HTTPONLY": True,
        "REMEMBER_COOKIE_SAMESITE": "Lax",
    })

    # Require a secure secret key in production.
    if (
        is_production
        and (
            not app.config.get("SECRET_KEY")
            or app.config.get("SECRET_KEY") == "dev-secret-key"
        )
    ):
        raise RuntimeError(
            "A secure SECRET_KEY must be configured in production."
        )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from . import models

    from .auth import auth
    app.register_blueprint(auth)

    from .student import student
    app.register_blueprint(student)

    from .recruiter import recruiter
    app.register_blueprint(recruiter)

    from .admin import admin
    app.register_blueprint(admin)

    from .pwa import pwa
    app.register_blueprint(pwa)

    @app.route("/")
    def home():
        return render_template(
            "index.html",
            current_year=datetime.now().year
        )

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models.user import User
    return User.query.get(int(user_id))