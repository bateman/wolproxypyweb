"""The entry point for the Flask application."""

from config import logger
from wolproxypyweb import create_app, db
from wolproxypyweb.database import create_database

app = create_app()
create_database(db, app)


def run() -> None:
    """Run the proxy server via poetry.

    Forces the app not to run in debug mode because the
    restarting with watchdog doesn't work via poetry.

    Args:
        None

    Returns:
        None
    """
    logger.info("Starting the wolproxypyweb server.")
    app.run(host="0.0.0.0", debug=False)


if __name__ == "__main__":
    run()
