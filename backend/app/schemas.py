"""Pydantic schemas: the shapes of the JSON our API sends back.

SQLAlchemy models (app/models.py) describe the database tables. Pydantic
schemas describe what leaves the API as JSON. Keeping them separate means we
can change the database without accidentally changing our public API.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileOut(BaseModel):
    """One file's public details, as returned to the client."""

    id: str
    filename: str
    original_size: int
    compressed_size: int | None
    file_hash: str
    upload_date: datetime
    user_id: str | None

    # from_attributes lets Pydantic build this straight from a SQLAlchemy File
    # object (reading .id, .filename, ... ) instead of needing a plain dict.
    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """What POST /api/upload returns.

    `deduplicated` is True when the uploaded file already existed and we
    returned the stored copy instead of saving a duplicate.
    """

    deduplicated: bool
    file: FileOut
