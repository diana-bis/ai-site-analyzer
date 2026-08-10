"""
Makes backend configuration constants available to the test suite.

This avoids duplicating values (such as supported analysis types or file
limits) between the backend and the tests.
"""

import sys
from pathlib import Path

# Add the backend folder to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import ANALYSIS_TYPES, IMAGE_SOURCES  
from app.services.file_validation import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE_BYTES  
