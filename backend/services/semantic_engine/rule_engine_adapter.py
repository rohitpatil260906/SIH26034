"""
Service 14: Legal Metrology Rule Engine Adapter
===============================================
Evaluates statutory compliance under Legal Metrology (Packaged Commodities) Rules, 2011
ONLY against verified semantic fields.
STRICT PRINCIPLE:
Never evaluate statutory rules on unverified raw OCR strings or unclassified tokens.
"""

from typing import List, Dict, Any, Tuple, Optional

from ...models import (
    StructuredProductData,
    ComplianceCheckItem,
    UniversalFieldObject,
    UniversalSemanticField
)
from ..rule_engine import evaluate_legal_metrology_rules


class LegalMetrologyRuleEngine:
    """Statutory Legal Metrology (Packaged Commodities) Rules 2011 compliance evaluator."""

    def __init__(self):
        pass

    def evaluate_compliance(
        self,
        product_data: StructuredProductData,
        universal_fields: List[UniversalFieldObject],
        surface: str = "Front (PDP)",
        is_image_degraded: bool = False,
        surfaces_processed: Optional[List[str]] = None
    ) -> Tuple[List[ComplianceCheckItem], int, str]:
        """Runs the deterministic 34-rule engine on verified semantic declarations."""
        # Ensure universal fields are attached to product_data
        product_data.universal_fields = universal_fields

        checks, score, status = evaluate_legal_metrology_rules(
            data=product_data,
            surface=surface,
            is_image_degraded=is_image_degraded,
            surfaces_processed=surfaces_processed
        )

        return checks, score, status
