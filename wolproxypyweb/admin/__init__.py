from flask import Blueprint

bp = Blueprint("admin", __name__)

from wolproxypyweb.admin import routes
