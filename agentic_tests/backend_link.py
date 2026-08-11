"""
Makes backend configuration constants available to the test suite.

This avoids duplicating values (such as supported analysis types or file
limits) between the backend and the tests.
"""

import sys
from pathlib import Path

# Add the backend folder to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import ANALYSIS_TYPES, IMAGE_SOURCES, settings
from app.services.file_validation import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE_BYTES

# Where uploaded images live on disk.
# Used only by the missing_image_file_handling flow, which needs real
# filesystem access to delete a file the same way a disk failure would.
UPLOADS_DIR = settings.uploads_dir
