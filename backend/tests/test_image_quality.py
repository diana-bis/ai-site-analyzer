from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageFilter

from app.analyzers.image_quality import (
    BLUR_VARIANCE_THRESHOLD,
    DARKNESS_MEAN_THRESHOLD,
    ImageQualityAnalyzer,
)

analyzer = ImageQualityAnalyzer()

def _save(img: Image.Image, path: Path) -> Path:
    img.save(path)
    return path


def _checkerboard(size: int = 200, step: int = 20) -> Image.Image:
    # Create a high-contrast checkerboard image
    # It contains many sharp edges, making it useful for blur testing
    arr = np.zeros((size, size), dtype=np.uint8)
    arr[::step, :] = 255
    arr[:, ::step] = 255
    return Image.fromarray(arr).convert("RGB")


def test_flat_image_blur_score_near_zero(tmp_path):
    # A completely uniform image has no edges,
    # so its blur score should be close to zero
    path = _save(Image.new("RGB", (200, 200), color=(150, 150, 150)), tmp_path / "flat.png")
    result = analyzer.analyze(path)
    assert result["blur_score"] < 1.0


def test_sharp_image_scores_above_blurred(tmp_path):
    sharp_path = _save(_checkerboard(), tmp_path / "sharp.png")
    # Create a blurred version of the same image
    with Image.open(sharp_path) as sharp_img:
        blurred_img = sharp_img.filter(ImageFilter.GaussianBlur(radius=8))
    blurred_path = _save(blurred_img, tmp_path / "blurred.png")

    sharp_result = analyzer.analyze(sharp_path)
    blurred_result = analyzer.analyze(blurred_path)

    # Sharp images should produce a much higher blur score
    assert sharp_result["blur_score"] > blurred_result["blur_score"] * 10


def test_dark_image_is_flagged(tmp_path):
    # Very dark images should be detected as dark
    path = _save(Image.new("RGB", (100, 100), color=(10, 10, 10)), tmp_path / "dark.png")
    assert analyzer.analyze(path)["is_dark"] is True


def test_normal_image_not_flagged_dark(tmp_path):
    # Normally lit images should not be flagged as dark
    path = _save(Image.new("RGB", (100, 100), color=(150, 150, 150)), tmp_path / "normal.png")
    assert analyzer.analyze(path)["is_dark"] is False


def test_darkness_threshold_boundary(tmp_path):
    # Test values just below and just above the darkness threshold
    below = int(DARKNESS_MEAN_THRESHOLD) - 1
    above = int(DARKNESS_MEAN_THRESHOLD) + 1

    dark_path = _save(Image.new("RGB", (50, 50), color=(below,) * 3), tmp_path / "below.png")
    lit_path = _save(Image.new("RGB", (50, 50), color=(above,) * 3), tmp_path / "above.png")

    assert analyzer.analyze(dark_path)["is_dark"] is True
    assert analyzer.analyze(lit_path)["is_dark"] is False


@pytest.mark.parametrize("fixture_name", ["sharp", "blurred", "flat"])
def test_is_blurry_matches_threshold_comparison(tmp_path, fixture_name):
    if fixture_name == "sharp":
        img = _checkerboard()
    elif fixture_name == "blurred":
        img = _checkerboard().filter(ImageFilter.GaussianBlur(radius=8))
    else:
        img = Image.new("RGB", (200, 200), color=(150, 150, 150))

    path = _save(img, tmp_path / f"{fixture_name}.png")
    result = analyzer.analyze(path)
    
    # Verify that the boolean flag matches the threshold logic
    assert result["is_blurry"] == (result["blur_score"] < BLUR_VARIANCE_THRESHOLD)
