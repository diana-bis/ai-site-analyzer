"""
Builds the test images that test cases reference by name
"""

import io

from PIL import Image, ImageFilter

from backend_link import MAX_FILE_SIZE_BYTES


def _save(img, image_format):
    buf = io.BytesIO()
    img.save(buf, format=image_format)
    return buf.getvalue()


def _valid_jpeg():
    img = Image.new("RGB", (200, 200), color=(120, 130, 140))
    return _save(img, "JPEG"), "image/jpeg", "valid.jpg"


def _valid_png():
    img = Image.new("RGB", (200, 200), color=(120, 130, 140))
    return _save(img, "PNG"), "image/png", "valid.png"


def _corrupted_image():
    # Real JPEG bytes, cut off partway through - looks like an image file,
    # isn't actually readable as one.
    real_bytes, _, _ = _valid_jpeg()
    return real_bytes[: len(real_bytes) // 4], "image/jpeg", "corrupted.jpg"


def _oversized_file():
    # Content doesn't matter here - the size check runs before the bytes
    # are ever opened as an image, so this never needs to be a real photo.
    return b"0" * (MAX_FILE_SIZE_BYTES + 1), "image/jpeg", "oversized.jpg"


def _undersized_file():
    # Not empty, but nowhere near a real image - fails the "is this
    # actually readable" check, not the size check.
    return b"tiny", "image/jpeg", "tiny.jpg"


def _text_file_renamed_jpg():
    return b"This is plain text, not an image.", "image/jpeg", "fake.jpg"


def _dark_image():
    img = Image.new("RGB", (200, 200), color=(10, 10, 10))
    return _save(img, "JPEG"), "image/jpeg", "dark.jpg"


def _blurred_image():
    img = Image.new("RGB", (200, 200), color=(200, 200, 200))
    img.paste(Image.new("RGB", (20, 20), color=(0, 0, 0)), (90, 90))
    blurred = img.filter(ImageFilter.GaussianBlur(radius=10))
    return _save(blurred, "JPEG"), "image/jpeg", "blurred.jpg"


_BUILDERS = {
    "valid_jpeg": _valid_jpeg,
    "valid_png": _valid_png,
    "corrupted_image": _corrupted_image,
    "oversized_file": _oversized_file,
    "undersized_file": _undersized_file,
    "text_file_renamed_jpg": _text_file_renamed_jpg,
    "dark_image": _dark_image,
    "blurred_image": _blurred_image,
}


def build_fixture(name):
    """Returns (file_bytes, content_type, filename) for a fixture name."""
    return _BUILDERS[name]()
