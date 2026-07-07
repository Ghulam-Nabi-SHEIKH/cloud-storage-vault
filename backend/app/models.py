import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


def _new_id() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=_new_id)
    filename = Column(String, nullable=False)
    original_size = Column(Integer, nullable=False)
    compressed_size = Column(Integer, nullable=True)
    file_hash = Column(String, nullable=False, unique=True, index=True)
    upload_date = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    # Nullable for now - populated once Phase 6 (auth) adds real user accounts.
    user_id = Column(String, nullable=True)
