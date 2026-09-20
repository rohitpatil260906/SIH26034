"""
Stage 4: Identity Confidence & Status Evaluator
===============================================
Computes structured multi-dimensional confidence scores and identity statuses:
- entity_confidence, role_confidence, product_confidence, category_confidence
- Statuses: CONFIRMED, PARTIAL, UNCERTAIN, NOT_VISIBLE, NEEDS_REVIEW
- Evaluates overall identity validity across any packaging panel
"""

from typing import Dict, Any, Optional, Tuple, List
from ...models import (
    Stage4ProductIdentity,
    Stage4Entity,
    Stage4ValueWithStatus,
    Stage4CategoryInfo
)


class IdentityConfidenceEvaluator:
    """Evaluates multi-dimensional confidence and determines final identity status."""

    def evaluate_identity_status(
        self,
        product_name: Stage4ValueWithStatus,
        brand: Stage4ValueWithStatus,
        category: Stage4CategoryInfo,
        entities: List[Stage4Entity],
        is_garbage_detected: bool = False
    ) -> str:
        """Determines the overall identity_status for the product."""
        if is_garbage_detected:
            return "NEEDS_REVIEW"

        has_confirmed_entity = any(e.confidence >= 0.75 for e in entities)
        has_partial_entity = any(e.partial_entity for e in entities)
        has_product = product_name.status == "CONFIRMED"
        has_brand = brand.status == "CONFIRMED"

        # If we have at least one confirmed entity (e.g. Manufacturer on back panel)
        # OR we have confirmed product_name / brand on front panel
        if has_confirmed_entity or has_product or has_brand:
            if has_partial_entity and not has_confirmed_entity:
                return "PARTIAL"
            return "CONFIRMED"

        if has_partial_entity or product_name.status == "PARTIAL":
            return "PARTIAL"

        if not entities and product_name.status == "NOT_VISIBLE" and brand.status == "NOT_VISIBLE":
            return "UNCERTAIN"

        return "CONFIRMED"
