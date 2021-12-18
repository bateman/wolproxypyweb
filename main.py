"""
The entry point for the Flask application.
"""
from wolproxypyweb import app


def run() -> None:
    """
    Runs the proxy server via poetry.

    Forces the app not to run in debug mode because the
    restarting with watchdog doesn't work via poetry.

    Args:
        None

    Returns:
        None
    """
    app.run(debug=False)


if __name__ == "__main__":
    run()
