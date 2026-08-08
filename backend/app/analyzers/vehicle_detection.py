import hashlib
import random
import time
from pathlib import Path

from PIL import Image

from app.analyzers.base import BaseAnalyzer

VEHICLE_TYPES = ["private_car", "truck", "bus", "motorcycle", "other"]


class VehicleDetectionAnalyzer(BaseAnalyzer):
    """Deterministic mock: same image bytes always produce the same result
    Bounding boxes are scaled to the image's real dimensions
    so they're visually plausible when drawn over the actual image."""

    def analyze(self, image_path: Path) -> dict:
        start = time.perf_counter()

        image_bytes = image_path.read_bytes()
        seed = int(hashlib.sha256(image_bytes).hexdigest(), 16)
        # private random generator
        rng = random.Random(seed)  

        # Read image dimensions so generated bounding boxes fit inside the image
        with Image.open(image_path) as img:
            width, height = img.size

        # Generate a deterministic number of detected vehicles
        count = rng.randint(0, 8)
        detections = []
        for _ in range(count):
            box_w = rng.randint(width // 10, width // 3)
            box_h = rng.randint(height // 10, height // 3)
            x = rng.randint(0, max(width - box_w, 0))
            y = rng.randint(0, max(height - box_h, 0))
            detections.append({
                "vehicle_type": rng.choice(VEHICLE_TYPES),
                "confidence": round(rng.uniform(0.6, 0.97), 2),
                "bounding_box": {"x": x, "y": y, "width": box_w, "height": box_h},
            })

        # Count how many detections belong to each vehicle type
        by_type = {t: sum(1 for d in detections if d["vehicle_type"] == t) for t in VEHICLE_TYPES}
        elapsed_ms = int((time.perf_counter() - start) * 1000)  # real measured time

        return {
            "total_count": count,
            "count_by_type": by_type,
            "detections": detections,
            "processing_time_ms": elapsed_ms,
        }
