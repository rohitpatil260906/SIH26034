"""
Stage 3: Ambiguity Resolver & Strict No-Hallucination Policy
============================================================
Handles ambiguous or low-confidence semantic candidates:
- If confidence is insufficient (< 0.60) or multiple candidates compete closely:
  semantic_type = UNKNOWN
  status = NEEDS_REVIEW
  preserves candidate_types with respective confidence scores
- NEVER converts ambiguity or missing data into a violation
- Strictly enforces NO-HALLUCINATION: never invents companies, prices, or dates
"""

from typing import List, Tuple
from ...models import Stage3SemanticField, Stage3CandidateType


class AmbiguityResolverService:
    """Evaluates semantic field candidates for ambiguity and applies conservative safety gating."""

    def resolve_ambiguity(
        self,
        fields: List[Stage3SemanticField]
    ) -> Tuple[List[Stage3SemanticField], List[Stage3SemanticField]]:
        """Separates confirmed high-confidence fields from ambiguous/needs-review fields.
        
        Returns:
            (confirmed_fields, ambiguous_fields)
        """
        confirmed: List[Stage3SemanticField] = []
        ambiguous: List[Stage3SemanticField] = []

        for field in fields:
            # Check for ambiguity conditions:
            # 1. semantic_type is explicitly UNKNOWN, PRICE_CANDIDATE, or OTHER
            # 2. semantic_confidence < 0.60
            # 3. Two candidates compete closely under moderate confidence (< 0.80)
            is_ambiguous = False

            if field.semantic_type in ("UNKNOWN", "PRICE_CANDIDATE", "OTHER"):
                is_ambiguous = True

            elif field.semantic_confidence < 0.60:
                is_ambiguous = True

            elif field.semantic_confidence < 0.80 and len(field.candidate_types) >= 2:
                sorted_cands = sorted(field.candidate_types, key=lambda c: c.confidence, reverse=True)
                if abs(sorted_cands[0].confidence - sorted_cands[1].confidence) < 0.10:
                    is_ambiguous = True

            if is_ambiguous:
                field.status = "NEEDS_REVIEW"
                ambiguous.append(field)
            else:
                field.status = "CONFIRMED"
                confirmed.append(field)

        return confirmed, ambiguous
