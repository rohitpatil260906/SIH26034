"""
Service 9: Entity Extraction Service
====================================
Extracts raw entities without committing to premature semantic fields.
STRICT RULE: Never classify numbers or tokens in isolation!
Extracts:
- Quantities with units (50 g, 500 mg, 1 L, 10 mm, 40 cm, 12 pieces, 1 N)
- Currency and price values (₹299, Rs. 240.00, 299/-, USP: Rs. 0.48/g)
- Dates (12/2024, 08/2026, August 2026, 24 Months)
- Postal PIN codes (400013, 110001, 560100)
- Corporate entities (Pvt Ltd, Limited, LLP, Inc, Co)
- Codes (Batch ABC123, Model 50, Lot 892A)
- Contact endpoints (Helplines, Emails, Websites)
"""

from typing import List, Dict, Any, Tuple, Optional
import re

from ...models import ExtractedLine, UniversalSemanticField, BoundingBox


class RawCandidateEntity:
    """A detected raw entity with open candidate interpretations."""
    def __init__(
        self,
        raw_text: str,
        entity_type: str,  # "QUANTITY", "PRICE", "DATE", "PIN", "COMPANY", "CODE", "CONTACT"
        normalized_value: Any,
        unit: Optional[str] = None,
        candidate_fields: Optional[List[str]] = None,
        line_index: int = 0,
        bbox: Optional[BoundingBox] = None,
        surrounding_text: str = ""
    ):
        self.raw_text = raw_text
        self.entity_type = entity_type
        self.normalized_value = normalized_value
        self.unit = unit
        self.candidate_fields = candidate_fields or []
        self.line_index = line_index
        self.bbox = bbox
        self.surrounding_text = surrounding_text


# Unit standardizer map to statutory SI symbols under Rule 13
UNIT_NORMALIZATION = {
    "g": "g", "gm": "g", "gms": "g", "gram": "g", "grams": "g", "ग्राम": "g",
    "kg": "kg", "kgs": "kg", "kilogram": "kg", "किलोग्राम": "kg", "किलो": "kg",
    "mg": "mg", "mgs": "mg", "milligram": "mg",
    "ml": "ml", "mls": "ml", "millilitre": "ml", "milliliter": "ml", "मिली": "ml",
    "l": "l", "ltr": "l", "litre": "l", "liter": "l", "लीटर": "l",
    "cm": "cm", "cms": "cm", "centimetre": "cm", "centimeter": "cm",
    "m": "m", "metre": "m", "meter": "m",
    "mm": "mm", "millimetre": "mm", "millimeter": "mm",
    "n": "N", "u": "Unit", "unit": "Unit", "units": "Unit", "pcs": "pieces", "pieces": "pieces", "पैक": "pieces"
}


