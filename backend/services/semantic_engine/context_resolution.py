"""
Service 11: Context Resolution Service
======================================
Resolves complex multi-field contexts and relationships:
1. Heading-Value Association Engine:
   Links labels to values across same line, next line, and table rows:
   - "Net Quantity:" -> "50 g"
   - "MRP:" -> "₹299"
   - "Batch:" -> "ABC123"
   - "Mfg:" -> "08/2026"
   - "Manufactured by:" -> "ABC Pvt Ltd"
   - "Consumer Care:" -> "1800-209-1234"
2. Address Decomposition Engine:
   Decomposes commercial entity blocks into separate atomic semantic components:
   - COMPANY_NAME
   - STREET_ADDRESS
   - CITY
   - STATE
   - POSTAL_PIN
3. Table Resolution:
   Resolves tabular structures (e.g. "Serving Size | 50 g" -> SERVING_SIZE).
"""

from typing import List, Dict, Any, Tuple, Optional
import re

from ...models import (
    ExtractedLine,
    UniversalFieldObject,
    UniversalSemanticField,
    BoundingBox,
    SectionType
)
from .layout_analysis import TableRow, LayoutBlock


class DecomposedAddress:
    """Atomic components of a statutory commercial entity declaration."""
    def __init__(
        self,
        company_name: str = "",
        street_address: str = "",
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_pin: Optional[str] = None,
        entity_role: str = "MANUFACTURER",
        full_text: str = ""
    ):
        self.company_name = company_name
        self.street_address = street_address
        self.city = city
        self.state = state
        self.postal_pin = postal_pin
        self.entity_role = entity_role
        self.full_text = full_text


