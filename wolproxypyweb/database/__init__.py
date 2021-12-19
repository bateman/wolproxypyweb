""" Database instance creation module.
"""

from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy

from config import db_config, logger


def create_database(web_app: Flask) -> SQLAlchemy:
    """
    Create the database.

    Args:
        init (bool): If True, the database will be initialized.

    Returns:
        db (SQLAlchemy): The database.
    """
    # set the database uniform resource identifier for the database
    db_uri = f"{db_config['database']['protocol']}{db_config['database']['path']}{db_config['database']['name']}"
    logger.info("Database URI: %s", db_uri)
    web_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    # create an instance of the database module
    logger.info("Creating instance of the database.")
    db = SQLAlchemy(web_app)

    return db
