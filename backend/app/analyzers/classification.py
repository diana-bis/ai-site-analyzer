import hashlib
import random
import time
from pathlib import Path

from app.analyzers.base import BaseAnalyzer

# Possible categories that the mock classifier can return
CATEGORIES = [
    "urban_area", "road_or_intersection", "open_area", "building",
    "crowd", "vehicles", "industrial_site", "unclassified",
]


class ClassificationAnalyzer(BaseAnalyzer):
    """Deterministic mock: same image bytes always produce the same result,
    so the agentic test suite can assert expected vs actual """

    def analyze(self, image_path: Path) -> dict:
        start = time.perf_counter()

        image_bytes = image_path.read_bytes()
        # Generate a deterministic seed from the image contents.
        # Same image -> same SHA-256 hash -> same seed.
        seed = int(hashlib.sha256(image_bytes).hexdigest(), 16)
        rng = random.Random(seed)  

        # Pick the primary predicted category
        category = rng.choice(CATEGORIES)
        confidence = round(rng.uniform(0.55, 0.98), 2)
        remaining = [c for c in CATEGORIES if c != category]
        # Pick two alternative categories
        alternatives = [
            {
                "category": c, 
                "confidence": round(rng.uniform(0.05, confidence - 0.05), 2)
            }
            for c in rng.sample(remaining, k=2)
        ]

        elapsed_ms = int((time.perf_counter() - start) * 1000)  # real measured time

        # Return the mock classification result
        return {
            "category": category,
            "confidence": confidence,
            "alternatives": alternatives,
            "processing_time_ms": elapsed_ms,
        }
