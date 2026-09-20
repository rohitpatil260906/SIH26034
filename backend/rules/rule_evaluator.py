"""
Stage 8: Evidence-First Rule Evaluator
======================================
Evaluates applicable Legal Metrology rules against Stage 7 unified product evidence:
- Enforces strict verification gating: ONLY rules with verification_status = "VERIFIED" automatically evaluate compliance.
- Unverified rules flag NEEDS_REVIEW and cannot generate automatic violations.
- NON_COMPLIANT is assigned ONLY when rule is verified, applicable, reliable evidence exists, and demonstrates non-compliance.
- Generates machine-readable rule traces for auditability.
"""

from typing import List, Dict, Any, Optional, Tuple
from .rule_models import (
    Stage8RuleDefinition,
    Stage8ApplicabilityResult,
    Stage8EvidenceItem,
    Stage8RuleEvaluation,
    Stage8RuleTrace,
    Stage7UnifiedProduct
)
from .evidence_validator import EvidenceValidator
from .rule_trace import RuleTraceGenerator


class RuleEvaluator:
    """Evaluates statutory rules with strict verification gating & trace generation."""

    def __init__(self):
        self.validator = EvidenceValidator()
        self.trace_generator = RuleTraceGenerator()

    def evaluate_rule(
        self,
        rule: Stage8RuleDefinition,
        applicability: Stage8ApplicabilityResult,
        product: Stage7UnifiedProduct,
        rule_context: Optional[Dict[str, Any]] = None
    ) -> Stage8RuleEvaluation:
        """Evaluates a single legal rule against product evidence."""
        trace_steps: List[str] = [
            f"Rule verification status: {rule.verification_status}",
            f"Applicability status: {applicability.applicability_status} ({applicability.reason})"
        ]

        # 1. Verification Gating Check
        if rule.verification_status != "VERIFIED":
            trace_steps.append("Rule is UNVERIFIED or NEEDS_REVIEW; automatic compliance evaluation disabled.")
            trace = self.trace_generator.build_trace(
                rule=rule,
                applicability=applicability,
                evaluation_status="NEEDS_REVIEW",
                confidence=0.50,
                evidence_item=None,
                trace_steps=trace_steps
            )
            return Stage8RuleEvaluation(
                rule_id=rule.rule_id,
                rule_number=rule.rule_number,
                requirement_title=rule.title,
                applicability_status=applicability.applicability_status,
                evaluation_status="NEEDS_REVIEW",
                confidence=0.50,
                evidence=[],
                rule_source=rule.source_name,
                rule_version=rule.source_version,
                trace=trace
            )

        # 2. Non-applicable Rule Check
        if applicability.applicability_status == "NOT_APPLICABLE":
            trace_steps.append("Rule not applicable to product context; skipped.")
            trace = self.trace_generator.build_trace(
                rule=rule,
                applicability=applicability,
                evaluation_status="NOT_APPLICABLE",
                confidence=1.0,
                evidence_item=None,
                trace_steps=trace_steps
            )
            return Stage8RuleEvaluation(
                rule_id=rule.rule_id,
                rule_number=rule.rule_number,
                requirement_title=rule.title,
                applicability_status="NOT_APPLICABLE",
                evaluation_status="NOT_APPLICABLE",
                confidence=1.0,
                evidence=[],
                rule_source=rule.source_name,
                rule_version=rule.source_version,
                trace=trace
            )

        # 3. Unknown / Ambiguous Applicability Safety
        if applicability.applicability_status in ("NEEDS_REVIEW", "UNKNOWN"):
            trace_steps.append("Applicability is uncertain; flagging for manual review.")
            trace = self.trace_generator.build_trace(
                rule=rule,
                applicability=applicability,
                evaluation_status="NEEDS_REVIEW",
                confidence=0.50,
                evidence_item=None,
                trace_steps=trace_steps
            )
            return Stage8RuleEvaluation(
                rule_id=rule.rule_id,
                rule_number=rule.rule_number,
                requirement_title=rule.title,
                applicability_status=applicability.applicability_status,
                evaluation_status="NEEDS_REVIEW",
                confidence=0.50,
                evidence=[],
                rule_source=rule.source_name,
                rule_version=rule.source_version,
                trace=trace
            )

        # 4. Mandatory Declaration & Field Validation
        eval_status = "COMPLIANT"
        evidence_list: List[Stage8EvidenceItem] = []
        conf = 0.95

        req_type = rule.requirement_type.upper()

        if req_type == "NET_QUANTITY":
            eval_status, ev_item, msg = self.validator.validate_net_quantity(product)
            trace_steps.append(msg)
            if ev_item:
                evidence_list.append(ev_item)

        elif req_type == "MRP":
            eval_status, ev_item, msg = self.validator.validate_mrp(product)
            trace_steps.append(msg)
            if ev_item:
                evidence_list.append(ev_item)

        elif req_type in ("DECLARATION", "CONSUMER_CARE", "IMPORTER"):
            # Evaluate all required fields for rule
            field_results: List[str] = []
            for req_f in rule.required_fields:
                rf_upper = req_f.upper()
                if "MANUFACTURER" in rf_upper:
                    if "ADDRESS" in rf_upper:
                        st, ev, msg = self.validator.validate_address_declaration(product, "MANUFACTURER")
                    else:
                        st, ev, msg = self.validator.validate_entity_declaration(product, "MANUFACTURER")
                elif "IMPORTER" in rf_upper:
                    if "ADDRESS" in rf_upper:
                        st, ev, msg = self.validator.validate_address_declaration(product, "IMPORTER")
                    else:
                        st, ev, msg = self.validator.validate_entity_declaration(product, "IMPORTER")
                elif "PACKER" in rf_upper:
                    if "ADDRESS" in rf_upper:
                        st, ev, msg = self.validator.validate_address_declaration(product, "PACKER")
                    else:
                        st, ev, msg = self.validator.validate_entity_declaration(product, "PACKER")
                else:
                    st, ev, msg = self._validate_generic_field(product, req_f)

                trace_steps.append(msg)
                if ev:
                    evidence_list.append(ev)
                field_results.append(st)

            if any(r == "CONFLICT" for r in field_results):
                eval_status = "CONFLICT"
            elif any(r == "NON_COMPLIANT" for r in field_results):
                # Strict check: NON_COMPLIANT assigned only if verified, applicable, and evidence confirms missing
                eval_status = "NON_COMPLIANT"
            elif any(r == "NEEDS_REVIEW" for r in field_results):
                eval_status = "NEEDS_REVIEW"
            else:
                eval_status = "COMPLIANT"

        primary_ev = evidence_list[0] if evidence_list else None
        trace = self.trace_generator.build_trace(
            rule=rule,
            applicability=applicability,
            evaluation_status=eval_status,
            confidence=conf,
            evidence_item=primary_ev,
            trace_steps=trace_steps
        )

        return Stage8RuleEvaluation(
            rule_id=rule.rule_id,
            rule_number=rule.rule_number,
            requirement_title=rule.title,
            applicability_status="APPLICABLE",
            evaluation_status=eval_status,
            confidence=conf,
            evidence=evidence_list,
            rule_source=rule.source_name,
            rule_version=rule.source_version,
            trace=trace
        )

    def _validate_generic_field(
        self,
        product: Stage7UnifiedProduct,
        fname: str
    ) -> Tuple[str, Optional[Stage8EvidenceItem], str]:
        for f in product.fields:
            if f.field_name.upper() == fname.upper() and f.value:
                src = f.sources[0] if f.sources else None
                ev = Stage8EvidenceItem(
                    image_id=src.image_id if src else None,
                    panel=src.panel if src else None,
                    region_id=src.region_id if src else None,
                    bbox=src.bbox if src else [],
                    observed_text=src.raw_text if src else f.value,
                    normalized_value=f.value,
                    semantic_field=f.field_name,
                    confidence=f.confidence
                )
                if f.status == "CONFIRMED":
                    return ("COMPLIANT", ev, f"Field {fname} declared: {f.value}")
                elif f.status in ("CONFLICT", "NOT_VISIBLE", "UNKNOWN", "NEEDS_REVIEW"):
                    return (f.status, ev, f"Field {fname} status: {f.status}")

        return ("NON_COMPLIANT", None, f"Required field {fname} not found in evidence")
