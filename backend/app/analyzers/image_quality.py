import time
from pathlib import Path

import numpy as np
from PIL import Image

from app.analyzers.base import BaseAnalyzer

# Empirical thresholds, not derived from a formula — would need tuning
# against a real labeled dataset for production use.
BLUR_VARIANCE_THRESHOLD = 100.0
DARKNESS_MEAN_THRESHOLD = 50.0


class ImageQualityAnalyzer(BaseAnalyzer):
    """Real algorithm, not mocked: blur via variance of Laplacian, darkness
    via mean brightness. Both computed on the actual pixel data."""

    def analyze(self, image_path: Path) -> dict:
        start = time.perf_counter()

        with Image.open(image_path) as img:
            # Convert the image to grayscale so every pixel has a single brightness value
            grayscale = img.convert("L")  

            # Convert the image into a floating-point NumPy array for numerical calculations
            arr = np.asarray(grayscale, dtype=np.float64)

            # Average pixel brightness across the entire image
            brightness_score = round(float(arr.mean()), 2)
            is_dark = brightness_score < DARKNESS_MEAN_THRESHOLD

            # Compute a simple Laplacian filter to measure edge strength.
            # Sharp images have stronger edges; blurry images have weaker ones
            laplacian = (
                arr[:-2, 1:-1] + arr[2:, 1:-1]
                + arr[1:-1, :-2] + arr[1:-1, 2:]
                - 4 * arr[1:-1, 1:-1]
            )
            blur_score = round(float(laplacian.var()), 2)
            is_blurry = blur_score < BLUR_VARIANCE_THRESHOLD

        elapsed_ms = int((time.perf_counter() - start) * 1000)  # real measured time

        return {
            "is_blurry": is_blurry,
            "blur_score": blur_score,
            "is_dark": is_dark,
            "brightness_score": brightness_score,
            "quality": "poor" if (is_blurry or is_dark) else "good",
            "processing_time_ms": elapsed_ms,
        }
