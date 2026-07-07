from fastapi import Depends, FastAPI, File, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, storage
from app.database import Base, engine, get_db
from app.schemas import FileOut, UploadResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud File Optimizer & Smart Vault")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Accept a file upload, deduplicating by content fingerprint.

    We fingerprint the file first, then look for that fingerprint in the
    database. If it's already there, we return the existing record and never
    touch the disk. If it's new, we save it and record it.
    """
    file_hash, size = await storage.compute_hash(file)

    existing = (
        db.query(models.File)
        .filter(models.File.file_hash == file_hash)
        .first()
    )
    if existing is not None:
        return UploadResponse(deduplicated=True, file=FileOut.model_validate(existing))

    # New file: save it to disk, then record its details in the database.
    await storage.save_file(file, file_hash)

    record = models.File(
        filename=file.filename,
        original_size=size,
        file_hash=file_hash,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except IntegrityError:
        # Two identical new files uploaded at nearly the same time can both pass
        # the check above, then collide on the file_hash unique constraint. The
        # database is the final guard: roll back and return the record that won.
        db.rollback()
        existing = (
            db.query(models.File)
            .filter(models.File.file_hash == file_hash)
            .first()
        )
        return UploadResponse(deduplicated=True, file=FileOut.model_validate(existing))

    return UploadResponse(deduplicated=False, file=FileOut.model_validate(record))
