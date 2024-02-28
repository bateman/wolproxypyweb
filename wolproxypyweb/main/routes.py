"""Definiton of the web app routes."""

import json
from typing import Any

import requests
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.wrappers import Response

from config import app_config, logger
from wolproxypyweb import db
from wolproxypyweb.database.models import Host
from wolproxypyweb.main import bp
from wolproxypyweb.main.forms import AddHostForm, EditHostForm, EditUserProfileForm


def _call_wolproxypyapi(host: Host) -> Response:
    """Call the API to wake up the host."""
    url = f"{app_config.get('API_PROTO')}://{app_config.get('API_HOST')}:" f"{app_config.get('API_PORT')}/wol"
    data = {
        "host": {
            "mac_address": host.macaddress,
            "ip_address": host.ipaddress,
            "port": host.port,
            "interface": host.interface,
        },
        "key": {"key": app_config.get("API_KEY")},
    }

    logger.debug(json.dumps(data))
    logger.info("Calling the API endpoint %s" % url)
    return requests.post(url=url, data=json.dumps(data), timeout=5)


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def home() -> Any:
    """Render the home page."""
    form = AddHostForm()
    if form.validate_on_submit():
        host = Host(
            name=form.name.data,
            macaddress=form.macaddress.data,
            ipaddress=form.ipaddress.data or "",
            port=form.port.data or 9,
            interface=form.interface.data or "",
            user_id=current_user.id,
        )
        if form.submit.data:
            try:
                db.session.add(host)
                db.session.commit()
                logger.info("Storing %s" % host)
                flash("Host added")
            except IntegrityError as ie:
                flash("Host configuration already exists, skipping")
                logger.error("Raised exception %s" % ie)
            except SQLAlchemyError as sqe:
                flash("Error adding host")
                logger.error("Raised exception %s" % sqe)
        elif form.wake.data:
            try:
                logger.info("Waking %s" % host)
                response = _call_wolproxypyapi(host)
                logger.info("Response %s" % response)
                if response.status_code == 200:
                    flash(f"Wake-on-lan packet sent to {host}.", "success")
                else:
                    flash(f"Error sending wake-on-lan packet to {host}.", "warning")
            except Exception as e:
                flash("Failed to send wol packet to host", "warning")
                logger.error("Raised exception %s." % e)
        return redirect(url_for("main.home"))
    hosts = current_user.get_hosts()
    return render_template("index.html", title="Home", hosts=hosts, form=form)


@bp.route("/wake/<hostid>")
@login_required
def wake_host(hostid: int) -> Response:
    """Wake a host using the wol api.

    Args:
        hostid (int): The id of the host to wake.
    """
    try:
        host = Host.query.filter_by(id=hostid).first()
    except SQLAlchemyError as sqe:
        flash("Error querying host")
        logger.error("Raised exception %s" % sqe)
    logger.info("Waking %s" % host)
    try:
        logger.info("Waking %s" % host)
        response = _call_wolproxypyapi(host)
        logger.info("Response %s" % response)
        if response.status_code == 200:
            flash(f"Wake-on-lan packet sent to {host}.", "success")
        else:
            flash(f"Error sending wake-on-lan packet to {host}.", "warning")
    except Exception as e:
        flash("Error sending wol packet to host", "warning")
        logger.error("Raised exception %s" % e)
    return redirect(url_for("main.home"))


@bp.route("/hosts", methods=["GET", "POST"])
@login_required
def edit_hosts() -> Any:
    """Render the edit hosts page."""
    form = EditHostForm()
    if form.validate_on_submit():
        host = Host(
            name=form.name.data,
            macaddress=form.macaddress.data,
            ipaddress=form.ipaddress.data or "",
            port=form.port.data or 9,
            interface=form.interface.data or "",
            user_id=current_user.id,
        )
        if form.submit.data:
            try:
                if form.hiddenid.data:
                    logger.info("Updating %s" % host)
                    host = Host.query.filter_by(id=form.hiddenid.data).first()
                    host.name = form.name.data
                    host.macaddress = form.macaddress.data
                    host.ipaddress = form.ipaddress.data or ""
                    host.port = form.port.data or 9
                    host.interface = form.interface.data or ""
                    db.session.commit()
                    flash("Host updated")
                else:
                    logger.info("Adding %s" % host)
                    host = Host(
                        name=form.name.data,
                        macaddress=form.macaddress.data,
                        ipaddress=form.ipaddress.data or "",
                        port=form.port.data or 9,
                        interface=form.interface.data or "",
                        user_id=current_user.id,
                    )
                    db.session.add(host)
                    db.session.commit()
                    flash("Host added")
            except IntegrityError as ie:
                flash("Host configuration already exists, skipping", "warning")
                logger.error("Raised exception %s" % ie)
            except SQLAlchemyError as sqe:
                flash("Error adding host", "danger")
                logger.error("Raised exception %s" % sqe)
        return redirect(url_for("main.edit_hosts"))
    hosts = current_user.get_hosts()
    return render_template("host.html", title="Edit hosts", form=form, hosts=hosts)


@bp.route("/delete/<hostid>")
@login_required
def delete_host(hostid: int) -> Response:
    """Delete host from database.

    Args:
        hostid (int): Host id to delete.
    """
    host = Host.query.filter_by(id=hostid).first()
    try:
        db.session.delete(host)
        logger.info("Removing %s" % host)
        db.session.commit()
    except SQLAlchemyError as sqe:
        flash("Error removing host", "danger")
        logger.error("Raised exception %s" % sqe)
    return redirect(url_for("main.edit_hosts"))


@bp.route("/get/<hostid>")
@login_required
def get(hostid: int) -> str:
    """Return the host configuration as a JSON string.

    Args:
        hostid (int): The id of the host to return.

    Returns:
        str: The host configuration as a JSON string.
    """
    try:
        host = Host.query.filter_by(id=hostid).first()
    except SQLAlchemyError as sqe:
        flash("Error querying host", "danger")
        logger.error("Raised exception %s" % sqe)
    return host.to_json()


@bp.route("/user", methods=["GET", "POST"])
@login_required
def edit_profile() -> Any:
    """Render the edit profile form."""
    form = EditUserProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data and form.password.data == form.password_confirm.data:
            current_user.set_password(form.password.data)
        current_user.set_password(form.password.data)
        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("user.html", title="Edit Profile", form=form)


@bp.route("/about")
def about() -> str:
    """Render the about page."""
    return render_template("about.html", title="About")
