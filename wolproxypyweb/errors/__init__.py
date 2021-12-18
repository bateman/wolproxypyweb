from flask import Blueprint

bp = Blueprint("errors", __name__)

from wolproxypyweb.errors import handlers
