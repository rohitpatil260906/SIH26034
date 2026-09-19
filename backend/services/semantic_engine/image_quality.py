"""
Service 1: Image Quality Service
================================
Analyzes packaging label images across 14 statutory and optical dimensions:
resolution, focus/blur (Laplacian variance), contrast (std dev), brightness (mean),
noise, glare specular percentage, shadow, perspective distortion, skew angle,
estimated glyph height, margin clipping risk, background interference, and text visibility.
"""

from typing import Optional, Dict, Any
from PIL import Image

from ...models import ImageQualityMetrics
from ..cv_pipeline import analyze_complete_image_quality


class ImageQualityService:
    """Evaluates optical suitability of packaging label images."""

    def __init__(self, blur_threshold: float = 80.0, min_contrast: float = 30.0):
        self.blur_threshold = blur_threshold
        self.min_contrast = min_contrast

    def analyze_quality(self, image: Image.Image) -> ImageQualityMetrics:
        """Runs the complete 14-dimension optical quality analysis."""
        metrics = analyze_complete_image_quality(image)
        return metrics

    def is_degraded(self, metrics: ImageQualityMetrics) -> bool:
        """Determines if image is degraded enough to require NEEDS_REVIEW gating."""
        if metrics.overall_quality_score < 60:
            return True
        if metrics.is_blurred:
            return True
        if metrics.contrast is not None and metrics.contrast < self.min_contrast:
            return True
        return False
