from flask import Blueprint

bp = Blueprint("auth", __name__)

from wolproxypyweb.auth import routes
