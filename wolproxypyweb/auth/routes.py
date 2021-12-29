"""Auth routes."""
from typing import Any

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.wrappers import Response

from config import logger
from wolproxypyweb import db
from wolproxypyweb.auth import bp
from wolproxypyweb.auth.forms import LoginForm, RegistrationForm
from wolproxypyweb.database.models import User


@bp.route("/login", methods=["GET", "POST"])
def login() -> Any:
    """Render the login page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm(remember_me=True)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        logger.info("User %s logged in." % user.username)
        return redirect(url_for("main.home"))
    return render_template("auth/login.html", title="Sign In", form=form)


@bp.route("/loginnav", methods=["POST"])
def login_navbar() -> Response:
    """Login from navbar."""
    user = User.query.filter_by(username=request.form["navbarusername"]).first()
    if user is None or not user.check_password(request.form["navbarpassword"]):
        flash("Invalid username or password.")
        return redirect(url_for("auth.login"))
    try:
        remember = bool(request.form["navbarcheckbox"])
    except KeyError:  # if unchecked
        remember = False
    login_user(user, remember=remember)
    logger.info("User %s logged in" % user.username)
    return redirect(url_for("main.home"))


@bp.route("/logout")
def logout() -> Response:
    """Logout the current user."""
    logger.info("Logging out user %s." % current_user.username)
    logout_user()
    return redirect(url_for("main.home"))


@bp.route("/register", methods=["GET", "POST"])
def register() -> Any:
    """Render the registration page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        logger.info("User %s registered." % user.username)
        flash("You are registered. Please, log in.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Register", form=form)
