import hashlib
import random
import time
from pathlib import Path

from app.analyzers.base import BaseAnalyzer

VEHICLE_TYPES = ["private_car", "truck", "bus", "motorcycle", "other"]


class VehicleDetectionAnalyzer(BaseAnalyzer):
    """Deterministic mock: same image bytes always produce the same result
    Bounding boxes are normalized (0-1 fractions of the image's width and
    height), not pixel coordinates, so the frontend can position them with
    CSS percentages without needing to know the image's real size."""

    def analyze(self, image_path: Path) -> dict:
        start = time.perf_counter()

        image_bytes = image_path.read_bytes()
        seed = int(hashlib.sha256(image_bytes).hexdigest(), 16)
        # private random generator
        rng = random.Random(seed)

        # Generate a deterministic number of detected vehicles
        count = rng.randint(0, 8)
        detections = []
        for _ in range(count):
            box_w = round(rng.uniform(0.1, 0.33), 3)
            box_h = round(rng.uniform(0.1, 0.33), 3)
            x = round(rng.uniform(0, 1 - box_w), 3)
            y = round(rng.uniform(0, 1 - box_h), 3)
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
