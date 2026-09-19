"""
Service 18: Audit / Explainability Service
==========================================
Generates officer-ready statutory explainability dossiers:
For every extracted value, displays:
- VALUE (raw and normalized)
- SEMANTIC MEANING (statutory field classification)
- SOURCE REGION (Front/PDP, Back, Side, Coding Area)
- CONFIDENCE (percentage score)
- REASON (contextual evidence reasoning)
"""

from typing import List, Dict, Any, Optional

from ...models import UniversalFieldObject, LmCompassResult, StructuredProductData


class AuditExplanationDossier:
    """Officer-grade explainability record."""
    def __init__(
        self,
        value: str,
        semantic_meaning: str,
        source_region: str,
        confidence: str,
        reason: str,
        status: str,
        candidates: List[str]
    ):
        self.value = value
        self.semantic_meaning = semantic_meaning
        self.source_region = source_region
        self.confidence = confidence
        self.reason = reason
        self.status = status
        self.candidates = candidates

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "semantic_meaning": self.semantic_meaning,
            "source_region": self.source_region,
            "confidence": self.confidence,
            "reason": self.reason,
            "status": self.status,
            "candidates": self.candidates
        }


class AuditExplainabilityService:
    """Generates statutory explainability reports for enforcement dossiers."""

    def __init__(self):
        pass

    def generate_field_dossiers(
        self,
        fields: List[UniversalFieldObject]
    ) -> List[AuditExplanationDossier]:
        """Creates the required 5-part statutory explanation for every detected value."""
        dossiers: List[AuditExplanationDossier] = []

        for f in fields:
            conf_pct = f"{int(f.overall_confidence * 100)}%"
            val_str = f"{f.raw_text}"
            if f.normalized_value is not None and str(f.normalized_value) != f.raw_text:
                val_str += f" (Normalized: {f.normalized_value} {f.unit or ''})".strip()

            dossiers.append(AuditExplanationDossier(
                value=val_str,
                semantic_meaning=f.selected_field.replace("_", " "),
                source_region=f.source_panel,
                confidence=conf_pct,
                reason=f.reason,
                status=f.status,
                candidates=f.candidate_fields
            ))

        return dossiers

    def format_text_report(self, dossiers: List[AuditExplanationDossier]) -> str:
        """Formats dossiers into statutory text report."""
        lines = [
            "=" * 70,
            "LM-COMPASS STATUTORY FIELD EXPLAINABILITY DOSSIER",
            "=" * 70
        ]
        for d in dossiers:
            lines.append(f"\nValue:            {d.value}")
            lines.append(f"Semantic Meaning: {d.semantic_meaning}")
            lines.append(f"Source Region:    {d.source_region}")
            lines.append(f"Confidence:       {d.confidence}")
            lines.append(f"Reason:           {d.reason}")
            lines.append(f"Status:           {d.status}")
            lines.append("-" * 70)

        return "\n".join(lines)
