import io

import pytest
from PIL import Image

from app.services.file_validation import (
    ALLOWED_CONTENT_TYPES,
    MAX_FILE_SIZE_BYTES,
    FileValidationError,
    validate_image_file,
)


def _real_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (50, 50), color=(80, 80, 80)).save(buf, format="JPEG")
    return buf.getvalue()


def _real_png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (50, 50), color=(80, 80, 80)).save(buf, format="PNG")
    return buf.getvalue()


def test_valid_jpeg_accepted():
    # A valid JPEG should pass validation without raising an exception
    validate_image_file("image/jpeg", _real_jpeg_bytes())  


def test_valid_png_accepted():
    # A valid PNG should pass validation without raising an exception
    validate_image_file("image/png", _real_png_bytes())  


def test_empty_file_rejected():
    with pytest.raises(FileValidationError, match="empty"):
        validate_image_file("image/jpeg", b"")


def test_oversized_file_rejected():
    oversized = b"0" * (MAX_FILE_SIZE_BYTES + 1)
    with pytest.raises(FileValidationError, match="too large"):
        validate_image_file("image/jpeg", oversized)


def test_unsupported_content_type_rejected():
    with pytest.raises(FileValidationError, match="Unsupported file type"):
        validate_image_file("image/gif", _real_png_bytes())


def test_text_file_renamed_to_jpg_is_rejected():
    # Simulate a file that claims to be JPEG but actually contains plain text
    fake_bytes = b"this is plain text, not an image"
    with pytest.raises(FileValidationError, match="could not be read as a valid image"):
        validate_image_file("image/jpeg", fake_bytes)


def test_truncated_image_rejected():
    # simulate a corrupted file
    truncated = _real_png_bytes()[:20]
    with pytest.raises(FileValidationError, match="could not be read as a valid image"):
        validate_image_file("image/png", truncated)


def test_allowed_content_types_are_the_documented_three():
    # Guards against silently adding/removing a type without updating
    # the spec-facing "Allowed: JPEG, PNG, WEBP" error message.
    assert ALLOWED_CONTENT_TYPES == {"image/jpeg", "image/png", "image/webp"}
