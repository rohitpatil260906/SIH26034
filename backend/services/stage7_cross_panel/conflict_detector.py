"""
Stage 7: Cross-Panel Conflict Detector
======================================
Detects conflicting field values across multiple panels:
- Identifies when the same semantic field contains contradictory values (e.g. MRP ₹299 vs ₹349).
- Never discards evidence or uses arbitrary priority ("front panel wins").
- Flags status = "CONFLICT" and preserves all competing candidate values with source image and panel metadata.
"""

from typing import List, Dict, Any, Optional, Set
from ...models import (
    Stage7ConflictCandidate,
    Stage7FieldConflict,
    Stage7FieldSource
)


class ConflictDetector:
    """Detects and encapsulates multi-panel field value conflicts."""

    def evaluate_field_values(
        self,
        field_name: str,
        sources: List[Stage7FieldSource]
    ) -> Tuple[str, Optional[str], List[Stage7ConflictCandidate]]:
        """
        Analyzes field values across sources.
        Returns:
            (status, resolved_value_if_confirmed, conflict_candidates)
        """
        if not sources:
            return ("NOT_VISIBLE", None, [])

        # Group sources by normalized value
        val_groups: Dict[str, List[Stage7FieldSource]] = {}
        for src in sources:
            val = (src.raw_text or "").strip()
            if not val or val.upper() in ("NOT_VISIBLE", "UNKNOWN", "NONE"):
                continue
            norm_val = val.lower()
            if norm_val not in val_groups:
                val_groups[norm_val] = []
            val_groups[norm_val].append(src)

        if not val_groups:
            return ("NOT_VISIBLE", None, [])

        # Single unique value across all panels -> CONFIRMED
        if len(val_groups) == 1:
            best_src = max(sources, key=lambda s: s.confidence)
            return ("CONFIRMED", best_src.raw_text, [])

        # Multiple distinct values -> CONFLICT
        candidates: List[Stage7ConflictCandidate] = []
        for norm_val, src_list in val_groups.items():
            best_s = max(src_list, key=lambda s: s.confidence)
            candidates.append(Stage7ConflictCandidate(
                value=best_s.raw_text or norm_val,
                image_id=best_s.image_id,
                panel=best_s.panel,
                confidence=best_s.confidence,
                raw_text=best_s.raw_text
            ))

        return ("CONFLICT", None, candidates)
