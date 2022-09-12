import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy.dialects.postgresql import UUID, ENUM

from services.db import db


class PlatformEnum(Enum):
    pc = "pc"
    mobile = "mobile"
    tablet = "tablet"


class History(db.Model):
    __tablename__ = "user_history"
    __table_args__ = (
        {
            "postgresql_partition_by": "LIST (platform)",
        }
    )

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(), primary_key=True)
    device = db.Column(db.String(255))
    platform = db.Column(
        ENUM(PlatformEnum), nullable=False, server_default=PlatformEnum.pc.value
    )
    location = db.Column(db.String(255))
