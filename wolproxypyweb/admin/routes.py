"""Definiton of the admin routes."""
from typing import Any

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response

from config import app_config, logger
from wolproxypyweb import db
from wolproxypyweb.admin import bp
from wolproxypyweb.admin.forms import ApiForm, SingleSignOnForm
from wolproxypyweb.database.models import User


@bp.route("/", methods=["GET"])
@login_required
def admin() -> Any:
    """Render the admin page.

    This page is only accessible to users with the admin role.

    Returns:
        Response: The rendered admin page if the current user is an admin, 403 otherwise.
    """
    if not current_user.is_admin:
        logger.error("User %s tried to access admin page." % current_user.id)
        # raise forbidden error
        abort(403)
    else:
        return render_template("admin/admin.html", pages=generate_page_list())


@bp.route("/general", methods=["GET"])
@login_required
def general() -> Response:
    """Render the general options page.

    Returns:
        Response: The rendered general options page.
    """
    return render_template(
        "admin/general.html", title="General", pages=generate_page_list(), selected="General", app_config=app_config
    )


@bp.route("/users", methods=["GET"])
@login_required
def users() -> Response:
    """Render the users page.

    Returns:
        Response: The rendered users page.
    """
    users = User.query.all()
    return render_template(
        "admin/users.html",
        title="Users",
        pages=generate_page_list(),
        selected="Users",
        currentuserid=current_user.id,
        users=users,
    )


@bp.route("/api", methods=["GET", "POST"])
@login_required
def api() -> Response:
    """Render the API settings page.

    Returns:
        Response: The rendered API settings page.
    """
    form = ApiForm()
    if form.validate_on_submit():
        logger.info("Updating API key.")
        app_config.setsave("API_KEY", form.key.data)
        flash("API key updated")
        return redirect(url_for("admin.api"))
    elif request.method == "GET":
        form.key.data = app_config.get("API_KEY")
    return render_template(
        "admin/api.html", title="API settings", pages=generate_page_list(), selected="API", form=form
    )


@bp.route("/sso", methods=["GET", "POST"])
@login_required
def sso() -> Response:
    """Render the SSO settings page.

    Returns:
        Response: The rendered SSO settings page.
    """
    form = SingleSignOnForm()
    if form.validate_on_submit():
        logger.info("Updating SSO settings.")
        app_config.setsave("SSO_CLIENT_ID", form.id.data)
        app_config.setsave("SSO_CLIENT_SECRET", form.secret.data)
        flash("SSO settings updated")
        return redirect(url_for("admin.sso"))
    elif request.method == "GET":
        form.id.data = app_config.get("SSO_CLIENT_ID")
        form.secret.data = app_config.get("SSO_CLIENT_SECRET")
    return render_template(
        "admin/sso.html",
        title="Single Sign-On settings",
        pages=generate_page_list(),
        selected="SSO",
        form=form,
    )


@bp.route("/change/<option>/<value>", methods=["GET"])
@login_required
def change_option(option: str, value: str) -> Response:
    """Change the admin status of a user.

    Args:
        option (str): The option to change.
        value (str): The new option value.

    Returns:
        Response: A redirect back to the admin page.
    """
    option = option.removeprefix("toggle-")
    logger.debug(f"Changing {option} status to {value}.")
    if value == "false":
        value = "False"
    elif value == "true":
        value = "True"
    else:
        flash("Error setting invalid option value %s" % value, "danger")
        logger.error("Option value must be either true or false.")

    if option == "adminstration":
        app_config.setsave("ADMIN_ENABLED", value)
        logger.info("Changed adminstration status to %s." % value)
    elif option == "registration":
        app_config.setsave("REGISTRATION_ENABLED", value)
        logger.info("Changed registration status to %s." % value)
    else:
        flash("Error setting invalid option %s" % option, "danger")
        logger.error("Option %s is not valid." % option)

    return redirect(url_for("admin.admin"))


@bp.route("/set/<userid>/<is_admin>", methods=["GET"])
@login_required
def set_admin(userid: int, is_admin: bool) -> Response:
    """Set the admin status of a user.

    User with id 1 is the the superuser and that status cannot be changed.

    Args:
        userid (int): The user id to set the admin status of.
        is_admin (bool): The new admin status.

    Returns:
        Response: A redirect back to the admin page.
    """
    user = User.query.filter_by(id=userid).first()
    if userid == "1":
        flash("Forbidden: User %s is the superuser.", user.username, "warning")
        logger.debug("Attempt to change admin status of user with id 1: forbidden.")
    else:
        if not user:
            abort(404)
        if is_admin == "false":
            is_admin = False
        elif is_admin == "true":
            is_admin = True
        else:
            raise ValueError("Option value must be either true or false.")
        logger.info("Chaning admin status")
        user.is_admin = is_admin
        db.session.commit()
        flash(f"Admin status of user {user.username} changed to {is_admin}.")
        logger.debug("Changed admin status of %s" % user)
    return redirect(url_for("admin.admin"))


@bp.route("/delete/<userid>", methods=["GET"])
@login_required
def delete_user(userid: int) -> Response:
    """Delete a user from the database.

     User with id 1 is the the superuser and that status cannot be changed.

    Args:
        userid (int): The id of the user to delete.

    Returns:
        Response: A redirect back to the admin page.
    """
    user = User.query.filter_by(id=userid).first()
    if userid == "1":
        flash("Forbidden: User %s is the superuser." % user.username, "warning")
    else:
        try:
            if user == current_user:
                flash("You have deleted yourself and have been logged out.", "warning")
                logger.debug("Self deletion of user %s." % user.username)
            logger.info("Removing user")
            db.session.delete(user)
            db.session.commit()
            flash("User %s deleted." % user.username)
        except SQLAlchemyError as sqe:
            flash("Error deleting user %s" % user.username, "danger")
            logger.error("Raised exception %s" % sqe)
    return redirect(url_for("admin.users"))


def generate_page_list() -> list:
    """Generate a list of pages for the admin sidebar.

    Returns:
        list: A list of pages for the admin sidebar.
    """
    pages = [
        {"name": "General", "url": url_for("admin.general")},
        {"name": "Users", "url": url_for("admin.users")},
        {"name": "API", "url": url_for("admin.api")},
        {"name": "SSO", "url": url_for("admin.sso")},
    ]
    return pages
