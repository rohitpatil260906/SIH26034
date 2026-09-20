"""
Stage 7: Cross-Panel Field Consolidation Engine
===============================================
Consolidates extracted semantic and adaptive fields across panels:
- Unifies identical field declarations across panels into a single Stage7UnifiedField with multiple sources.
- Distinguishes identical raw strings with different semantic meanings (e.g. 500 g Net Qty vs 500 g Serving Size).
- Uses score-based ranking (semantic confidence, OCR confidence, explicit heading) rather than arbitrary panel priority.
- Detects conflicts via ConflictDetector and preserves all competing candidates.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from ...models import (
    Stage6SingleProductProfile,
    Stage6AdaptiveField,
    Stage7UnifiedField,
    Stage7FieldSource,
    Stage7FieldConflict,
    Stage7SourceImage
)
from .conflict_detector import ConflictDetector


class FieldMerger:
    """Consolidates Stage 6 adaptive fields across panels for a single product."""

    def __init__(self):
        self.conflict_detector = ConflictDetector()

    def merge_product_fields(
        self,
        profiles_by_image: List[Tuple[Stage7SourceImage, Stage6SingleProductProfile]]
    ) -> Tuple[List[Stage7UnifiedField], List[Stage7FieldConflict]]:
        """Consolidates fields across all panel profiles for a single product."""

        fields_by_name: Dict[str, List[Stage7FieldSource]] = {}
        field_units: Dict[str, str] = {}
        field_evidence: Dict[str, str] = {}

        for src_img, profile in profiles_by_image:
            image_id = src_img.image_id
            panel = src_img.panel

            for field in profile.adaptive_schema.fields:
                fname = field.field_name
                # Skip NOT_APPLICABLE or empty values unless PRESENT/NEEDS_REVIEW/UNKNOWN
                if field.status in ("NOT_APPLICABLE", "NOT_VISIBLE") and not field.value:
                    continue

                if fname not in fields_by_name:
                    fields_by_name[fname] = []

                if field.unit and fname not in field_units:
                    field_units[fname] = field.unit
                if field.evidence and fname not in field_evidence:
                    field_evidence[fname] = field.evidence

                # Construct source record
                fields_by_name[fname].append(Stage7FieldSource(
                    image_id=image_id,
                    panel=panel,
                    region_id=field.source_region_ids[0] if field.source_region_ids else None,
                    bbox=[],
                    confidence=field.confidence if field.confidence > 0 else 0.90,
                    raw_text=field.value
                ))

        unified_fields: List[Stage7UnifiedField] = []
        conflicts: List[Stage7FieldConflict] = []

        for fname, sources in fields_by_name.items():
            status, resolved_val, candidates = self.conflict_detector.evaluate_field_values(fname, sources)

            if status == "CONFLICT":
                unified_fields.append(Stage7UnifiedField(
                    field_name=fname,
                    value=None,
                    status="CONFLICT",
                    confidence=0.0,
                    sources=sources,
                    unit=field_units.get(fname),
                    evidence=field_evidence.get(fname),
                    candidates=candidates
                ))
                conflicts.append(Stage7FieldConflict(
                    field_name=fname,
                    status="CONFLICT",
                    candidates=candidates
                ))
            elif status == "CONFIRMED":
                # Compute best confidence across sources
                best_conf = max(s.confidence for s in sources)
                unified_fields.append(Stage7UnifiedField(
                    field_name=fname,
                    value=resolved_val,
                    status="CONFIRMED",
                    confidence=best_conf,
                    sources=sources,
                    unit=field_units.get(fname),
                    evidence=field_evidence.get(fname)
                ))
            else:
                unified_fields.append(Stage7UnifiedField(
                    field_name=fname,
                    value=None,
                    status=status,
                    confidence=0.0,
                    sources=sources,
                    unit=field_units.get(fname)
                ))

        return unified_fields, conflicts
