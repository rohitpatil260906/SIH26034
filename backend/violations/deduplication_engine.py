"""
Stage 9: Violation Deduplication Engine
=======================================
Deduplicates confirmed violations across multi-panel products:
- If multiple evidence regions across panels support the same confirmed violation,
  consolidates them into ONE violation record containing multiple evidence items.
- Uses FingerprintEngine to deterministically group identical violations.
- Keeps distinct violation types and distinct rule evaluations as separate records.
"""

from typing import List, Dict, Any
from .violation_models import Stage9Violation, Stage9EvidenceItem
from .fingerprint_engine import FingerprintEngine


class DeduplicationEngine:
    """Consolidates duplicate violations across multiple panels."""

    @staticmethod
    def deduplicate_violations(violations: List[Stage9Violation]) -> List[Stage9Violation]:
        """
        Deduplicates violations by fingerprint.
        Merges evidence items when the same violation appears on multiple panels.
        """
        dedup_map: Dict[str, Stage9Violation] = {}

        for v in violations:
            fp = v.fingerprint
            if fp not in dedup_map:
                dedup_map[fp] = v
            else:
                existing = dedup_map[fp]
                # Merge evidence items cleanly without duplicate evidence references
                existing_ev_keys = {
                    (ev.image_id, ev.panel, ev.region_id, tuple(ev.original_bbox))
                    for ev in existing.evidence
                }
                for new_ev in v.evidence:
                    key = (new_ev.image_id, new_ev.panel, new_ev.region_id, tuple(new_ev.original_bbox))
                    if key not in existing_ev_keys:
                        existing.evidence.append(new_ev)
                        existing_ev_keys.add(key)

                # Keep highest confidence
                if v.confidence > existing.confidence:
                    existing.confidence = v.confidence

        return list(dedup_map.values())
