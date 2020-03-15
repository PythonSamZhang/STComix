import os

from flask import Flask
from flask_uploads import configure_uploads, patch_request_class

from .extensions import *
from .models import User


def create_app():
    env = os.environ.get('CONFIG_NAME') or 'dev'
    app = Flask(__name__)
    app.config.from_pyfile('%s.cfg' % env)
    bootstrap.init_app(app)
    bebel.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    dropzone.init_app(app)
    moment.init_app(app)
    avatars.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'Please Login First'

    configure_uploads(app, books)
    patch_request_class(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin as admin_bp
    app.register_blueprint(admin_bp)

    return app
