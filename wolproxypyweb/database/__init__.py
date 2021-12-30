from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import logger
from wolproxypyweb.database import models


def create_database(db: SQLAlchemy, app: Flask) -> None:
    """Create the database and the tables.

    Args:
        db (SQLAlchemy): The database.
        app (Flask): The Flask application.

    Returns:
        None
    """
    with app.app_context():
        db.create_all()
        logger.info("Database created.")
