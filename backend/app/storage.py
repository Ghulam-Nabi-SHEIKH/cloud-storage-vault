"""File storage helpers: fingerprinting an upload and saving it to disk.

Everything here reads the upload in small chunks rather than loading the whole
file into memory at once, so even very large files stay cheap to handle.
"""

import hashlib
from pathlib import Path

from fastapi import UploadFile

# How much of the file we read at a time (1 MB). Small enough to stay memory
# friendly, big enough to be fast.
CHUNK_SIZE = 1024 * 1024

# Where saved files live. Relative to wherever the server is started from
# (the backend/ folder), so this resolves to backend/uploaded_files/.
UPLOAD_DIR = Path("uploaded_files")


async def compute_hash(upload_file: UploadFile) -> tuple[str, int]:
    """Stream the upload through SHA-256 and return (fingerprint, size_in_bytes).

    We read the file chunk by chunk, feeding each chunk into the hasher and
    counting the bytes as we go. Afterwards we rewind the file back to the
    start (seek(0)) so it can be read again when we save it.
    """
    hasher = hashlib.sha256()
    total_bytes = 0

    while True:
        chunk = await upload_file.read(CHUNK_SIZE)
        if not chunk:  # empty chunk means we've reached the end of the file
            break
        hasher.update(chunk)
        total_bytes += len(chunk)

    await upload_file.seek(0)  # rewind so save_file() can read from the start
    return hasher.hexdigest(), total_bytes


async def save_file(upload_file: UploadFile, file_hash: str) -> Path:
    """Save the upload to disk, named by its hash, and return the path.

    Naming the file by its hash means two identical files would map to the
    exact same path - which is impossible to reach in practice, because the
    dedup check stops us before we ever save a file we already have.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Keep the original file extension (.png, .jpg, ...) so later phases and
    # downloads know what kind of file this is.
    extension = Path(upload_file.filename or "").suffix
    destination = UPLOAD_DIR / f"{file_hash}{extension}"

    with destination.open("wb") as out_file:
        while True:
            chunk = await upload_file.read(CHUNK_SIZE)
            if not chunk:
                break
            out_file.write(chunk)

    return destination
