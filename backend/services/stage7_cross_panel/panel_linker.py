"""
Stage 7: Cross-Panel Entity & Address Linker
============================================
Links entities, addresses, and statutory declarations across panels:
- Maps panel roles (FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM, SIDE, PARTIAL, UNKNOWN).
- Links entity names on one panel (e.g. Manufacturer on BACK) with addresses on another panel (e.g. Address on SIDE).
- Merges multi-panel address lines when supported by evidence.
- Calculates panel completeness (available_panels vs missing_panels).
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from ...models import (
    Stage4ProductIdentity,
    Stage4Entity,
    Stage7CrossPanelLink,
    Stage7PanelCompleteness,
    Stage7SourceImage
)

ALL_POSSIBLE_PANELS = ["FRONT", "BACK", "LEFT", "RIGHT", "TOP", "BOTTOM", "SIDE"]


class PanelLinker:
    """Cross-panel entity linker and panel completeness evaluator."""

    def calculate_panel_completeness(
        self,
        source_images: List[Stage7SourceImage]
    ) -> Stage7PanelCompleteness:
        """Determines available vs missing panel coverage."""
        available: Set[str] = set()
        for img in source_images:
            p = (img.panel or "UNKNOWN").upper()
            if p != "UNKNOWN" and p != "PARTIAL":
                available.add(p)

        missing = [p for p in ALL_POSSIBLE_PANELS if p not in available]
        return Stage7PanelCompleteness(
            available_panels=sorted(list(available)),
            missing_panels=missing
        )

    def link_cross_panel_entities(
        self,
        identities_by_image: Dict[str, Tuple[Stage7SourceImage, Stage4ProductIdentity]]
    ) -> List[Stage7CrossPanelLink]:
        """Links entity names, roles, and addresses across panels."""
        links: List[Stage7CrossPanelLink] = []
        link_counter = 1

        images = list(identities_by_image.items())
        for i in range(len(images)):
            img_id_a, (src_img_a, id_a) = images[i]
            for j in range(i + 1, len(images)):
                img_id_b, (src_img_b, id_b) = images[j]

                # Match entities by role or company name
                for ent_a in id_a.entities:
                    if not ent_a.name or ent_a.name == "NOT_VISIBLE":
                        continue
                    for ent_b in id_b.entities:
                        if not ent_b.name or ent_b.name == "NOT_VISIBLE":
                            continue

                        # Same role or matching entity name
                        same_role = ent_a.role.upper() == ent_b.role.upper()
                        same_name = ent_a.name.strip().lower() == ent_b.name.strip().lower()

                        if same_role or same_name:
                            # 1. Address split or complementary address linking
                            linked_val = ""
                            if ent_a.address and ent_b.address:
                                if ent_a.address == ent_b.address:
                                    linked_val = f"{ent_a.name} — {ent_a.address}"
                                else:
                                    # Complementary address parts (e.g. Street on one, City on another)
                                    linked_val = f"{ent_a.name} — {ent_a.address}, {ent_b.address}"
                            elif ent_a.address:
                                linked_val = f"{ent_a.name} — {ent_a.address}"
                            elif ent_b.address:
                                linked_val = f"{ent_b.name} — {ent_b.address}"
                            else:
                                linked_val = ent_a.name

                            links.append(Stage7CrossPanelLink(
                                link_id=f"link_{link_counter:03d}",
                                entity_type=f"{ent_a.role.upper()}_LINK",
                                source_image_id=img_id_a,
                                target_image_id=img_id_b,
                                source_panel=src_img_a.panel,
                                target_panel=src_img_b.panel,
                                confidence=round(min(ent_a.confidence, ent_b.confidence), 2),
                                linked_value=linked_val
                            ))
                            link_counter += 1

        return links
