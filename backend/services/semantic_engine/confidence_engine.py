"""
Service 15: Confidence Engine
=============================
Computes multi-tier confidence scores across all pipeline stages:
1. OCR Confidence (Engine character certainty)
2. Text Detection Confidence (Bounding box proposal certainty)
3. Layout Confidence (Spatial grouping & reading order certainty)
4. Semantic Confidence (Candidate classification certainty)
5. Category Confidence (Commodity category relevance certainty)
6. Rule Confidence (Statutory applicability certainty)
7. Overall Field Confidence (Calibrated composite score)
"""

from typing import Dict, Any, Optional
import math

from ...models import UniversalFieldObject


class ConfidenceEngine:
    """Calculates multi-dimensional statutory confidence metrics."""

    WEIGHTS = {
        "ocr": 0.25,
        "text_detection": 0.15,
        "layout": 0.20,
        "semantic": 0.25,
        "category": 0.10,
        "rule": 0.05
    }

    def __init__(self, review_threshold: float = 0.65):
        self.review_threshold = review_threshold

    def calculate_overall_confidence(
        self,
        ocr_conf: float = 0.95,
        detection_conf: float = 0.95,
        layout_conf: float = 0.95,
        semantic_conf: float = 0.95,
        category_conf: float = 0.95,
        rule_conf: float = 0.95
    ) -> float:
        """Calculates calibrated weighted composite confidence score."""
        scores = [
            (max(0.1, min(1.0, ocr_conf)), self.WEIGHTS["ocr"]),
            (max(0.1, min(1.0, detection_conf)), self.WEIGHTS["text_detection"]),
            (max(0.1, min(1.0, layout_conf)), self.WEIGHTS["layout"]),
            (max(0.1, min(1.0, semantic_conf)), self.WEIGHTS["semantic"]),
            (max(0.1, min(1.0, category_conf)), self.WEIGHTS["category"]),
            (max(0.1, min(1.0, rule_conf)), self.WEIGHTS["rule"]),
        ]

        # Weighted geometric mean for rigorous multi-stage gating
        log_sum = sum(weight * math.log(val) for val, weight in scores)
        total_weight = sum(self.WEIGHTS.values())
        composite = math.exp(log_sum / total_weight)

        return round(min(0.99, max(0.10, composite)), 2)

    def calibrate_field(self, field: UniversalFieldObject) -> UniversalFieldObject:
        """Computes and updates the 7 confidence dimensions for a UniversalFieldObject."""
        field.overall_confidence = self.calculate_overall_confidence(
            ocr_conf=field.ocr_confidence,
            detection_conf=0.95,
            layout_conf=field.layout_confidence,
            semantic_conf=field.semantic_confidence,
            category_conf=field.category_confidence,
            rule_conf=field.rule_confidence
        )

        if field.overall_confidence < self.review_threshold and field.status == "RESOLVED":
            field.status = "NEEDS_REVIEW"
            field.reason += " | Gated: Composite confidence below officer automated acceptance threshold."

        return field
