import io

from PIL import Image

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
# Supported image formats
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


class FileValidationError(Exception):
    """Raised with a user-facing message; the route catches this and
    returns 400 with the message as the detail."""


def validate_image_file(content_type: str, file_bytes: bytes) -> None:
    # Reject empty uploads
    if not file_bytes:
        raise FileValidationError("Uploaded file is empty.")

    # Reject oversized files
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File too large: {len(file_bytes)} bytes (max {MAX_FILE_SIZE_BYTES})."
        )

    # Reject unsupported image formats
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise FileValidationError(
            f"Unsupported file type: {content_type}. Allowed: JPEG, PNG, WEBP."
        )

    # Verify that the uploaded bytes represent a real, readable image
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()  # raises if the file is corrupted/unreadable
    except Exception as exc:
        raise FileValidationError(f"File could not be read as a valid image: {exc}")
