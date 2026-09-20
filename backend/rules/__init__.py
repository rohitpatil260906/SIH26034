"""
Stage 8: Verified Legal Metrology Rule Engine
=============================================
Master Pipeline Entry Point for Stage 8:
- Consumes Stage 7 unified multi-panel product objects.
- Loads verified statutory Legal Metrology rules from RuleRegistry.
- Evaluates rule applicability via ApplicabilityEngine.
- Validates semantic declarations (Net Qty, MRP, Entity names/addresses, Dates) via EvidenceValidator.
- Enforces strict verification gating (ONLY VERIFIED rules evaluate compliance; unverified flag NEEDS_REVIEW).
- Generates auditable machine-readable Stage8RuleTrace objects.
- Keeps multiple products strictly isolated.

Legal Separation Policy:
- Does NOT generate Stage 9 violation reports or legal compounding fee calculations.
- Does NOT perform complete end-to-end testing.
"""

import logging
from typing import List, Dict, Any, Optional
from .rule_models import (
    Stage8RuleDefinition,
    Stage8ApplicabilityResult,
    Stage8EvidenceItem,
    Stage8RuleTrace,
    Stage8RuleEvaluation,
    Stage8ProductEvaluation,
    Stage8Request,
    Stage8Response
)
from .rule_registry import RuleRegistry
from .rule_loader import load_statutory_rules
from .applicability_engine import ApplicabilityEngine
from .rule_evaluator import RuleEvaluator
from ..models import Stage7UnifiedProduct, Stage7Response

logger = logging.getLogger(__name__)


class Stage8RuleEngine:
    """Master Legal Metrology Rule Engine for Stage 8."""

    def __init__(self, json_path: Optional[str] = None):
        self.registry = RuleRegistry()
        load_statutory_rules(self.registry, json_path)
        self.applicability_engine = ApplicabilityEngine()
        self.rule_evaluator = RuleEvaluator()

    def evaluate_product(
        self,
        product: Stage7UnifiedProduct,
        rule_context: Optional[Dict[str, Any]] = None
    ) -> Stage8ProductEvaluation:
        """Evaluates all applicable statutory rules for a single unified product."""
        rule_context = rule_context or {}
        prod_cat = product.category_profile.category or "UNKNOWN"
        target_date = rule_context.get("target_date")

        # 1. Fetch applicable rules from registry
        rules = self.registry.get_applicable_rules(category=prod_cat, target_date=target_date)

        evaluations: List[Stage8RuleEvaluation] = []
        needs_review: List[Stage8RuleEvaluation] = []
        traces: List[Stage8RuleTrace] = []

        # 2. Evaluate each rule independently
        for rule in rules:
            # Applicability Check
            applicability = self.applicability_engine.evaluate_applicability(rule, product, rule_context)

            # Rule Evaluation
            eval_res = self.rule_evaluator.evaluate_rule(rule, applicability, product, rule_context)
            evaluations.append(eval_res)

            if eval_res.trace:
                traces.append(eval_res.trace)

            if eval_res.evaluation_status in ("NEEDS_REVIEW", "CONFLICT", "UNKNOWN"):
                needs_review.append(eval_res)

        # 3. Overall Product Compliance Status
        if any(e.evaluation_status == "NON_COMPLIANT" for e in evaluations):
            overall = "NON_COMPLIANT"
        elif any(e.evaluation_status in ("NEEDS_REVIEW", "CONFLICT") for e in evaluations):
            overall = "NEEDS_REVIEW"
        else:
            overall = "COMPLIANT"

        return Stage8ProductEvaluation(
            product_id=product.product_id,
            overall_status=overall,
            evaluations=evaluations,
            needs_review_items=needs_review,
            conflicts=product.conflicts,
            rule_traces=traces
        )

    def evaluate_session(
        self,
        session_id: str = "session_001",
        stage7_response: Optional[Stage7Response] = None,
        products: Optional[List[Stage7UnifiedProduct]] = None,
        rule_context: Optional[Dict[str, Any]] = None
    ) -> Stage8Response:
        """
        Evaluates Legal Metrology compliance for all products in a session.
        Ensures multiple products are evaluated with zero cross-contamination.
        """
        target_products = products or (stage7_response.products if stage7_response else [])
        if not target_products:
            return Stage8Response(
                session_id=session_id,
                status="COMPLETED",
                product_evaluations=[],
                overall_status="COMPLIANT",
                message="No products available for evaluation"
            )

        product_evals: List[Stage8ProductEvaluation] = []
        all_needs_review: List[Stage8RuleEvaluation] = []
        all_conflicts = []

        for prod in target_products:
            peval = self.evaluate_product(prod, rule_context)
            product_evals.append(peval)
            all_needs_review.extend(peval.needs_review_items)
            all_conflicts.extend(peval.conflicts)

        if any(pe.overall_status == "NON_COMPLIANT" for pe in product_evals):
            overall_status = "NON_COMPLIANT"
        elif any(pe.overall_status == "NEEDS_REVIEW" for pe in product_evals):
            overall_status = "NEEDS_REVIEW"
        else:
            overall_status = "COMPLIANT"

        return Stage8Response(
            session_id=session_id,
            rule_engine_version="2024.1",
            status="COMPLETED" if overall_status != "NEEDS_REVIEW" else "NEEDS_REVIEW",
            product_evaluations=product_evals,
            overall_status=overall_status,
            needs_review_items=all_needs_review,
            conflicts=all_conflicts
        )
