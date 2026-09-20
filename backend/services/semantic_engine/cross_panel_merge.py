"""
Service 13: Cross-Panel Merge Service
=====================================
Synthesizes and fuses declarations across packaging surfaces (Front PDP, Back Panel, Coding Area):
- Preserves both NET_QUANTITY and SERVING_SIZE simultaneously (NO OVERWRITING)
- Retains distinct commercial entities (Separate Manufacturer, Packer, Importer, Marketer)
- Detects and flags intra-field conflicts (e.g. Front says Net Qty: 500g, Back says Net Qty: 450g -> CONFLICT)
- Maintains strict panel provenance attribution for legal auditability
"""

from typing import List, Dict, Any, Tuple, Optional
from ...models import (
    UniversalFieldObject,
    UniversalSemanticField,
    UniversalFieldStatus,
    StructuredProductData
)


class CrossPanelMergeService:
    """Fuses multi-surface extractions and resolves panel conflicts."""

    def __init__(self):
        pass

    def merge_panel_fields(
        self,
        panel_field_groups: List[Tuple[str, List[UniversalFieldObject]]]
    ) -> Tuple[List[UniversalFieldObject], Dict[str, Any]]:
        """Merges fields across panels with conflict preservation."""
        fused_fields: List[UniversalFieldObject] = []
        conflicts: List[Dict[str, Any]] = []

        # Index fields by selected semantic category
        fields_by_category: Dict[str, List[UniversalFieldObject]] = {}

        for surface_name, field_list in panel_field_groups:
            for field in field_list:
                cat = field.selected_field
                if cat not in fields_by_category:
                    fields_by_category[cat] = []
                fields_by_category[cat].append(field)

        # Process each category
        for cat, items in fields_by_category.items():
            if len(items) == 1:
                fused_fields.append(items[0])
                continue

            # Multi-item category: check for value consistency or coexistence
            if cat in [UniversalSemanticField.SERVING_SIZE, UniversalSemanticField.INGREDIENT_QUANTITY]:
                # Legitimate coexistence of multiple ingredients or serving sizes
                fused_fields.extend(items)
            elif cat == UniversalSemanticField.NET_QUANTITY:
                # Compare declared net quantities
                values = set(str(it.normalized_value).strip().lower() for it in items if it.normalized_value is not None)
                if len(values) > 1:
                    # Conflicting net quantities across panels!
                    for it in items:
                        it.status = "CONFLICT"
                        it.reason += " | CONFLICT: Contradictory net quantity declared on another panel."
                        fused_fields.append(it)
                    conflicts.append({
                        "field": UniversalSemanticField.NET_QUANTITY,
                        "surfaces": [it.source_panel for it in items],
                        "values": list(values),
                        "status": "CONFLICT"
                    })
                else:
                    # Consistent: select the one from Front (PDP) or highest confidence
                    pdp_item = next((it for it in items if "pdp" in it.source_panel.lower() or "front" in it.source_panel.lower()), items[0])
                    fused_fields.append(pdp_item)
            elif cat == UniversalSemanticField.MRP:
                # Compare declared MRPs
                values = set(str(it.normalized_value) for it in items if it.normalized_value is not None)
                if len(values) > 1:
                    for it in items:
                        it.status = "CONFLICT"
                        it.reason += " | CONFLICT: Contradictory retail price declared on another panel."
                        fused_fields.append(it)
                    conflicts.append({
                        "field": UniversalSemanticField.MRP,
                        "surfaces": [it.source_panel for it in items],
                        "values": list(values),
                        "status": "CONFLICT"
                    })
                else:
                    best_item = max(items, key=lambda x: x.semantic_confidence)
                    fused_fields.append(best_item)
            else:
                # Commercial entities or dates: keep all distinct entities
                fused_fields.extend(items)

        return fused_fields, {"conflicts": conflicts}
