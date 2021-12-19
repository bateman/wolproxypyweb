import requests
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import ApiConfig, logger
from wolproxypyweb import app, db
from wolproxypyweb.database.models import Host, User
from wolproxypyweb.forms import (
    AddHostForm,
    EditHostForm,
    EditUserProfileForm,
    LoginForm,
    RegistrationForm,
)


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def home() -> str:
    form = AddHostForm()
    if form.validate_on_submit():
        host = Host(
            name=form.name.data,
            macaddress=form.macaddress.data,
            ipaddress=form.ipaddress.data or "",
            port=form.port.data or 0,
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
                response = requests.get(
                    url=(
                        f"{ApiConfig.API_PROTO}://{ApiConfig.API_HOST}:"
                        "{ApiConfig.API_PORT}/mac/{host.macaddress}"
                    )
                )
                logger.debug("Response %s" % response)
                flash("Wake-on-lan packet sent to %s" % host)
            except Exception as e:
                flash("Error sending wol packet to host")
                logger.error("Raised exception %s" % e)
        return redirect(url_for("home"))
    hosts = current_user.get_hosts()
    return render_template("index.html", title="Home", hosts=hosts, form=form)


@app.route("/wake/<hostid>")
@login_required
def wake_host(hostid: int) -> str:
    try:
        host = Host.query.filter_by(id=hostid).first()
    except SQLAlchemyError as sqe:
        flash("Error querying host")
        logger.error("Raised exception %s" % sqe)
    logger.info("Waking %s" % host)
    try:
        logger.info(ApiConfig.API_PROTO, ApiConfig.API_HOST, ApiConfig.API_PORT)
        url = f"{ApiConfig.API_PROTO}://{ApiConfig.API_HOST}:{ApiConfig.API_PORT}/mac/{host.macaddress}"
        response = requests.get(url=url)
        logger.debug("Response %s" % response)
        flash("Wake-on-lan packet sent to %s" % host)
    except Exception as e:
        flash("Error sending wol packet to host")
        logger.error("Raised exception %s" % e)
    return redirect(url_for("home"))


@app.route("/hosts", methods=["GET", "POST"])
@login_required
def edit_hosts() -> str:
    form = EditHostForm()
    if form.validate_on_submit():
        host = Host(
            name=form.name.data,
            macaddress=form.macaddress.data,
            ipaddress=form.ipaddress.data or "",
            port=form.port.data or 0,
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
                    host.port = form.port.data or 0
                    host.interface = form.interface.data or ""
                    db.session.commit()
                    flash("Host updated")
                else:
                    logger.info("Adding %s" % host)
                    host = Host(
                        name=form.name.data,
                        macaddress=form.macaddress.data,
                        ipaddress=form.ipaddress.data or "",
                        port=form.port.data or 0,
                        interface=form.interface.data or "",
                        user_id=current_user.id,
                    )
                    db.session.add(host)
                    db.session.commit()
                    flash("Host added")
            except IntegrityError as ie:
                flash("Host configuration already exists, skipping")
                logger.error("Raised exception %s" % ie)
            except SQLAlchemyError as sqe:
                flash("Error adding host")
                logger.error("Raised exception %s" % sqe)
        return redirect(url_for("edit_hosts"))
    hosts = current_user.get_hosts()
    return render_template("host.html", title="Edit hosts", form=form, hosts=hosts)


@app.route("/delete/<hostid>")
@login_required
def delete_host(hostid: int) -> str:
    host = Host.query.filter_by(id=hostid).first()
    try:
        db.session.delete(host)
        logger.info("Removing %s" % host)
        db.session.commit()
    except SQLAlchemyError as sqe:
        flash("Error removing host")
        logger.error("Raised exception %s" % sqe)
    return redirect(url_for("edit_hosts"))


@app.route("/get/<hostid>")
@login_required
def get(hostid: int) -> str:
    try:
        host = Host.query.filter_by(id=hostid).first()
    except SQLAlchemyError as sqe:
        flash("Error querying host")
        logger.error("Raised exception %s" % sqe)
    return host.to_json()


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm(remember_me=True)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("home"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/loginnav", methods=["POST"])
def login_navbar() -> str:
    user = User.query.filter_by(username=request.form["navbarusername"]).first()
    if user is None or not user.check_password(request.form["navbarpassword"]):
        flash("Invalid username or password")
        return redirect(url_for("login"))
    try:
        remember = bool(request.form["navbarcheckbox"])
    except KeyError:  # if unchecked
        remember = False
    login_user(user, remember=remember)
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("You are registered.")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user", methods=["GET", "POST"])
@login_required
def edit_profile():
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


@app.route("/about")
def about():
    return render_template("about.html", title="About")
