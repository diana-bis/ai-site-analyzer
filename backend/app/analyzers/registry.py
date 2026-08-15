# The only place that knows all concrete analyzers.
# Callers use get_analyzer() and talk to BaseAnalyzer only - adding a 4th
# analyzer means one new dict entry, no caller ever changes.
from app.analyzers.base import BaseAnalyzer
from app.analyzers.classification import ClassificationAnalyzer
from app.analyzers.image_quality import ImageQualityAnalyzer
from app.analyzers.vehicle_detection import VehicleDetectionAnalyzer

# Keys match app.config.ANALYSIS_TYPES. Instances are module-level singletons
# since analyzers are stateless — safe to share across every request.
ANALYZER_REGISTRY: dict[str, BaseAnalyzer] = {
    "classification": ClassificationAnalyzer(),
    "vehicle_detection": VehicleDetectionAnalyzer(),
    "image_quality": ImageQualityAnalyzer(),
}


def get_analyzer(analysis_type: str) -> BaseAnalyzer:
    try:
        return ANALYZER_REGISTRY[analysis_type]
    except KeyError:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
