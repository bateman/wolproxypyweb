from flask import Blueprint

bp = Blueprint("main", __name__)

from wolproxypyweb.main import routes
