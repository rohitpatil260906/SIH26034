"""
Stage 3: Section Detection & Semantic Shielding Service
======================================================
Identifies semantic sections on packaging surfaces:
- INGREDIENTS
- NUTRITION
- MANUFACTURER_INFORMATION / PACKER_INFORMATION / MARKETER_INFORMATION / IMPORTER_INFORMATION
- DIRECTIONS / INSTRUCTIONS
- WARNINGS / PRECAUTIONS
- STORAGE
- CONSUMER_CARE
- PRICE_INFORMATION / QUANTITY_INFORMATION / DATE_INFORMATION / BATCH_INFORMATION
- TECHNICAL_SPECIFICATIONS

CRITICAL SHIELDING RULE:
Any text region within an INGREDIENTS block MUST NEVER be classified as:
- ADDRESS
- MANUFACTURER_NAME / PACKER_NAME
- POSTAL_PIN
- NET_QUANTITY
"""

import re
import uuid
from typing import List, Dict, Any, Tuple, Optional
from ...models import Stage2TextRegion, Stage3Section


class SectionDetectionService:
    """Detects packaging sections and shields specific domains from cross-contamination."""

    # Section header patterns
    SECTION_HEADER_PATTERNS = [
        (r'\b(?:ingredients?|composition|active\s+ingredients?|contains)\b[:\s]?', "INGREDIENTS"),
        (r'\b(?:nutritional?\s+(?:information|facts|values?)|per\s+100\s*g|approximate\s+composition)\b', "NUTRITION"),
        (r'\b(?:manufactured\s+(?:by|at)|mfd\s+by|produced\s+by)\b', "MANUFACTURER_INFORMATION"),
        (r'\b(?:marketed\s+by|mkt\s+by|distributed\s+by)\b', "MARKETER_INFORMATION"),
        (r'\b(?:packed\s+by|pkd\s+by)\b', "PACKER_INFORMATION"),
        (r'\b(?:imported\s+by|imp\s+by)\b', "IMPORTER_INFORMATION"),
        (r'\b(?:directions?\s+(?:for\s+use)?|how\s+to\s+use|usage|instructions?|application)\b', "DIRECTIONS"),
        (r'\b(?:warnings?|caution|precautions?|contraindications?)\b', "WARNINGS"),
        (r'\b(?:storage\s+instructions?|store\s+in\s+a?\s*cool|keep\s+in\s+a?\s*dry)\b', "STORAGE"),
        (r'\b(?:consumer\s+care|customer\s+(?:care|service|support)|helpline|toll\s*free|queries\s+or\s+feedback)\b', "CONSUMER_CARE"),
        (r'\b(?:mrp|price|maximum\s+retail\s+price)\b', "PRICE_INFORMATION"),
        (r'\b(?:net\s+(?:quantity|qty|wt|volume|weight|mass))\b', "QUANTITY_INFORMATION"),
        (r'\b(?:mfg\s+date|expiry\s+date|best\s+before|use\s+by)\b', "DATE_INFORMATION"),
        (r'\b(?:batch\s+no|lot\s+no|b\.?\s*no)\b', "BATCH_INFORMATION"),
        (r'\b(?:specifications?|technical\s+data|rating|dimensions?)\b', "TECHNICAL_SPECIFICATIONS"),
    ]

    def detect_sections(
        self,
        regions: List[Stage2TextRegion]
    ) -> Tuple[List[Stage3Section], Dict[str, str]]:
        """Detects sections and returns a tuple of:
        (List[Stage3Section], Dict[region_id, section_type])
        """
        if not regions:
            return [], {}

        # Sort by reading order / visual hierarchy
        sorted_regions = sorted(regions, key=lambda r: (r.bbox[1] if r.bbox else 0, r.bbox[0] if r.bbox else 0))
        region_to_section: Dict[str, str] = {}
        sections: List[Stage3Section] = []

        current_section_type: Optional[str] = None
        current_section_id: Optional[str] = None
        current_heading_text: Optional[str] = None
        current_region_ids: List[str] = []
        current_bbox: Optional[List[float]] = None

        for region in sorted_regions:
            text = region.normalized_text or region.raw_text or ""
            text_lower = text.lower()

            # Check if this region begins a new section
            detected_header_type = None
            for pattern, sec_type in self.SECTION_HEADER_PATTERNS:
                if re.search(pattern, text_lower, re.I):
                    detected_header_type = sec_type
                    break

            if detected_header_type:
                # Close existing section if any
                if current_section_type and current_region_ids:
                    sections.append(
                        Stage3Section(
                            section_id=current_section_id or f"SEC-{uuid.uuid4().hex[:6].upper()}",
                            section_type=current_section_type,
                            heading_text=current_heading_text,
                            region_ids=current_region_ids,
                            bbox=current_bbox or [],
                            confidence=0.95
                        )
                    )

                # Start new section
                current_section_type = detected_header_type
                current_section_id = f"SEC-{uuid.uuid4().hex[:6].upper()}"
                current_heading_text = text
                current_region_ids = [region.region_id]
                current_bbox = list(region.bbox)
                region_to_section[region.region_id] = current_section_type

            elif current_section_type:
                # Check spatial continuity with current section
                # If within vertical distance (e.g. 150px) or part of multi-line block
                if current_bbox and region.bbox:
                    prev_bottom = current_bbox[1] + current_bbox[3]
                    curr_top = region.bbox[1]
                    vertical_gap = curr_top - prev_bottom

                    # Break section if huge vertical gap (> 200px)
                    if vertical_gap > 200:
                        sections.append(
                            Stage3Section(
                                section_id=current_section_id,
                                section_type=current_section_type,
                                heading_text=current_heading_text,
                                region_ids=current_region_ids,
                                bbox=current_bbox,
                                confidence=0.90
                            )
                        )
                        current_section_type = None
                        current_region_ids = []
                        current_bbox = None
                        region_to_section[region.region_id] = "OTHER"
                        continue

                current_region_ids.append(region.region_id)
                region_to_section[region.region_id] = current_section_type
                if current_bbox and region.bbox:
                    x1 = min(current_bbox[0], region.bbox[0])
                    y1 = min(current_bbox[1], region.bbox[1])
                    x2 = max(current_bbox[0] + current_bbox[2], region.bbox[0] + region.bbox[2])
                    y2 = max(current_bbox[1] + current_bbox[3], region.bbox[1] + region.bbox[3])
                    current_bbox = [x1, y1, x2 - x1, y2 - y1]
            else:
                region_to_section[region.region_id] = "OTHER"

        # Final section flush
        if current_section_type and current_region_ids:
            sections.append(
                Stage3Section(
                    section_id=current_section_id or f"SEC-{uuid.uuid4().hex[:6].upper()}",
                    section_type=current_section_type,
                    heading_text=current_heading_text,
                    region_ids=current_region_ids,
                    bbox=current_bbox or [],
                    confidence=0.95
                )
            )

        return sections, region_to_section
