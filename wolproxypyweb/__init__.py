"""Initialize the Flask application.

It loads the configuration from the config.py file, initializes the Flask application,
creates the database and the tables, and registers the routes.
"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import FlaskConfig, logger

db = SQLAlchemy()
login = LoginManager()
bootstrap = Bootstrap()


def create_app(config_class=FlaskConfig):
    """Initialize the Flask application.

    It loads the configuration from the config_class object, initializes the Flask application.

    Args:
        config_class (FlaskConfig): The configuration class.

    Returns:
        app (Flask): The Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    login.init_app(app)
    login.login_view = "auth.login"
    login.login_message = "Please log in to access this page."
    bootstrap.init_app(app)

    from wolproxypyweb.main import bp as main_bp

    app.register_blueprint(main_bp)

    from wolproxypyweb.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from wolproxypyweb.admin import bp as admin_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")

    from wolproxypyweb.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    return app
