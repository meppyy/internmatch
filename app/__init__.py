from flask import Flask

from .config import Config
from .extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from . import models

    from .auth import auth
    app.register_blueprint(auth)

    @app.route("/")
    def home():
        return "InternMatch is running!"

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models.user import User

    return User.query.get(int(user_id))