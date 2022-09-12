import uuid

from sqlalchemy.dialects.postgresql import UUID

from services.db import db
from .role import UserRoles


class User(db.Model):
    __tablename__ = "users"

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(512))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    birth_date = db.Column(db.Date)
    roles = db.relationship(
        "Role", secondary=UserRoles, lazy="subquery",
        backref=db.backref("users", lazy=True),
    )
    history = db.relationship("History", backref="parent", passive_deletes=True, lazy="dynamic")
    superuser = db.Column(db.Boolean, default=False)
    time_zone = db.Column(db.SmallInteger, default=0)
    notification = db.Column(db.Boolean, default=True)

    @property
    def is_superuser(self):
        return self.superuser

    def __repr__(self):
        return f"<User: {self.username}>"


class SocialAccount(db.Model):
    __tablename__ = 'social_account'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.uuid"), nullable=False)
    user = db.relationship(User, backref=db.backref("social_accounts", lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (db.UniqueConstraint("social_id", "social_name", name="social_pk"),)

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"
