"""
Stage 8: Machine-Readable Rule Trace Generator
==============================================
Generates auditable, machine-readable traces for every evaluated legal rule:
- Maps Rule -> Requirement -> Observed Field -> Source Image / Panel -> Bounding Box -> Decision.
- Does NOT expose LLM chain-of-thought; stores concise, auditable decision steps.
"""

from typing import List, Dict, Any, Optional
from .rule_models import (
    Stage8RuleDefinition,
    Stage8ApplicabilityResult,
    Stage8EvidenceItem,
    Stage8RuleTrace
)


class RuleTraceGenerator:
    """Generates machine-readable rule evaluation traces."""

    def build_trace(
        self,
        rule: Stage8RuleDefinition,
        applicability: Stage8ApplicabilityResult,
        evaluation_status: str,
        confidence: float,
        evidence_item: Optional[Stage8EvidenceItem],
        trace_steps: List[str]
    ) -> Stage8RuleTrace:
        """Constructs an auditable Stage8RuleTrace."""
        return Stage8RuleTrace(
            rule_id=rule.rule_id,
            applicable=(applicability.applicability_status == "APPLICABLE"),
            observed_field=evidence_item.semantic_field if evidence_item else (rule.required_fields[0] if rule.required_fields else None),
            observed_value=evidence_item.normalized_value or evidence_item.observed_text if evidence_item else None,
            evidence=evidence_item,
            evaluation=evaluation_status,
            confidence=confidence,
            rule_source=rule.source_name,
            rule_version=rule.source_version,
            trace_steps=trace_steps
        )
