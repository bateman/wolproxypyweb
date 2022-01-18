"""Define the forms for the web application."""
import re

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField
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


class EditUserProfileForm(FlaskForm):  # lgtm [py/missing-call-to-init]
    """Edit user profile form.

    This form is used to edit a user profile.

    Attributes:
        username (StringField): Username.
        email (StringField): Email.
        password (PasswordField): Password.
        password_confirm (PasswordField): Password confirmation.

    Extends:
        FlaskForm
    """

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
    password_confirm = PasswordField("Repeat Password", validators=[EqualTo("password")])
    submit = SubmitField("Update")

    def __init__(
        self,
        original_username: str,
        original_email: str,
        password: str = None,
        password_confirm: str = None,
    ) -> None:
        """Initialize the form.

        Args:
            original_username (str): The username.
            original_email (str): The email.
            password (str): The password.
            password_confirm (str): The password confirmation.

        Returns:
            None
        """
        super().__init__()
        self.original_username = original_username
        self.original_email = original_email
        self.password = password if password == "" else ""  # nosec
        self.password_confirm = password_confirm if password_confirm == "" else ""  # nosec

    def validate_username(self, username: StringField) -> None:
        """Validate the username.

        Args:
            username (StringField): The username.

        Raises:
            ValidationError: If the username is not valid.

        Returns:
            None
        """
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please, use a different username.")

    def validate_email(self, email: StringField) -> None:
        """Validate the email.

        Args:
            email (StringField): The email.

        Raises:
            ValidationError: If the email is not valid.

        Returns:
            None
        """
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError("Please, use a different email address.")


class HostForm(FlaskForm):
    """Host form.

    Attributes:
        name (StringField): The name of the host to wake.
        ip (StringField): The ip of the host.
        mac (StringField): The mac of the host.
        port (IntegerField): The port of the host.
        interface (StringField): The interface for sending the packet.

    Extends:
        FlaskForm
    """

    regex = r"^(?:[0-9A-Fa-f]{2}([:-]?)[0-9A-Fa-f]{2})(?:(?:\1|\.)(?:[0-9A-Fa-f]{2}([:-]?)[0-9A-Fa-f]{2})){2}$"

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
    port = IntegerField("Port", validators=[Optional(), NumberRange(Host.MIN_PORT, Host.MAX_PORT)])
    ipaddress = StringField("IP address", validators=[Optional(), IPAddress(ipv4=True)])
    interface = StringField("Interface", validators=[Optional(), IPAddress(ipv4=True)])


class AddHostForm(HostForm):
    """Add host form.

    Extends:
        HostForm
    """

    submit = SubmitField("Save")
    wake = SubmitField("Wake on LAN")


class EditHostForm(HostForm):
    """Edit host form.

    Extends:
        HostForm
    """

    hiddenid = HiddenField()
    submit = SubmitField("Save")
