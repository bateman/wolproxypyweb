import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, StringField, SubmitField
from wtforms.fields.simple import HiddenField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    IPAddress,
    Length,
    NumberRange,
    Optional,
    Regexp,
    ValidationError,
)

from wolproxypyweb.database.models import Host, User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=User.MIN_USERNAME_LEN, max=User.MAX_USERNAME_LEN),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=User.MIN_PASSWORD_LEN, max=User.MAX_PASSWORD_LEN),
        ],
    )
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=User.MIN_PASSWORD_LEN, max=User.MAX_PASSWORD_LEN),
        ],
    )
    password_confirm = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Request Password Reset")


class EditUserProfileForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=User.MIN_USERNAME_LEN, max=User.MAX_USERNAME_LEN),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            Optional(),
            Length(min=User.MIN_PASSWORD_LEN, max=User.MAX_PASSWORD_LEN),
        ],
    )
    password_confirm = PasswordField(
        "Repeat Password", validators=[EqualTo("password")]
    )
    submit = SubmitField("Update")

    def __init__(self, original_username: str, original_email: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please, use a different username.")

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError("Please, use a different email address.")


class HostForm(FlaskForm):
    regex = (
        r"^(?:[0-9A-Fa-f]{2}([:-]?)[0-9A-Fa-f]{2})(?:(?:\1|\.)"
        "(?:[0-9A-Fa-f]{2}([:-]?)[0-9A-Fa-f]{2})){2}$"
    )

    name = StringField(
        "Hostname",
        validators=[
            DataRequired(),
            Length(min=Host.MIN_HOSTNAME_LEN, max=Host.MAX_HOSTNAME_LEN),
        ],
    )
    macaddress = StringField(
        "MAC address",
        validators=[
            DataRequired(),
            Length(min=Host.MIN_MACADDRESS_LEN, max=Host.MAX_MACADDRESS_LEN),
            Regexp(regex=regex, flags=re.IGNORECASE),
        ],
    )
    port = IntegerField(
        "Port", validators=[Optional(), NumberRange(Host.MIN_PORT, Host.MAX_PORT)]
    )
    ipaddress = StringField("IP address", validators=[Optional(), IPAddress(ipv4=True)])
    interface = StringField("Interface", validators=[Optional(), IPAddress(ipv4=True)])


class AddHostForm(HostForm):
    submit = SubmitField("Save")
    wake = SubmitField("Wake on LAN")


class EditHostForm(HostForm):
    hiddenid = HiddenField()
    submit = SubmitField("Save")
