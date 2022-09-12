import uuid

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID

from services.db import db

UserRoles = db.Table(
    "user_roles",
    db.Column("user_uuid", UUID(as_uuid=True), db.ForeignKey("users.uuid"), primary_key=True),
    db.Column("role_uuid", UUID(as_uuid=True), db.ForeignKey("roles.uuid"), primary_key=True)
)


class Role(db.Model):
    __tablename__ = "roles"

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), unique=True)
    permission_level = db.Column(Integer, default=1)

    def __repr__(self):
        return f"<Role: {self.name}>"
