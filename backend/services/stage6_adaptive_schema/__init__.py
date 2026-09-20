"""
Stage 6: Universal Product-Specific Detection + Adaptive Schema Engine
========================================================================
Master orchestrator for Stage 6:
- Classifies product into primary categories (FOOD, COSMETIC, ELECTRONICS, TEXTILE, FOOTWEAR, TOYS, etc.)
- Preserves multi-candidate category possibilities when evidence is ambiguous
- Constructs adaptive product schema assigning explicit field status:
  PRESENT, NOT_VISIBLE, NOT_APPLICABLE, UNKNOWN, NEEDS_REVIEW
- Differentiates ambiguous numerical values (Serving Size vs Net Qty vs Tech Weight vs Dimensions)
- Preserves strict zero-hallucination policy and legal separation
- Supports multiple product instances (product_001, product_002) in a single capture
"""

import uuid
import time
from typing import List, Dict, Any, Optional, Tuple

from ...models import (
    Stage1Response,
    Stage2Response,
    Stage3Response,
    Stage4Response,
    Stage4ProductIdentity,
    Stage6Response,
    Stage6SingleProductProfile,
    Stage6ProductProfile
)
from .category_classifier import CategoryClassifier
from .adaptive_schema_engine import AdaptiveSchemaEngine


class Stage6Pipeline:
    """Master pipeline orchestrator for Stage 6 Universal Product-Specific Adaptive Schema Engine."""

    def __init__(self):
        self.category_classifier = CategoryClassifier()
        self.adaptive_schema_engine = AdaptiveSchemaEngine()

    def process_from_stages(
        self,
        stage4_output: Optional[Stage4Response] = None,
        stage3_output: Optional[Stage3Response] = None,
        stage2_output: Optional[Stage2Response] = None,
        stage1_output: Optional[Stage1Response] = None
    ) -> Stage6Response:
        """Processes outputs from previous stages and generates Stage6Response JSON."""
        
        scan_id = (
            stage4_output.scan_id.replace("STAGE4", "STAGE6") if stage4_output
            else (stage3_output.scan_id.replace("STAGE3", "STAGE6") if stage3_output
            else f"STAGE6-{uuid.uuid4().hex[:10].upper()}")
        )

        products_input: List[Tuple[str, Optional[Stage4ProductIdentity]]] = []

        if stage4_output and stage4_output.products:
            for idx, prod in enumerate(stage4_output.products):
                pid = f"product_{idx+1:03d}"
                products_input.append((pid, prod))
        elif stage4_output and stage4_output.identity:
            products_input.append(("product_001", stage4_output.identity))
        else:
            products_input.append(("product_001", None))

        single_profiles: List[Stage6SingleProductProfile] = []
        imported_any = False
        overall_status = "COMPLETED"

        for pid, prod_identity in products_input:
            # 1. Classify Category & Subcategory
            profile = self.category_classifier.classify_product(
                stage4_output=stage4_output,
                stage3_output=stage3_output,
                stage2_output=stage2_output,
                stage1_output=stage1_output,
                product_identity=prod_identity
            )

            if profile.category_status == "NEEDS_REVIEW":
                overall_status = "NEEDS_REVIEW"

            # 2. Build Adaptive Schema
            single_profile = self.adaptive_schema_engine.build_adaptive_schema(
                product_id=pid,
                profile=profile,
                stage4_output=stage4_output,
                stage3_output=stage3_output,
                stage2_output=stage2_output,
                stage1_output=stage1_output,
                product_identity=prod_identity
            )

            # Check imported signals
            for field in single_profile.adaptive_schema.fields:
                if field.field_name in ("IMPORTER", "COUNTRY_OF_ORIGIN") and field.status == "PRESENT":
                    imported_any = True

            single_profiles.append(single_profile)

        message = (
            f"Stage 6 completed. Extracted adaptive schemas for {len(single_profiles)} product(s). "
            f"Primary Category: {single_profiles[0].product_profile.category} "
            f"({single_profiles[0].product_profile.category_confidence:.2f})."
        )

        return Stage6Response(
            scan_id=scan_id,
            status=overall_status,
            products=single_profiles,
            imported_product_detected=imported_any,
            message=message
        )
