"""
Stage 3: Heading Detection & Heading-to-Value Association Service
================================================================
Identifies explicit statutory headings on packaging and establishes
explicit spatial & contextual relationships with value tokens:
- "Net Quantity" / "Net Qty" -> "50 g"
- "Serving Size" -> "50 g"
- "MRP" / "Maximum Retail Price" -> "Rs. 299"
- "Batch No." -> "ABC123"
- "Mfg Date" -> "08/2026"
- "Best Before" -> "24 Months"
- "Manufactured By" -> "XYZ Foods Pvt Ltd"
- "Marketed By" -> "ABC Pvt Ltd"
- "Consumer Care" -> phone/email
"""

import re
import uuid
from typing import List, Dict, Any, Tuple, Optional
from ...models import Stage2TextRegion, Stage3Relationship


class HeadingAssociationService:
    """Discovers explicit headings and associates them to value tokens."""

    HEADING_PATTERNS = [
        # Quantity
        (r'^(?:net\s+(?:quantity|qty|wt|volume|weight|mass))\b[.:;=\-]?\s*', "NET_QUANTITY"),
        (r'^(?:serving\s+size)\b[.:;=\-]?\s*', "SERVING_SIZE"),
        (r'^(?:unit\s+sale\s+price|u\.?s\.?p\.?)\b[.:;=\-]?\s*', "SALE_PRICE"),

        # Price
        (r'^(?:m\.?r\.?p\.?|maximum\s+retail\s+price|mrp\s*\(incl\.?\s*of\s*all\s*taxes\))\b[.:;=\-]?\s*', "MRP"),
        (r'^(?:price|sale\s+price|retail\s+price)\b[.:;=\-]?\s*', "PRICE"),

        # Entities
        (r'^(?:manufactured\s+(?:by|at)|mfd\s+by|produced\s+by)\b[.:;=\-]?\s*', "MANUFACTURER_NAME"),
        (r'^(?:marketed\s+by|mkt\s+by)\b[.:;=\-]?\s*', "MARKETER_NAME"),
        (r'^(?:packed\s+by|pkd\s+by)\b[.:;=\-]?\s*', "PACKER_NAME"),
        (r'^(?:imported\s+by|imp\s+by)\b[.:;=\-]?\s*', "IMPORTER_NAME"),
        (r'^(?:distributed\s+by)\b[.:;=\-]?\s*', "DISTRIBUTOR_NAME"),

        # Dates & Shelf-Life
        (r'^(?:mfg\s*(?:date|on|\.)?|mfd\s*(?:date|on|\.)?|date\s+of\s+mfg)\b[.:;=\-]?\s*', "MANUFACTURING_DATE"),
        (r'^(?:pkd\s*(?:date|on|\.)?|packed\s*(?:date|on|\.)?|date\s+of\s+pkd)\b[.:;=\-]?\s*', "PACKING_DATE"),
        (r'^(?:exp\s*(?:date|\.)?|expiry\s*(?:date)?|use\s+by|use\s+before)\b[.:;=\-]?\s*', "EXPIRY_DATE"),
        (r'^(?:best\s+before|shelf\s+life)\b[.:;=\-]?\s*', "BEST_BEFORE_DATE"),

        # Identifiers
        (r'^(?:batch\s*(?:no|number|\.)?|b\.?\s*no)\b[.:;=\-]?\s*', "BATCH_NUMBER"),
        (r'^(?:lot\s*(?:no|number|\.)?)\b[.:;=\-]?\s*', "LOT_NUMBER"),
        (r'^(?:serial\s*(?:no|number|\.)?|s\.?\s*no)\b[.:;=\-]?\s*', "SERIAL_NUMBER"),
        (r'^(?:model\s*(?:no|number|\.)?)\b[.:;=\-]?\s*', "MODEL_NUMBER"),

        # Consumer Care
        (r'^(?:consumer\s+care|customer\s+(?:care|service|support)|helpline|toll\s*free)\b[.:;=\-]?\s*', "CONSUMER_CARE"),
        (r'^(?:email|e-mail)\b[.:;=\-]?\s*', "EMAIL"),
        (r'^(?:website|web)\b[.:;=\-]?\s*', "WEBSITE"),

        # Country
        (r'^(?:country\s+of\s+origin|made\s+in)\b[.:;=\-]?\s*', "COUNTRY_OF_ORIGIN"),
    ]

    def extract_heading_associations(
        self,
        regions: List[Stage2TextRegion]
    ) -> Tuple[List[Stage3Relationship], Dict[str, Dict[str, Any]]]:
        """Extracts relationships between headings and values.
        
        Returns:
            (relationships_list, region_associations_dict)
            where region_associations_dict maps region_id -> {
                "field_type": str,
                "heading_text": str,
                "value_text": str,
                "confidence": float
            }
        """
        relationships: List[Stage3Relationship] = []
        region_associations: Dict[str, Dict[str, Any]] = {}

        if not regions:
            return relationships, region_associations

        # Sort regions top-to-bottom, left-to-right
        sorted_regions = sorted(regions, key=lambda r: (r.bbox[1] if r.bbox else 0, r.bbox[0] if r.bbox else 0))

        used_as_value: set = set()

        for idx, reg in enumerate(sorted_regions):
            text = reg.normalized_text or reg.raw_text or ""
            text_strip = text.strip()

            matched_heading = None
            matched_field_type = None
            extracted_value = None

            # 1. Check Same-Line Heading with Value
            # e.g. "Net Qty: 200 g", "MRP Rs. 50.00", "Mfg Date: 12/2024"
            for pattern, ftype in self.HEADING_PATTERNS:
                m = re.search(pattern, text_strip, re.I)
                if m:
                    matched_heading = m.group(0).strip(" :;=-")
                    matched_field_type = ftype
                    val_part = text_strip[m.end():].strip(" :;=-")
                    if val_part:
                        extracted_value = val_part
                    break

            if matched_field_type and extracted_value:
                # Same-line heading-value match
                rel = Stage3Relationship(
                    relationship_id=f"REL-{uuid.uuid4().hex[:6].upper()}",
                    field_type=matched_field_type,
                    heading_text=matched_heading,
                    value_text=extracted_value,
                    heading_region_id=reg.region_id,
                    value_region_id=reg.region_id,
                    relationship_confidence=0.98,
                    association_type="SAME_LINE"
                )
                relationships.append(rel)
                region_associations[reg.region_id] = {
                    "field_type": matched_field_type,
                    "heading_text": matched_heading,
                    "value_text": extracted_value,
                    "confidence": 0.98
                }
                continue

            # 2. Check Heading alone on this line, Value on the next line or right adjacent
            # e.g. Line 1: "Manufactured By:", Line 2: "Golden Bake Foods Pvt Ltd"
            if matched_field_type and not extracted_value:
                # Search immediate next region
                if idx + 1 < len(sorted_regions):
                    next_reg = sorted_regions[idx + 1]
                    next_text = (next_reg.normalized_text or next_reg.raw_text or "").strip()

                    # Ensure next region is not another heading
                    is_next_heading = any(re.search(pat, next_text, re.I) for pat, _ in self.HEADING_PATTERNS)
                    if not is_next_heading and next_text and next_reg.region_id not in used_as_value:
                        # Spatial check: next_reg is vertically directly below or to the right
                        if reg.bbox and next_reg.bbox:
                            rx, ry, rw, rh = reg.bbox
                            nx, ny, nw, nh = next_reg.bbox
                            v_gap = ny - (ry + rh)
                            h_gap = nx - (rx + rw)

                            # Close vertical proximity (< 50px) or horizontal proximity (< 80px)
                            if (0 <= v_gap <= 60 and abs(nx - rx) < 180) or (abs(ny - ry) < 20 and 0 <= h_gap < 80):
                                rel = Stage3Relationship(
                                    relationship_id=f"REL-{uuid.uuid4().hex[:6].upper()}",
                                    field_type=matched_field_type,
                                    heading_text=matched_heading,
                                    value_text=next_text,
                                    heading_region_id=reg.region_id,
                                    value_region_id=next_reg.region_id,
                                    relationship_confidence=0.94,
                                    association_type="PROXIMITY"
                                )
                                relationships.append(rel)
                                region_associations[next_reg.region_id] = {
                                    "field_type": matched_field_type,
                                    "heading_text": matched_heading,
                                    "value_text": next_text,
                                    "confidence": 0.94
                                }
                                used_as_value.add(next_reg.region_id)

        return relationships, region_associations
