"""Handle errors for invalid request and return custom error pages."""

from typing import Any, Optional

from flask import jsonify, render_template, request
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.wrappers import Response

from config import logger
from wolproxypyweb import db
from wolproxypyweb.errors import bp


def _api_error_response(status_code: int, message: Optional[str] = None) -> Response:
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def _wants_json_response() -> bool:
    return request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]


@bp.app_errorhandler(403)
def forbidden_error(error) -> Any:
    """Return a custom 403 error."""
    logger.error("Raised exception %s" % error)
    """Return a JSON response for 403 errors."""
    if _wants_json_response():
        return _api_error_response(404)
    return render_template("errors/403.html"), 403


@bp.app_errorhandler(404)
def not_found_error(error) -> Any:
    """Return a custom 404 error."""
    logger.error("Raised exception %s" % error)
    """Return a JSON response for 404 errors."""
    if _wants_json_response():
        return _api_error_response(404)
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error) -> Any:
    """Return a custom 500 error."""
    logger.error("Raised exception %s" % error)
    logger.error("Rolling back database")
    db.session.rollback()
    if _wants_json_response():
        return _api_error_response(500)
    return render_template("errors/500.html"), 500
