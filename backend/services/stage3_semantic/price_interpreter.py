"""
Stage 3: Contextual Price Interpretation Service
================================================
Detects and interprets monetary amounts, currency symbols, and statutory pricing declarations:
- MRP (Maximum Retail Price)
- SALE_PRICE (Unit Sale Price, Discounted Price)
- PRICE_CANDIDATE (Isolated price with no label -> marked UNKNOWN / NEEDS_REVIEW)

CRITICAL RULE:
If only "₹299" or "Rs. 299" is visible without explicit MRP heading or context,
it MUST NOT automatically be declared MRP.
"""

import re
from typing import Tuple, List, Optional
from ...models import Stage3CandidateType


class PriceInterpretationService:
    """Interprets monetary values in accordance with packaging context."""

    PRICE_REGEX = re.compile(
        r'(?:₹|Rs\.?|INR)\s*(\d+(?:\.\d{1,2})?)',
        re.I
    )

    MRP_HEADING_REGEX = re.compile(
        r'\b(?:m\.?r\.?p\.?|maximum\s+retail\s+price|incl\.?\s*of\s*all\s*taxes)\b',
        re.I
    )

    USP_HEADING_REGEX = re.compile(
        r'\b(?:unit\s+sale\s+price|u\.?s\.?p\.?|per\s*(?:g|gm|ml|kg|l|piece|unit))\b',
        re.I
    )

    def interpret_price(
        self,
        text: str,
        section_type: str = "OTHER",
        heading_type: Optional[str] = None
    ) -> Tuple[str, str, float, List[Stage3CandidateType]]:
        """Interprets a price string in packaging context.
        
        Returns:
            (semantic_type, extracted_price_value, confidence, candidate_types)
        """
        match = self.PRICE_REGEX.search(text)
        if not match:
            return "UNKNOWN", "", 0.0, []

        full_price_token = match.group(0).strip()

        # 1. Check for Unit Sale Price (USP)
        if heading_type == "SALE_PRICE" or self.USP_HEADING_REGEX.search(text):
            return "SALE_PRICE", full_price_token, 0.96, [
                Stage3CandidateType(type="SALE_PRICE", confidence=0.96),
                Stage3CandidateType(type="MRP", confidence=0.04)
            ]

        # 2. Check for Explicit MRP heading or statutory inclusive statement
        if heading_type == "MRP" or self.MRP_HEADING_REGEX.search(text):
            return "MRP", full_price_token, 0.98, [
                Stage3CandidateType(type="MRP", confidence=0.98),
                Stage3CandidateType(type="SALE_PRICE", confidence=0.02)
            ]

        # 3. Isolated currency token without MRP label (e.g. "₹299" or "Rs. 299" alone)
        # MUST NOT automatically declare MRP!
        clean = text.strip()
        if clean.lower() == full_price_token.lower() or not re.search(r'[a-zA-Z]{3,}', clean):
            return "UNKNOWN", full_price_token, 0.50, [
                Stage3CandidateType(type="PRICE_CANDIDATE", confidence=0.55),
                Stage3CandidateType(type="MRP", confidence=0.45),
                Stage3CandidateType(type="SALE_PRICE", confidence=0.35)
            ]

        # Inconclusive
        return "UNKNOWN", full_price_token, 0.40, [
            Stage3CandidateType(type="PRICE_CANDIDATE", confidence=0.50),
            Stage3CandidateType(type="MRP", confidence=0.40)
        ]
