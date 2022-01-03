"""Auth forms."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from config import app_config
from wolproxypyweb.database.models import User


class LoginForm(FlaskForm):
    """Login form.

    This form is used to log in to the application.

    Attributes:
        username (StringField): Username.
        password (PasswordField): Password.
        remember_me (BooleanField): Remember me.

    Extends:
        FlaskForm
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Registration form.

    This form is used to register a new user.

    Attributes:
        username (StringField): Username.
        email (StringField): Email.
        password (PasswordField): Password.
        password2 (PasswordField): Password confirmation.
        is_admin (BooleanField): Whether the use is an admin.

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
            DataRequired(),
            Length(min=User.MIN_PASSWORD_LEN, max=User.MAX_PASSWORD_LEN),
        ],
    )
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    if app_config["ADMIN_ENABLED"] == "True":
        is_admin = BooleanField("Administrator?", default=False)
    submit = SubmitField("Register")

    def validate_username(self, username: StringField) -> None:
        """Validate the username.

        Args:
            username (StringField): The username.

        Raises:
            ValidationError: If the username is not valid.

        Returns:
            None
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email: StringField) -> None:
        """Validate the email.

        Args:
            email (StringField): The email.

        Raises:
            ValidationError: If the email is not valid.

        Returns:
            None
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class ResetPasswordRequestForm(FlaskForm):
    """Reset password request form.

    This form is used to request a password reset.

    Attributes:
        email (StringField): Email.

    Extends:
        FlaskForm
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    """Reset password form.

    This form is used to reset a password.

    Attributes:
        password (PasswordField): Password.
        password_confirm (PasswordField): Password confirmation.

    Extends:
        FlaskForm
    """

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=User.MIN_PASSWORD_LEN, max=User.MAX_PASSWORD_LEN),
        ],
    )
    password_confirm = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Request Password Reset")
