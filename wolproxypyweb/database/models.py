"""ORM classes for the flaskr application."""

from hashlib import md5

from flask_login import UserMixin
from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from config import logger
from wolproxypyweb import db, login

# Workaround for mypy,
# see https://github.com/dropbox/sqlalchemy-stubs/issues/76#issuecomment-595839159
BaseModel: DefaultMeta = db.Model


class User(UserMixin, BaseModel):
    """ORM class for the users table.

    Attributes:
        id (int): The unique identifier for the user.
        email (str): The email address of the user. Maximum length is 120.
        name (str): The name of the user. Max length is 80 characters.
        password_hash (str): The hashed password for the user.
    """

    MIN_USERNAME_LEN = 3
    MAX_USERNAME_LEN = 64
    MIN_PASSWORD_LEN = 5
    MAX_PASSWORD_LEN = 128
    MAX_EMAIL_LEN = 320

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(MAX_USERNAME_LEN), index=True, unique=True)
    email = db.Column(db.String(MAX_EMAIL_LEN), index=True, unique=True)
    password_hash = db.Column(db.String(MAX_PASSWORD_LEN))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username: str, email: str, password: str, is_admin: bool) -> None:
        """Initialize a new user.

        Args:
            username (str): The username for the user.
            email (str): The email for the user.
            password (str): The password for the user.
            is_admin (bool): True if the user is an admin.

        Returns:
            None
        """
        self.email = email
        self.username = username
        self.set_password(password)
        self.is_admin = is_admin

    def __eq__(self, other: object) -> bool:
        """Compare two users.

        Args:
            other (object): The other to compare to.

        Returns:
            equal (bool): True if the ids are equal.
        """
        equal = False
        if isinstance(other, User):
            equal = self.id == other.id
        return equal

    def set_password(self, password: str) -> None:
        """Set the hased password for the user.

        Args:
            password (str): The password to hash.

        Returns:
            None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the password matches the hashed password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches the hashed password.
        """
        return check_password_hash(self.password_hash, password)

    def get_hosts(self) -> list:
        """Get all hosts for the user.

        Args:
            None

        Returns:
            list[Hosts]: A list of all hosts for the user.
        """
        hosts = Host.query.filter_by(user_id=self.id)
        return hosts

    def get_avatar(self, size: int) -> str:
        """Get the avatar for the user.

        Args:
            size (int): The size of the avatar
        """
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()  # nosec
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def __repr__(self) -> str:
        """Get a string representation of the user.

        Returns:
            str: The string representation of the user.
        """
        return f"User {self.username}[{self.id}] <{self.email}>"


@login.user_loader
def load_user(id: int) -> User:
    """Load a user from the database.

    Args:
        id (int): The unique identifier for the user.

    Returns:
        User: The user with the given id.
    """
    return User.query.get(int(id))


class Host(BaseModel):
    """ORM class for the hosts table.

    Attributes:
        id (int): The unique identifier for the host.
        name (str): The name of the host. Max length is 80 characters.
        macaddress (str): The MAC address of the host to wake up. Max length is 18 characters.
        port (int): The port number to send the wol packet to.
        ipaddress (str): The IP address of the host. Max length is 16 characters.
        interface (str): The ip address of the network adapter to route the magic packet through.
                         Max length is 16 characters.
        user_id (int): The user id of the user who add the host. Foreign key to the users table.
    """

    MAX_HOSTNAME_LEN = 63
    MIN_HOSTNAME_LEN = 2
    MIN_MACADDRESS_LEN = 12
    MAX_MACADDRESS_LEN = 17
    IPADDRESS_LEN = 16
    MIN_PORT = 1
    MAX_PORT = 65535

    __tablename__ = "hosts"
    __table_args__ = (UniqueConstraint("name", "macaddress", "port", "ipaddress", "interface"),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_HOSTNAME_LEN))
    macaddress = db.Column(db.String(MAX_MACADDRESS_LEN))
    port = db.Column(db.Integer)
    ipaddress = db.Column(db.String(IPADDRESS_LEN))
    interface = db.Column(db.String(IPADDRESS_LEN))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(
        self,
        name: str,
        macaddress: str,
        user_id: int,
        ipaddress: str = "",
        port: int = 9,
        interface: str = "",
    ) -> None:
        """Initialize a new host."""
        self.name = name
        self.macaddress = macaddress
        self.port = port
        self.ipaddress = ipaddress
        self.interface = interface
        self.user_id = user_id

    def to_json(self) -> dict:
        """Convert the host to a json object.

        Args:
            None

        Returns:
            dict: The host as a json object.
        """
        return {
            "id": self.id,
            "name": self.name,
            "macaddress": self.macaddress,
            "port": self.port,
            "ipaddress": self.ipaddress,
            "interface": self.interface,
            "user_id": self.user_id,
        }

    def __repr__(self) -> str:
        """Get a string representation of the host.

        Returns:
            str: The string representation of the host.
        """
        return f"Host {self.name} <Mac: {self.macaddress}, port: {self.port} IP: {self.ipaddress}, interface: {self.interface}>"


logger.info("ORM classes loaded.")
