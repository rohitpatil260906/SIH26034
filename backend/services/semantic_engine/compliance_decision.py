"""
Service 17: Compliance Decision Engine
======================================
Synthesizes inspection findings into statutory compliance decisions:
- COMPLIANT: All applicable Legal Metrology rules satisfied with verified evidence.
- NON_COMPLIANT: Verified statutory defect with penal citation, compounding fee, and evidence crop.
- NEEDS_REVIEW: Ambiguous candidates or degraded image without false violation assertion.
- Calculates official compliance percentage (0-100%).
"""

from typing import List, Dict, Any, Tuple, Optional

from ...models import (
    ComplianceCheckItem,
    UniversalFieldObject,
    LmCompassViolationItem,
    LmCompassComplianceItem,
    LmCompassNeedsReviewItem,
    LmCompassResult,
    UniversalComplianceStatus
)


class ComplianceDecisionEngine:
    """Final decision gate for statutory compliance determination."""

    def __init__(self):
        pass

    def formulate_decision(
        self,
        checks: List[ComplianceCheckItem],
        universal_fields: List[UniversalFieldObject],
        is_image_degraded: bool = False
    ) -> Tuple[str, int, List[LmCompassViolationItem], List[LmCompassNeedsReviewItem]]:
        """Determines final compliance status, score, violations, and review queues."""
        failed_checks = [c for c in checks if c.status == "FAIL"]
        review_checks = [c for c in checks if c.status == "NEEDS REVIEW"]

        violations: List[LmCompassViolationItem] = []
        needs_review: List[LmCompassNeedsReviewItem] = []

        # 1. Process active violations
        for f in failed_checks:
            violations.append(LmCompassViolationItem(
                violation=f"{f.rule_no}: {f.rule_title}",
                rule=f.rule_no,
                evidence_text=f.detected_declaration,
                evidence_bbox=f.bounding_box,
                explanation=f.statutory_requirement,
                confidence=f.confidence
            ))

        # 2. Process needs review items
        for r in review_checks:
            needs_review.append(LmCompassNeedsReviewItem(
                uncertain_field=r.rule_title,
                reason=r.statutory_requirement,
                bbox=r.bounding_box,
                suggested_action="Officer optical review required."
            ))

        for u in universal_fields:
            if u.status == "NEEDS_REVIEW":
                needs_review.append(LmCompassNeedsReviewItem(
                    uncertain_field=u.selected_field,
                    reason=u.reason,
                    bbox=u.evidence_bbox,
                    suggested_action="Verify physical label declaration against candidate fields."
                ))

        # 3. Determine Overall Status
        if is_image_degraded and not failed_checks:
            overall_status = UniversalComplianceStatus.NEEDS_REVIEW
            score = 65
        elif failed_checks:
            overall_status = UniversalComplianceStatus.NON_COMPLIANT
            # Penalty deduction
            score = max(20, 100 - len(failed_checks) * 12)
        elif needs_review:
            overall_status = UniversalComplianceStatus.NEEDS_REVIEW
            score = 80
        else:
            overall_status = UniversalComplianceStatus.COMPLIANT
            score = 100

        return overall_status, score, violations, needs_review
