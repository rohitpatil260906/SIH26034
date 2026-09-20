"""
Stage 9: Violation & Evidence Engine
====================================
Master Engine converting Stage 8 verified rule evaluations into structured,
auditable violation records:
- Core Principle: "NO EVIDENCE, NO VIOLATION".
- Converts Stage 8 NON_COMPLIANT evaluations with reliable evidence into CONFIRMED violations.
- Converts ambiguous, unverified, NOT_VISIBLE, UNKNOWN, or CONFLICT evaluations into review queue items.
- Preserves original bounding boxes, panel names, and confidence scores.
- Uses FingerprintEngine and DeduplicationEngine for deterministic deduplication.
- Generates objective, factual, non-accusatory descriptions.
- Keeps multiple products strictly isolated.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from .violation_models import (
    Stage9Violation,
    Stage9EvidenceItem,
    Stage9ReviewItem,
    Stage9ViolationSummary,
    Stage9ProductViolationResult,
    Stage9Response,
    Stage8ProductEvaluation,
    Stage8RuleEvaluation,
    Stage8EvidenceItem
)
from .fingerprint_engine import FingerprintEngine
from .deduplication_engine import DeduplicationEngine
from .review_queue_engine import ReviewQueueEngine


class Stage9ViolationEngine:
    """Master Violation & Evidence Engine for Stage 9."""

    def evaluate_product_violations(
        self,
        product_eval: Stage8ProductEvaluation,
        scan_id: Optional[str] = None
    ) -> Stage9ProductViolationResult:
        """Evaluates violations for a single Stage 8 product evaluation."""
        product_id = product_eval.product_id
        violations: List[Stage9Violation] = []
        review_items: List[Stage9ReviewItem] = []

        total_evals = len(product_eval.evaluations)
        compliant_cnt = 0
        not_app_cnt = 0

        # Process each Stage 8 rule evaluation
        for r_eval in product_eval.evaluations:
            status = r_eval.evaluation_status
            app_status = r_eval.applicability_status

            if app_status == "NOT_APPLICABLE" or status == "NOT_APPLICABLE":
                not_app_cnt += 1
                continue

            if status == "COMPLIANT":
                compliant_cnt += 1
                continue

            # Handle uncertain / review statuses (NEEDS_REVIEW, CONFLICT, UNKNOWN, NOT_VISIBLE)
            if status in ("NEEDS_REVIEW", "CONFLICT", "UNKNOWN", "NOT_VISIBLE") or app_status in ("NEEDS_REVIEW", "UNKNOWN"):
                rev_reason = self._map_review_reason(status, app_status)
                rev_item = ReviewQueueEngine.create_review_item(
                    product_id=product_id,
                    reason=rev_reason,
                    evaluation=r_eval
                )
                review_items.append(rev_item)
                continue

            # Handle CONFIRMED violations from NON_COMPLIANT Stage 8 evaluations
            if status == "NON_COMPLIANT":
                # STRICT GATING: Only convert to violation if rule is APPLICABLE and Stage 8 verified
                if app_status == "APPLICABLE":
                    v_item = self._build_violation_item(product_id, r_eval, scan_id)
                    if v_item:
                        violations.append(v_item)
                    else:
                        # Fallback to review queue if evidence is insufficient
                        rev_item = ReviewQueueEngine.create_review_item(
                            product_id=product_id,
                            reason="INSUFFICIENT_EVIDENCE",
                            evaluation=r_eval,
                            description=f"Rule {r_eval.rule_number} evaluated as NON_COMPLIANT but insufficient evidence was available."
                        )
                        review_items.append(rev_item)

        # Deduplicate violations using fingerprinting
        deduped_violations = DeduplicationEngine.deduplicate_violations(violations)

        # Build Summary
        summary = Stage9ViolationSummary(
            total_evaluations=total_evals,
            confirmed_violations=len(deduped_violations),
            needs_review_items=len(review_items),
            compliant_rules=compliant_cnt,
            not_applicable_rules=not_app_cnt
        )

        overall = "NON_COMPLIANT" if deduped_violations else ("NEEDS_REVIEW" if review_items else "COMPLIANT")

        return Stage9ProductViolationResult(
            product_id=product_id,
            overall_status=overall,
            violations=deduped_violations,
            review_items=review_items,
            summary=summary
        )

    def evaluate_session_violations(
        self,
        session_id: str,
        product_evaluations: List[Stage8ProductEvaluation],
        scan_id: Optional[str] = None
    ) -> Stage9Response:
        """Evaluates violations across all product evaluations in a session."""
        prod_results: List[Stage9ProductViolationResult] = []
        tot_evals = 0
        tot_violations = 0
        tot_reviews = 0
        tot_compliant = 0
        tot_not_app = 0

        for peval in product_evaluations:
            p_res = self.evaluate_product_violations(peval, scan_id)
            prod_results.append(p_res)

            tot_evals += p_res.summary.total_evaluations
            tot_violations += p_res.summary.confirmed_violations
            tot_reviews += p_res.summary.needs_review_items
            tot_compliant += p_res.summary.compliant_rules
            tot_not_app += p_res.summary.not_applicable_rules

        overall = "NON_COMPLIANT" if any(p.overall_status == "NON_COMPLIANT" for p in prod_results) else (
            "NEEDS_REVIEW" if any(p.overall_status == "NEEDS_REVIEW" for p in prod_results) else "COMPLIANT"
        )

        summary = Stage9ViolationSummary(
            total_evaluations=tot_evals,
            confirmed_violations=tot_violations,
            needs_review_items=tot_reviews,
            compliant_rules=tot_compliant,
            not_applicable_rules=tot_not_app
        )

        return Stage9Response(
            session_id=session_id,
            violation_engine_version="2024.1",
            status="COMPLETED" if overall != "NEEDS_REVIEW" else "NEEDS_REVIEW",
            product_results=prod_results,
            overall_status=overall,
            summary=summary
        )

    def _build_violation_item(
        self,
        product_id: str,
        r_eval: Stage8RuleEvaluation,
        scan_id: Optional[str] = None
    ) -> Optional[Stage9Violation]:
        """Constructs a Stage9Violation object from a NON_COMPLIANT Stage 8 evaluation."""
        v_type = self._determine_violation_type(r_eval.rule_id, r_eval.requirement_title)
        v_id = f"viol_{uuid.uuid4().hex[:8]}"

        evidence_items: List[Stage9EvidenceItem] = []
        obs_val: Optional[str] = None

        if r_eval.evidence:
            for s8_ev in r_eval.evidence:
                evidence_items.append(Stage9EvidenceItem(
                    image_id=s8_ev.image_id,
                    product_id=product_id,
                    panel=s8_ev.panel,
                    region_id=s8_ev.region_id,
                    original_bbox=s8_ev.bbox or [],
                    observed_text=s8_ev.observed_text,
                    normalized_value=s8_ev.normalized_value,
                    semantic_field=s8_ev.semantic_field,
                    ocr_confidence=s8_ev.confidence,
                    semantic_confidence=s8_ev.confidence,
                    rule_evaluation_id=r_eval.rule_id,
                    evidence_confidence=s8_ev.confidence
                ))
                if not obs_val and s8_ev.normalized_value:
                    obs_val = s8_ev.normalized_value

        if not obs_val and r_eval.trace and r_eval.trace.observed_value:
            obs_val = r_eval.trace.observed_value

        issue_ident = obs_val or "missing_declaration"
        fingerprint = FingerprintEngine.generate_fingerprint(
            product_id=product_id,
            rule_id=r_eval.rule_id,
            violation_type=v_type,
            issue_identity=issue_ident
        )

        expected_cond = r_eval.requirement_title or "Statutory declaration requirement"
        desc = self._generate_description(r_eval, obs_val)

        return Stage9Violation(
            violation_id=v_id,
            product_id=product_id,
            scan_id=scan_id,
            rule_id=r_eval.rule_id,
            rule_number=r_eval.rule_number,
            clause=None,
            requirement=r_eval.requirement_title,
            violation_type=v_type,
            violation_status="CONFIRMED",
            severity="UNCLASSIFIED",
            description=desc,
            observed_value=obs_val,
            expected_condition=expected_cond,
            evidence=evidence_items,
            confidence=r_eval.confidence,
            rule_source=r_eval.rule_source,
            rule_version=r_eval.rule_version,
            fingerprint=fingerprint,
            created_at=datetime.now().isoformat(),
            review_status="NOT_REQUIRED"
        )

    def _determine_violation_type(self, rule_id: str, title: str) -> str:
        r_upper = rule_id.upper()
        t_lower = title.lower()

        if "NET_QUANTITY" in r_upper or "quantity" in t_lower:
            return "QUANTITY_NON_COMPLIANCE"
        if "MRP" in r_upper or "price" in t_lower:
            return "PRICE_DECLARATION_ISSUE"
        if "DATE" in r_upper or "month" in t_lower:
            return "DATE_DECLARATION_ISSUE"
        if "NAME_ADDRESS" in r_upper or "manufacturer" in t_lower or "packer" in t_lower:
            return "ENTITY_INFORMATION_ISSUE"
        if "CONSUMER_CARE" in r_upper or "consumer" in t_lower:
            return "CONSUMER_INFORMATION_ISSUE"
        if "PRODUCT_NAME" in r_upper or "generic name" in t_lower:
            return "MISSING_REQUIRED_DECLARATION"

        return "OTHER_VERIFIED_NON_COMPLIANCE"

    def _map_review_reason(self, status: str, app_status: str) -> str:
        if app_status in ("NEEDS_REVIEW", "UNKNOWN"):
            return "AMBIGUOUS_APPLICABILITY"
        if status == "CONFLICT":
            return "CONFLICTING_DECLARATIONS"
        if status == "NOT_VISIBLE":
            return "NOT_VISIBLE"
        if status == "UNKNOWN":
            return "UNKNOWN_STATUS"
        return "INSUFFICIENT_EVIDENCE"

    def _generate_description(self, r_eval: Stage8RuleEvaluation, obs_val: Optional[str]) -> str:
        """Generates a concise, objective, non-accusatory factual description."""
        rule_str = f"{r_eval.rule_number} ({r_eval.requirement_title})"
        if obs_val:
            return f"Declaration for {rule_str} was observed as '{obs_val}' and evaluated as non-compliant under statutory rule verification."
        else:
            return f"Mandatory declaration for {rule_str} was not found on available product package panels."
