"""
Stage 9: Review Queue Engine
============================
Creates structured review queue items for ambiguous or unconfirmed cases:
- Captures items requiring human review (INSUFFICIENT_EVIDENCE, CONFLICTING_DECLARATIONS, NOT_VISIBLE, UNKNOWN_STATUS, UNVERIFIED_RULE, AMBIGUOUS_SEMANTICS).
- Ensures ambiguous items NEVER become confirmed automatic violations.
"""

from typing import List, Dict, Any, Optional
import uuid
from .violation_models import Stage9ReviewItem, Stage9EvidenceItem, Stage8RuleEvaluation


class ReviewQueueEngine:
    """Manages creation of structured review queue items."""

    @staticmethod
    def create_review_item(
        product_id: str,
        reason: str,
        evaluation: Optional[Stage8RuleEvaluation] = None,
        description: Optional[str] = None,
        evidence: Optional[List[Stage9EvidenceItem]] = None
    ) -> Stage9ReviewItem:
        """Constructs a Stage9ReviewItem instance."""
        rule_id = evaluation.rule_id if evaluation else None
        rule_num = evaluation.rule_number if evaluation else None

        desc = description or (
            f"Rule {rule_num or rule_id} evaluation status '{evaluation.evaluation_status if evaluation else 'UNKNOWN'}' "
            f"requires manual review (Reason: {reason})."
        )

        ev_list: List[Stage9EvidenceItem] = evidence or []
        if evaluation and evaluation.evidence and not ev_list:
            for s8_ev in evaluation.evidence:
                ev_list.append(Stage9EvidenceItem(
                    image_id=s8_ev.image_id,
                    product_id=product_id,
                    panel=s8_ev.panel,
                    region_id=s8_ev.region_id,
                    original_bbox=s8_ev.bbox,
                    observed_text=s8_ev.observed_text,
                    normalized_value=s8_ev.normalized_value,
                    semantic_field=s8_ev.semantic_field,
                    evidence_confidence=s8_ev.confidence
                ))

        review_id = f"rev_{uuid.uuid4().hex[:8]}"

        return Stage9ReviewItem(
            review_id=review_id,
            product_id=product_id,
            reason=reason,
            related_rule_id=rule_id,
            related_rule_number=rule_num,
            description=desc,
            evidence=ev_list
        )