class EntityExtractionService:
    """Extracts raw candidate entities from text lines."""

    # 1. Quantity regex: quantity + unit
    QTY_RE = re.compile(
        r'\b([0-9]+(?:\.[0-9]+)?)\s*(gms|kgs|gm|g|kg|mg|ml|l|ltr|cm|mm|m|N|units?|pieces?|पैक|ग्राम|किलो(?:ग्राम)?|मिली)\b',
        re.I
    )

    # 2. Currency regex: ₹ / Rs / INR or slash-dash
    PRICE_RE = re.compile(
        r'(?:(?:MRP|M\.?R\.?P\.?|PRICE|मूल्य)\s*[:.\-\s]*)?(?:₹|Rs\.?|INR)\s*([0-9]+(?:\.[0-9]{1,2})?)|([0-9]{2,5}(?:\.[0-9]{2})?)\s*\/\-',
        re.I
    )

    # 3. Date regex
    DATE_RE = re.compile(
        r'\b((?:[0-9]{1,2}[\/\-\.])?[0-9]{1,2}[\/\-\.][0-9]{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*[\'\-]?[0-9]{2,4}|\d{1,2}\s*months?)\b',
        re.I
    )

    # 4. Postal PIN regex
    PIN_RE = re.compile(r'\b([1-9][0-9]{5})\b')

    # 5. Corporate Suffix regex
    COMPANY_RE = re.compile(
        r'\b([A-Za-z0-9\s.,&\'-]+?(?:Pvt\.?\s*Ltd\.?|Private\s*Limited|Ltd\.?|Limited|LLP|Inc\.?|Corporation|Enterprises|Laboratories|Industries))\b',
        re.I
    )

    def extract_candidates_from_lines(
        self,
        lines: List[ExtractedLine]
    ) -> List[RawCandidateEntity]:
        """Extracts candidate entities with multiple candidate interpretations."""
        candidates: List[RawCandidateEntity] = []

        for idx, line in enumerate(lines):
            txt = line.text.strip()
            surrounding = ""
            start = max(0, idx - 2)
            end = min(len(lines), idx + 3)
            surrounding = " | ".join(lines[j].text.strip() for j in range(start, end))

            # A. Extract Quantities
            for m in self.QTY_RE.finditer(txt):
                raw_num = m.group(1)
                raw_unit = m.group(2).lower()
                norm_unit = UNIT_NORMALIZATION.get(raw_unit, raw_unit)
                try:
                    norm_val = float(raw_num) if "." in raw_num else int(raw_num)
                except ValueError:
                    norm_val = raw_num

                # Open candidate fields
                cand_fields = [
                    UniversalSemanticField.NET_QUANTITY,
                    UniversalSemanticField.SERVING_SIZE,
                    UniversalSemanticField.INGREDIENT_QUANTITY,
                    UniversalSemanticField.OTHER_QUANTITY
                ]
                if norm_unit in ["cm", "mm", "m"]:
                    cand_fields = [
                        UniversalSemanticField.PRODUCT_DIMENSION,
                        UniversalSemanticField.DIMENSION,
                        UniversalSemanticField.NET_QUANTITY,
                        UniversalSemanticField.OTHER_QUANTITY
                    ]
                elif norm_unit in ["pieces", "Unit", "N"]:
                    cand_fields = [
                        UniversalSemanticField.NET_QUANTITY,
                        UniversalSemanticField.QUANTITY_COUNT,
                        UniversalSemanticField.OTHER_QUANTITY
                    ]

                candidates.append(RawCandidateEntity(
                    raw_text=m.group(0),
                    entity_type="QUANTITY",
                    normalized_value=norm_val,
                    unit=norm_unit,
                    candidate_fields=cand_fields,
                    line_index=line.line_index,
                    bbox=line.bbox,
                    surrounding_text=surrounding
                ))

            # B. Extract Currency / Prices
            for m in self.PRICE_RE.finditer(txt):
                val_str = m.group(1) or m.group(2)
                if val_str:
                    try:
                        p_val = float(val_str)
                    except ValueError:
                        p_val = val_str

                    cand_fields = [
                        UniversalSemanticField.MRP,
                        UniversalSemanticField.PRICE_CANDIDATE,
                        UniversalSemanticField.UNIT_PRICE
                    ]
                    candidates.append(RawCandidateEntity(
                        raw_text=m.group(0),
                        entity_type="PRICE",
                        normalized_value=p_val,
                        unit="INR",
                        candidate_fields=cand_fields,
                        line_index=line.line_index,
                        bbox=line.bbox,
                        surrounding_text=surrounding
                    ))

            # C. Extract Postal PINs
            for m in self.PIN_RE.finditer(txt):
                pin_val = m.group(1)
                candidates.append(RawCandidateEntity(
                    raw_text=pin_val,
                    entity_type="PIN",
                    normalized_value=pin_val,
                    unit=None,
                    candidate_fields=[
                        UniversalSemanticField.POSTAL_PIN,
                        UniversalSemanticField.PRODUCT_CODE,
                        UniversalSemanticField.UNKNOWN
                    ],
                    line_index=line.line_index,
                    bbox=line.bbox,
                    surrounding_text=surrounding
                ))

            # D. Extract Corporate Entities
            for m in self.COMPANY_RE.finditer(txt):
                comp_name = m.group(1).strip()
                if len(comp_name) > 4:
                    candidates.append(RawCandidateEntity(
                        raw_text=comp_name,
                        entity_type="COMPANY",
                        normalized_value=comp_name,
                        unit=None,
                        candidate_fields=[
                            UniversalSemanticField.MANUFACTURER,
                            UniversalSemanticField.PACKER,
                            UniversalSemanticField.MARKETER,
                            UniversalSemanticField.IMPORTER,
                            UniversalSemanticField.BRAND_OWNER
                        ],
                        line_index=line.line_index,
                        bbox=line.bbox,
                        surrounding_text=surrounding
                    ))

            # E. Extract Dates
            for m in self.DATE_RE.finditer(txt):
                date_str = m.group(1).strip()
                candidates.append(RawCandidateEntity(
                    raw_text=date_str,
                    entity_type="DATE",
                    normalized_value=date_str,
                    unit=None,
                    candidate_fields=[
                        UniversalSemanticField.DATE_OF_MANUFACTURE,
                        UniversalSemanticField.DATE_OF_PACKING,
                        UniversalSemanticField.EXPIRY,
                        UniversalSemanticField.BEST_BEFORE,
                        UniversalSemanticField.USE_BY,
                        UniversalSemanticField.OTHER_DATE
                    ],
                    line_index=line.line_index,
                    bbox=line.bbox,
                    surrounding_text=surrounding
                ))

        return candidates
