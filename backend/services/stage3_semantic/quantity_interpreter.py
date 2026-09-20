"""
Stage 3: Contextual Quantity Interpretation Service
===================================================
Never classifies numbers or quantities in isolation.
Understands:
- g, kg, mg, ml, L, cm, mm, m, pcs, pieces, count, tablets, capsules, units, pair, set

Distinguishes:
- NET_QUANTITY (e.g. "Net Quantity: 50 g", "Net Wt: 200 g")
- SERVING_SIZE (e.g. "Serving Size: 50 g", table serving row)
- INGREDIENT_QUANTITY (e.g. "Vitamin C 50 mg", "Zinc 10 mg" in Ingredients)
- DIMENSION / TECHNICAL_SPECIFICATION (e.g. "10 mm", "Length: 15 cm")
- UNKNOWN (e.g. "500 mg" alone without context -> status NEEDS_REVIEW)
"""

import re
from typing import Dict, Any, Tuple, Optional, List
from ...models import Stage3CandidateType


class QuantityInterpretationService:
    """Interprets quantities based on surrounding lexical and spatial context."""

    QUANTITY_REGEX = re.compile(
        r'\b(\d+(?:\.\d+)?)\s*(kg|kgs|g|gm|gms|mg|l|ltr|ltrs|ml|m1|cm|mm|m|pcs|pieces?|units?|tablets?|capsules?|count|pair|set)\b',
        re.I
    )

    DIMENSION_REGEX = re.compile(
        r'\b(?:\d+(?:\.\d+)?\s*(?:cm|mm|m|in|inch)\s*[xX*]\s*)+\d+(?:\.\d+)?\s*(?:cm|mm|m|in|inch)\b',
        re.I
    )

    def interpret_quantity(
        self,
        text: str,
        section_type: str = "OTHER",
        heading_type: Optional[str] = None,
        heading_text: Optional[str] = None
    ) -> Tuple[str, str, float, List[Stage3CandidateType]]:
        """Interprets a quantity token in context.
        
        Returns:
            (semantic_type, extracted_quantity_value, confidence, candidate_types)
        """
        match = self.QUANTITY_REGEX.search(text)
        dim_match = self.DIMENSION_REGEX.search(text)

        if not match and not dim_match:
            return "UNKNOWN", "", 0.0, []

        val_str = dim_match.group(0) if dim_match else match.group(0)

        # 1. INGREDIENTS Section Shield
        # If the quantity is inside an INGREDIENTS section:
        if section_type == "INGREDIENTS":
            return "INGREDIENT_QUANTITY", val_str, 0.95, [
                Stage3CandidateType(type="INGREDIENT_QUANTITY", confidence=0.95),
                Stage3CandidateType(type="PRODUCT_SPECIFICATION", confidence=0.05)
            ]

        # 2. Explicit Heading Guidance
        if heading_type == "NET_QUANTITY" or re.search(r'\b(?:net\s+(?:quantity|qty|wt|volume|weight|mass))\b', text, re.I):
            return "NET_QUANTITY", val_str, 0.98, [
                Stage3CandidateType(type="NET_QUANTITY", confidence=0.98),
                Stage3CandidateType(type="SERVING_SIZE", confidence=0.02)
            ]

        if heading_type == "SERVING_SIZE" or re.search(r'\b(?:serving\s+size)\b', text, re.I):
            return "SERVING_SIZE", val_str, 0.98, [
                Stage3CandidateType(type="SERVING_SIZE", confidence=0.98),
                Stage3CandidateType(type="NET_QUANTITY", confidence=0.02)
            ]

        if section_type == "NUTRITION":
            return "SERVING_SIZE", val_str, 0.90, [
                Stage3CandidateType(type="SERVING_SIZE", confidence=0.90),
                Stage3CandidateType(type="NUTRITION_SPECIFICATION", confidence=0.85)
            ]

        # 3. Dimensions / Technical Specifications
        if dim_match or re.search(r'\b(?:dimensions?|size|chest|length|width|height|diameter|thickness)\b', text, re.I):
            return "DIMENSION", val_str, 0.95, [
                Stage3CandidateType(type="DIMENSION", confidence=0.95),
                Stage3CandidateType(type="TECHNICAL_SPECIFICATION", confidence=0.90)
            ]

        if match:
            unit = match.group(2).lower()
            if unit in ("mm", "cm", "m"):
                # Standalone linear dimension e.g. "10 mm"
                if re.search(r'\b(?:drill|cable|wire|plug|adapter|thickness|dia|spec)\b', text, re.I):
                    return "TECHNICAL_SPECIFICATION", val_str, 0.90, [
                        Stage3CandidateType(type="TECHNICAL_SPECIFICATION", confidence=0.90),
                        Stage3CandidateType(type="DIMENSION", confidence=0.85)
                    ]
                else:
                    # Ambiguous dimension without product context
                    return "UNKNOWN", val_str, 0.45, [
                        Stage3CandidateType(type="DIMENSION", confidence=0.45),
                        Stage3CandidateType(type="TECHNICAL_SPECIFICATION", confidence=0.40),
                        Stage3CandidateType(type="PRODUCT_SPECIFICATION", confidence=0.15)
                    ]

        # 4. Standalone quantity without explicit heading (e.g. "50 g" or "500 mg" alone)
        # MUST NOT automatically assume NET_QUANTITY!
        clean_text = text.strip()
        if clean_text.lower() == val_str.lower():
            # Exact match of isolated number + unit without heading
            return "UNKNOWN", val_str, 0.40, [
                Stage3CandidateType(type="NET_QUANTITY", confidence=0.45),
                Stage3CandidateType(type="SERVING_SIZE", confidence=0.40),
                Stage3CandidateType(type="PRODUCT_WEIGHT_SPECIFICATION", confidence=0.15)
            ]

        # Inconclusive
        return "UNKNOWN", val_str, 0.35, [
            Stage3CandidateType(type="NET_QUANTITY", confidence=0.35),
            Stage3CandidateType(type="OTHER_QUANTITY", confidence=0.35)
        ]
