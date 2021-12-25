"""Initialize the Flask application.

It loads the configuration from the config.py file, initializes the Flask application,
creates the database and the tables, and registers the routes.
"""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from config import FlaskConfig
from wolproxypyweb.database import create_database

app = Flask(__name__)
app.config.from_object(FlaskConfig)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = "login"

db = create_database(app)

from wolproxypyweb import errors, routes
from wolproxypyweb.database import models
from wolproxypyweb.errors import bp as errors_bp

app.register_blueprint(errors_bp)
