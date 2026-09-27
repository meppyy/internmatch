from flask import Flask

from .config import Config
from .extensions import db, login_manager


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from . import models

    from .auth import auth
    app.register_blueprint(auth)

    from .student import student
    app.register_blueprint(student)

    @app.route("/")
    def home():
        return "InternMatch is running!"

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models.user import User

    return User.query.get(int(user_id))