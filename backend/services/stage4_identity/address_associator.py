"""
Stage 4: Address to Company Associator Service
=============================================
Associates physical address declarations and 6-digit postal PIN codes
with their corresponding commercial entity (Manufacturer, Packer, Marketer, Importer):
- Spatial proximity & sequential reading order
- Line ordering within entity declaration blocks
- Section boundary isolation
- Postal PIN extraction ([1-9][0-9]{5})
- Bounding box aggregation
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from ...models import Stage2TextRegion


class AddressAssociatorService:
    """Associates address lines and PIN codes to their corporate entities."""

    ADDRESS_LINE_REGEX = re.compile(
        r'\b(?:plot|survey|khasra|bldg|building|floor|industrial\s+area|ind\.\s*area|g\.?i\.?d\.?c\.?|m\.?i\.?d\.?c\.?|estate|sector|phase|nagar|marg|road|street|lane|chowk|village|dist\.?|district|taluka|tehsil|near|opp\.?|opposite|post|p\.?o\.?|city|state)\b',
        re.I
    )

    PIN_REGEX = re.compile(r'\b([1-9][0-9]{5})\b')

    INDIAN_STATES = {
        "maharashtra", "delhi", "karnataka", "tamil nadu", "gujarat", "uttar pradesh",
        "west bengal", "rajasthan", "telangana", "andhra pradesh", "kerala", "punjab",
        "haryana", "bihar", "odisha", "assam", "goa", "madhya pradesh", "jharkhand",
        "uttarakhand", "himachal pradesh", "mumbai", "bengaluru", "chennai", "kolkata",
        "hyderabad", "pune", "ahmedabad", "gurugram", "noida", "new delhi"
    }

    def is_address_text(self, text: str) -> bool:
        """Determines if a text line has address signals or state/city mentions."""
        if not text:
            return False
        clean = text.lower()
        if self.ADDRESS_LINE_REGEX.search(clean):
            return True
        if self.PIN_REGEX.search(clean):
            return True
        if any(state in clean for state in self.INDIAN_STATES):
            return True
        return False

    def extract_pin(self, text: str) -> Optional[str]:
        """Extracts 6-digit postal PIN code from text."""
        match = self.PIN_REGEX.search(text)
        return match.group(1) if match else None

    def clean_address_line(self, text: str) -> str:
        """Cleans address text, removing role labels or company prefixes."""
        # Strip Mfg By, etc., if on same line
        clean = re.sub(r'^(?:mfg|manufactured|packed|marketed|imported|pkd|mkt|imp)\s*(?:by|at|for)?[:\s\-]*', '', text, flags=re.I)
        return clean.strip()

    def associate_address_block(
        self,
        company_region_idx: int,
        all_regions: List[Stage2TextRegion],
        max_lookahead: int = 4
    ) -> Tuple[str, Optional[str], List[str], List[float]]:
        """Scans succeeding text regions to associate address lines and PIN codes.
        
        Returns:
            (combined_address_str, pin_code, consumed_region_ids, aggregated_bbox)
        """
        address_parts: List[str] = []
        found_pin: Optional[str] = None
        consumed_ids: List[str] = []
        
        comp_reg = all_regions[company_region_idx]
        agg_bbox = list(comp_reg.bbox) if comp_reg.bbox else []

        start_idx = company_region_idx + 1
        end_idx = min(len(all_regions), start_idx + max_lookahead)

        for i in range(start_idx, end_idx):
            reg = all_regions[i]
            txt = reg.normalized_text or reg.raw_text or ""

            # Check if this line is already another role header (e.g. "Marketed By:") or major section break
            if re.search(r'\b(?:manufactured|packed|marketed|imported|mfg|pkd|mkt|imp)\s+by\b', txt, re.I):
                break
            if re.search(r'\b(?:ingredients|nutritional\s+facts)\b', txt, re.I):
                break

            # If it has address signals or PIN
            if self.is_address_text(txt):
                cleaned_line = self.clean_address_line(txt)
                pin = self.extract_pin(txt)
                if pin and not found_pin:
                    found_pin = pin
                
                address_parts.append(cleaned_line)
                consumed_ids.append(reg.region_id)

                # Expand bbox
                if reg.bbox and len(reg.bbox) == 4:
                    if not agg_bbox or len(agg_bbox) != 4:
                        agg_bbox = list(reg.bbox)
                    else:
                        bx, by, bw, bh = reg.bbox
                        x1 = min(agg_bbox[0], bx)
                        y1 = min(agg_bbox[1], by)
                        x2 = max(agg_bbox[0] + agg_bbox[2], bx + bw)
                        y2 = max(agg_bbox[1] + agg_bbox[3], by + bh)
                        agg_bbox = [x1, y1, x2 - x1, y2 - y1]

        combined_addr = ", ".join(address_parts)
        return combined_addr, found_pin, consumed_ids, agg_bbox
