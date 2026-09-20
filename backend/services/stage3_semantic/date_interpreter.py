"""
Stage 3: Contextual Date Interpretation Service
===============================================
Interprets date declarations and shelf-life statements:
- MANUFACTURING_DATE (e.g. "Mfg Date: 10/2024", "Mfd: 08/2026")
- PACKING_DATE (e.g. "Pkg Date: 05/2024", "PKD: 01/2025")
- EXPIRY_DATE (e.g. "Expiry Date: 10/2026", "EXP: 07/2028")
- BEST_BEFORE_DATE / SHELF_LIFE (e.g. "Best Before 24 Months")
- UNKNOWN (e.g. "08/2026" alone without context -> status NEEDS_REVIEW)
"""

import re
from typing import Tuple, List, Optional
from ...models import Stage3CandidateType


class DateInterpretationService:
    """Interprets date strings and shelf-life statements based on visible context."""

    DATE_REGEX = re.compile(
        r'\b(?:(?:0?[1-9]|[12][0-9]|3[01])[/\-\.](?:0?[1-9]|1[0-2])[/\-\.](?:20\d{2}|\d{2})|(?:0?[1-9]|1[0-2])[/\-\.](?:20\d{2}|\d{2})|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\.\-]+(?:20\d{2}|\d{2}))\b',
        re.I
    )

    SHELF_LIFE_REGEX = re.compile(
        r'\b(?:best\s+before\s*(?:within\s*)?\d+\s*(?:months?|days?|years?)|shelf\s+life\s*(?:is\s*)?\d+\s*(?:months?|days?|years?))\b',
        re.I
    )

    def interpret_date(
        self,
        text: str,
        section_type: str = "OTHER",
        heading_type: Optional[str] = None
    ) -> Tuple[str, str, float, List[Stage3CandidateType]]:
        """Interprets dates and durations based on packaging context.
        
        Returns:
            (semantic_type, extracted_date_value, confidence, candidate_types)
        """
        # 1. Shelf-life statement e.g. "Best Before 24 Months"
        shelf_match = self.SHELF_LIFE_REGEX.search(text)
        if shelf_match:
            return "BEST_BEFORE_DATE", shelf_match.group(0).strip(), 0.98, [
                Stage3CandidateType(type="BEST_BEFORE_DATE", confidence=0.98),
                Stage3CandidateType(type="EXPIRY_DATE", confidence=0.02)
            ]

        date_match = self.DATE_REGEX.search(text)
        if not date_match:
            # Check if there is an explicit "Best Before" text with months
            if re.search(r'\bbest\s+before\b', text, re.I) and re.search(r'\b\d+\s*months?\b', text, re.I):
                return "BEST_BEFORE_DATE", text.strip(), 0.96, [
                    Stage3CandidateType(type="BEST_BEFORE_DATE", confidence=0.96)
                ]
            return "UNKNOWN", "", 0.0, []

        date_token = date_match.group(0).strip()

        # 2. Contextual heading evaluation
        if heading_type == "MANUFACTURING_DATE" or re.search(r'\b(?:mfg|mfd|date\s+of\s+mfg|manufactured)\b', text, re.I):
            return "MANUFACTURING_DATE", date_token, 0.98, [
                Stage3CandidateType(type="MANUFACTURING_DATE", confidence=0.98),
                Stage3CandidateType(type="PACKING_DATE", confidence=0.02)
            ]

        if heading_type == "PACKING_DATE" or re.search(r'\b(?:pkd|packed|pkg|date\s+of\s+pkd)\b', text, re.I):
            return "PACKING_DATE", date_token, 0.98, [
                Stage3CandidateType(type="PACKING_DATE", confidence=0.98),
                Stage3CandidateType(type="MANUFACTURING_DATE", confidence=0.02)
            ]

        if heading_type == "EXPIRY_DATE" or re.search(r'\b(?:exp|expiry|use\s+by|use\s+before)\b', text, re.I):
            return "EXPIRY_DATE", date_token, 0.98, [
                Stage3CandidateType(type="EXPIRY_DATE", confidence=0.98),
                Stage3CandidateType(type="BEST_BEFORE_DATE", confidence=0.02)
            ]

        if heading_type == "BEST_BEFORE_DATE" or re.search(r'\bbest\s+before\b', text, re.I):
            return "BEST_BEFORE_DATE", date_token, 0.95, [
                Stage3CandidateType(type="BEST_BEFORE_DATE", confidence=0.95),
                Stage3CandidateType(type="EXPIRY_DATE", confidence=0.05)
            ]

        # 3. Standalone date without context (e.g. "08/2026" alone)
        # MUST NOT guess whether it is Mfg or Expiry!
        clean = text.strip()
        if clean.lower() == date_token.lower() or not re.search(r'[a-zA-Z]{3,}', clean):
            return "UNKNOWN", date_token, 0.40, [
                Stage3CandidateType(type="MANUFACTURING_DATE", confidence=0.45),
                Stage3CandidateType(type="EXPIRY_DATE", confidence=0.45),
                Stage3CandidateType(type="PACKING_DATE", confidence=0.10)
            ]

        return "UNKNOWN", date_token, 0.35, [
            Stage3CandidateType(type="DATE", confidence=0.40)
        ]
