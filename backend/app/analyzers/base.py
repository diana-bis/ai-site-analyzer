from abc import ABC, abstractmethod
from pathlib import Path


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, image_path: Path) -> dict:
        """Run the analysis and return a result dict matching this
        analyzer's expected shape. Raises on unreadable/corrupted images."""
        ...