class ContextResolutionService:
    """Performs heading-value linkage and commercial entity address decomposition."""

    INDIAN_STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi"
    ]

    MAJOR_CITIES = [
        "Mumbai", "Delhi", "Bengaluru", "Bangalore", "Kolkata", "Chennai", "Hyderabad",
        "Pune", "Ahmedabad", "Gurugram", "Gurgaon", "Noida", "Baddi", "Haridwar",
        "Solan", "Alwar", "Thane", "Nagpur", "Indore", "Surat", "Jaipur", "Lucknow",
        "Kanpur", "Bhiwandi", "Ratnagiri", "Khurja", "Morena", "Gwalior", "Dehradun",
        "Karnal", "Bidadi"
    ]

    def __init__(self):
        pass

    def decompose_commercial_address(
        self,
        lines: List[str],
        entity_role: str = "MANUFACTURER"
    ) -> DecomposedAddress:
        """Splits multi-line commercial entity block into Company, Street, City, State, and PIN."""
        if not lines:
            return DecomposedAddress(entity_role=entity_role)

        full_text = " ".join(lines)
        company_name = ""
        street_parts: List[str] = []
        city: Optional[str] = None
        state: Optional[str] = None
        pin_code: Optional[str] = None

        # Extract 6-digit PIN
        pin_m = re.search(r'\b([1-9][0-9]{5})\b', full_text)
        if pin_m:
            pin_code = pin_m.group(1)

        # Extract State
        for s in self.INDIAN_STATES:
            if re.search(rf'\b{re.escape(s)}\b', full_text, re.I):
                state = s
                break

        # Extract City
        for c in self.MAJOR_CITIES:
            if re.search(rf'\b{re.escape(c)}\b', full_text, re.I):
                city = c
                break

        # Clean corporate prefix from line 1
        first_line = lines[0]
        cleaned_first = re.sub(
            r'^(?:manufactured\s*(?:and\s*packaged\s*)?by|mfd\.?\s*by|packed\s*by|pkd\.?\s*by|imported\s*by|marketed\s*by|produced\s*by)[:.\-\s]*',
            '',
            first_line,
            flags=re.I
        ).strip()

        # If corporate entity suffix is split across line 1 and line 2 (e.g. "Hindustan Unilever" \n "Limited")
        if len(lines) > 1 and re.match(r'^(?:Limited|Ltd\.?|LLP|Inc\.?|Corporation)\b', lines[1].strip(), re.I):
            company_name = f"{cleaned_first} {lines[1].strip()}".strip()
            remaining_lines = lines[2:]
        else:
            company_name = cleaned_first
            remaining_lines = lines[1:]

        # Street address is remainder
        street_address = ", ".join(l.strip() for l in remaining_lines if l.strip())

        return DecomposedAddress(
            company_name=company_name,
            street_address=street_address,
            city=city,
            state=state,
            postal_pin=pin_code,
            entity_role=entity_role,
            full_text=full_text
        )

    def resolve_heading_associations(
        self,
        lines: List[ExtractedLine]
    ) -> List[Tuple[str, str, ExtractedLine]]:
        """Associates label lines with subsequent value lines (e.g., 'Net Quantity:' on line 1, '50 g' on line 2)."""
        associations: List[Tuple[str, str, ExtractedLine]] = []
        heading_keys = [
            (r'^(?:Net\s*(?:Qty|Quantity|Weight|Wt|Content)[:.\-\s]*)$', UniversalSemanticField.NET_QUANTITY),
            (r'^(?:M\.?R\.?P\.?|Maximum\s*Retail\s*Price)[:.\-\s]*$', UniversalSemanticField.MRP),
            (r'^(?:Batch\s*(?:No\.?|Number)?|B\.?\s*No\.?)[:.\-\s]*$', UniversalSemanticField.BATCH_NUMBER),
            (r'^(?:Mfg\s*Date|Date\s*of\s*Mfg|Date\s*of\s*Manufacture)[:.\-\s]*$', UniversalSemanticField.DATE_OF_MANUFACTURE),
            (r'^(?:Pkd\s*Date|Date\s*of\s*Packing)[:.\-\s]*$', UniversalSemanticField.DATE_OF_PACKING),
            (r'^(?:Best\s*Before)[:.\-\s]*$', UniversalSemanticField.BEST_BEFORE),
            (r'^(?:Consumer\s*Care|Customer\s*Care)[:.\-\s]*$', UniversalSemanticField.CONSUMER_CARE),
        ]

        for i in range(len(lines) - 1):
            curr_text = lines[i].text.strip()
            next_line = lines[i + 1]

            for pat, field_name in heading_keys:
                if re.match(pat, curr_text, re.I):
                    associations.append((field_name, curr_text, next_line))
                    break

        return associations

    def resolve_table_rows_to_fields(
        self,
        table_rows: List[TableRow],
        surface: str
    ) -> List[UniversalFieldObject]:
        """Converts structured table rows into UniversalFieldObjects with anti-confusion guarantees."""
        fields: List[UniversalFieldObject] = []

        for row in table_rows:
            h_lower = row.header.lower()

            if "serving size" in h_lower or "portion" in h_lower:
                fields.append(UniversalFieldObject(
                    raw_text=row.value,
                    normalized_value=row.value,
                    candidate_fields=[UniversalSemanticField.SERVING_SIZE, UniversalSemanticField.OTHER_QUANTITY],
                    selected_field=UniversalSemanticField.SERVING_SIZE,
                    semantic_confidence=0.98,
                    evidence_bbox=row.bbox,
                    evidence_context=row.raw_text,
                    source_panel=surface,
                    reason="Identified within structured nutrition table row under Serving Size header.",
                    status="RESOLVED",
                    section=SectionType.NUTRITION_INFORMATION
                ))
            elif any(k in h_lower for k in ["net qty", "net weight", "net quantity"]):
                fields.append(UniversalFieldObject(
                    raw_text=row.value,
                    normalized_value=row.value,
                    candidate_fields=[UniversalSemanticField.NET_QUANTITY],
                    selected_field=UniversalSemanticField.NET_QUANTITY,
                    semantic_confidence=0.98,
                    evidence_bbox=row.bbox,
                    evidence_context=row.raw_text,
                    source_panel=surface,
                    reason="Identified within specification table under Net Quantity header.",
                    status="RESOLVED",
                    section=SectionType.PRODUCT_DETAILS
                ))

        return fields
