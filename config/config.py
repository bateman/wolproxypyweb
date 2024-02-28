"""Configuration file for the application."""

import configparser
import logging
import logging.config
import os
from pathlib import Path

import pretty_errors
from dotenv import load_dotenv
from easysettings import EasySettings
from rich.logging import RichHandler

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "config")
LOGS_DIR = Path(BASE_DIR, "logs")
DATABASE_DIR = Path(BASE_DIR, "db")

# Create dirs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)


# Use config file to initialize rich logger
logging.config.fileConfig(Path(CONFIG_DIR, "logging.config"))
logger = logging.getLogger("root")
logger.handlers[0] = RichHandler(markup=True)
if os.environ.get("FLASK_DEBUG"):
    logger.setLevel(logging.DEBUG)

# Configure error formatter
pretty_errors.configure(
    separator_character="*",
    filename_display=pretty_errors.FILENAME_EXTENDED,
    line_number_first=True,
    display_link=True,
    lines_before=5,
    lines_after=2,
    line_color=pretty_errors.RED + "> " + pretty_errors.default_config.line_color,
    code_color="  " + pretty_errors.default_config.line_color,
    truncate_code=True,
    display_locals=True,
)


# App
class AppConfig(EasySettings):
    """Configuration options for the app."""

    def __init__(self):
        """Initialize the app config."""
        super().__init__(name="wolproxypyweb")
        self.configfile = os.path.join(CONFIG_DIR, "app.config")
        if not os.path.exists(self.configfile):
            logger.info("No app config file found. Creating new one in %s", self.configfile)
            self.configfile_create()
            self.set("ADMIN_ENABLED", "True")
            self.set("REGISTRATION_ENABLED", "True")
            self.set("API_PROTO", "http")
            self.set("API_HOST", "0.0.0.0")
            self.set("API_PORT", "8000")
            self.set("API_KEY", "")
            self.save()
        else:
            logger.info("Loading app config file %s", self.configfile)
            self.load_file()


app_config = AppConfig()


# Flask
db_config = configparser.ConfigParser()
with open(Path(CONFIG_DIR, "db.config"), encoding="UTF-8") as f:
    db_config.read_file(f)

load_dotenv(dotenv_path=Path(BASE_DIR, ".env"))


class FlaskConfig:
    """Configuration for the Flask application."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24).hex()
    SQLALCHEMY_DATABASE_URI = (
        f"{db_config['database']['protocol']}{DATABASE_DIR}{os.sep}{db_config['database']['name']}"
    )
