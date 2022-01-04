"""Auth forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from config import app_config


class ApiForm(FlaskForm):
    """Api form.

    This form is used to save the API authentication key.

    Attributes:
        key (StringField): The API authentication token.

    Extends:
        FlaskForm
    """

    key = StringField("API authentication key", validators=[DataRequired()])
    submit = SubmitField("Save")


class SingleSignOnForm(FlaskForm):
    """Single sign on form.

    This form is used to save the SSO authentication key.

    Args:
        id (StringField): The cliet id.
        secret (StringField): The client secret.

    Extends:
        FlaskForm
    """

    id = StringField("Client id", validators=[DataRequired()])
    secret = StringField("Client secret", validators=[DataRequired()])
    submit = SubmitField("Save")
