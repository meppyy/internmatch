import os

from flask import Flask

from .config import Config
from .extensions import db, login_manager, migrate, csrf


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

        
        # Recalculate environment-dependent settings after test overrides.
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


        if (
            app.config.get("APP_ENV") == "production"
            and (
                not app.config.get("SECRET_KEY")
                or app.config.get("SECRET_KEY") == "dev-secret-key"
            )
        ):
            raise RuntimeError(
                "SECRET_KEY must be configured in production."
            )

    # Ensure the required directories exist.
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import models.
    from . import models

    # Register blueprints.
    from .auth import auth
    app.register_blueprint(auth)

    from .student import student
    app.register_blueprint(student)

    from .recruiter import recruiter
    app.register_blueprint(recruiter)

    @app.route("/")
    def home():
        return "InternMatch is running!"

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models.user import User

    return User.query.get(int(user_id))
