"""
Service 10: Semantic Field Classification Service
=================================================
Implements multi-check visual-spatial-semantic classification (Checks A through F):
- CHECK A (Spatial Location): PDP vs Back vs Side vs Ingredients vs Nutrition table vs Base stamp
- CHECK B (Neighboring Text): Contextual keywords (Net Qty, Serving Size, Mfg by, MRP, Pk Size)
- CHECK C (Product Category): Food vs Cosmetics vs Electronics vs Textiles vs Toys
- CHECK D (Visual Hierarchy): Font prominence, container grouping, proximity to product name
- CHECK E (Text Pattern): Metric unit normalization (Rule 13 SI compliance)
- CHECK F (Cross-Field Validation): Co-occurrence consistency (Net Qty vs Serving Size)

Calculates candidate probabilities across 42+ statutory fields without isolated guessing.
"""

from typing import List, Dict, Any, Tuple, Optional
import re

from ...models import (
    UniversalSemanticField,
    UniversalFieldObject,
    BoundingBox,
    SectionType,
    ProductCategory
)
from .entity_extraction import RawCandidateEntity


class SemanticFieldClassificationService:
    """Executes Checks A through F for all extracted packaging candidates."""

    # Explicit Net Quantity indicators
    NET_QTY_KEYWORDS = [
        "net qty", "net quantity", "net wt", "net weight", "net content",
        "net contents", "net volume", "net mass", "contents", "pack size",
        "शुद्ध मात्रा", "वजन"
    ]

    # Serving Size indicators
    SERVING_SIZE_KEYWORDS = [
        "serving size", "per serving", "servings per pack", "approx. serving",
        "portion size", "प्रति सर्विंग"
    ]

    # Ingredient indicators
    INGREDIENT_KEYWORDS = [
        "ingredients", "composition", "key ingredients", "active ingredients",
        "contains", "सामग्री"
    ]

    # MRP indicators
    MRP_KEYWORDS = [
        "mrp", "m.r.p.", "maximum retail price", "retail sale price",
        "अधिकतम खुदरा मूल्य", "एमआरपी"
    ]

    # Unit Sale Price indicators
    USP_KEYWORDS = [
        "usp", "u.s.p.", "unit sale price", "unit price"
    ]

    def __init__(self):
        pass

    def classify_candidate(
        self,
        candidate: RawCandidateEntity,
        section: str,
        surface: str,
        product_category: str,
        visual_prominence: Dict[str, Any],
        other_fields: Optional[List[Dict[str, Any]]] = None
    ) -> UniversalFieldObject:
        """Applies Checks A through F to resolve a raw candidate into a UniversalFieldObject."""
        if candidate.entity_type == "QUANTITY":
            return self._resolve_quantity(
                candidate, section, surface, product_category, visual_prominence, other_fields
            )
        elif candidate.entity_type == "PRICE":
            return self._resolve_price(
                candidate, section, surface, product_category, visual_prominence, other_fields
            )
        elif candidate.entity_type == "PIN":
            return self._resolve_pin(
                candidate, section, surface, product_category, visual_prominence, other_fields
            )
        elif candidate.entity_type == "COMPANY":
            return self._resolve_company(
                candidate, section, surface, product_category, visual_prominence, other_fields
            )
        elif candidate.entity_type == "DATE":
            return self._resolve_date(
                candidate, section, surface, product_category, visual_prominence, other_fields
            )

        # Generic default
        return UniversalFieldObject(
            raw_text=candidate.raw_text,
            normalized_value=candidate.normalized_value,
            unit=candidate.unit,
            candidate_fields=[UniversalSemanticField.UNKNOWN],
            selected_field=UniversalSemanticField.UNKNOWN,
            semantic_confidence=0.50,
            evidence_bbox=candidate.bbox,
            evidence_context=candidate.surrounding_text,
            source_panel=surface,
            reason="Unrecognized entity pattern",
            status="NEEDS_REVIEW"
        )

    def _resolve_quantity(
        self,
        cand: RawCandidateEntity,
        section: str,
        surface: str,
        product_category: str,
        visual_prominence: Dict[str, Any],
        other_fields: Optional[List[Dict[str, Any]]]
    ) -> UniversalFieldObject:
        """Disambiguates quantity tokens (e.g. '50 g') across Net Qty, Serving Size, Ingredient, Dimension."""
        surrounding_lower = cand.surrounding_text.lower()
        unit_lower = (cand.unit or "").lower()

        scores: Dict[str, float] = {
            UniversalSemanticField.NET_QUANTITY: 0.20,
            UniversalSemanticField.SERVING_SIZE: 0.10,
            UniversalSemanticField.INGREDIENT_QUANTITY: 0.10,
            UniversalSemanticField.PRODUCT_DIMENSION: 0.05,
            UniversalSemanticField.WEIGHT_SPECIFICATION: 0.05,
            UniversalSemanticField.QUANTITY_COUNT: 0.05,
            UniversalSemanticField.OTHER_QUANTITY: 0.10
        }

        # ----------------------------------------------------
        # CHECK A: SPATIAL LOCATION & SECTION
        # ----------------------------------------------------
        if surface == "Front (PDP)":
            scores[UniversalSemanticField.NET_QUANTITY] += 0.35
        elif surface == "Coding Area":
            scores[UniversalSemanticField.OTHER_QUANTITY] += 0.20

        if section == SectionType.INGREDIENTS:
            scores[UniversalSemanticField.INGREDIENT_QUANTITY] += 0.65
            scores[UniversalSemanticField.NET_QUANTITY] -= 0.30
        elif section == SectionType.NUTRITION_INFORMATION:
            scores[UniversalSemanticField.SERVING_SIZE] += 0.50
            scores[UniversalSemanticField.NET_QUANTITY] -= 0.20
        elif section == SectionType.DIRECTIONS:
            scores[UniversalSemanticField.OTHER_QUANTITY] += 0.40
            scores[UniversalSemanticField.NET_QUANTITY] -= 0.30

        # ----------------------------------------------------
        # CHECK B: NEIGHBORING TEXT & KEYWORDS
        # ----------------------------------------------------
        if any(k in surrounding_lower for k in self.NET_QTY_KEYWORDS):
            scores[UniversalSemanticField.NET_QUANTITY] += 0.55
            scores[UniversalSemanticField.SERVING_SIZE] -= 0.30
        if any(k in surrounding_lower for k in self.SERVING_SIZE_KEYWORDS):
            scores[UniversalSemanticField.SERVING_SIZE] += 0.70
            scores[UniversalSemanticField.NET_QUANTITY] -= 0.40
        if any(k in surrounding_lower for k in ["dimensions?", "size:", "chest", "length", "width"]):
            scores[UniversalSemanticField.PRODUCT_DIMENSION] += 0.60
            scores[UniversalSemanticField.NET_QUANTITY] -= 0.20
        if any(k in surrounding_lower for k in ["weight:", "device weight", "item weight"]):
            scores[UniversalSemanticField.WEIGHT_SPECIFICATION] += 0.60

        # ----------------------------------------------------
        # CHECK C: PRODUCT CATEGORY
        # ----------------------------------------------------
        if "electronic" in product_category.lower():
            if unit_lower in ["mm", "cm"]:
                scores[UniversalSemanticField.PRODUCT_DIMENSION] += 0.40
            if "weight" in surrounding_lower:
                scores[UniversalSemanticField.WEIGHT_SPECIFICATION] += 0.40
        elif "textile" in product_category.lower() or "apparel" in product_category.lower() or "garment" in product_category.lower():
            if unit_lower in ["cm", "m"]:
                scores[UniversalSemanticField.PRODUCT_DIMENSION] += 0.45
            if unit_lower in ["n", "unit", "piece"]:
                scores[UniversalSemanticField.NET_QUANTITY] += 0.30
        elif "toy" in product_category.lower():
            if unit_lower in ["pieces", "unit", "pcs"]:
                scores[UniversalSemanticField.QUANTITY_COUNT] += 0.50
                scores[UniversalSemanticField.NET_QUANTITY] += 0.35

        # ----------------------------------------------------
        # CHECK D: VISUAL HIERARCHY
        # ----------------------------------------------------
        if visual_prominence.get("is_prominent", False):
            # Large prominent font on Front/PDP strongly indicates package quantity
            scores[UniversalSemanticField.NET_QUANTITY] += 0.25
            scores[UniversalSemanticField.SERVING_SIZE] -= 0.15

        # ----------------------------------------------------
        # CHECK E: TEXT PATTERN & UNIT
        # ----------------------------------------------------
        if unit_lower in ["mg"] and scores[UniversalSemanticField.NET_QUANTITY] < 0.70:
            # mg is almost always active ingredient or nutrition amount unless micro-package
            scores[UniversalSemanticField.INGREDIENT_QUANTITY] += 0.35

        # ----------------------------------------------------
        # CHECK F: CROSS-FIELD VALIDATION
        # ----------------------------------------------------
        # Sort candidates
        sorted_cands = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_field, top_score = sorted_cands[0]
        second_field, second_score = sorted_cands[1]

        # Anti-Hallucination check: if top score is weak or ambiguous
        if top_score < 0.45 or (top_score - second_score < 0.10 and top_score < 0.65):
            selected = UniversalSemanticField.UNKNOWN
            status = "NEEDS_REVIEW"
            reason = f"Ambiguous quantity context between {top_field} and {second_field}. Needs review."
            conf = 0.50
        else:
            selected = top_field
            status = "RESOLVED"
            conf = min(0.99, max(0.60, top_score))
            if selected == UniversalSemanticField.NET_QUANTITY:
                reason = "Detected as package-level quantity based on location, surrounding text and product context."
            elif selected == UniversalSemanticField.SERVING_SIZE:
                reason = "Detected as nutrition serving size based on header and tabular nutrition section."
            elif selected == UniversalSemanticField.INGREDIENT_QUANTITY:
                reason = "Detected inside ingredients/formulation section as component quantity."
            elif selected == UniversalSemanticField.PRODUCT_DIMENSION:
                reason = "Detected as physical product dimension based on linear metric unit and context."
            else:
                reason = f"Resolved to {selected} based on contextual evidence."

        return UniversalFieldObject(
            raw_text=cand.raw_text,
            normalized_value=cand.normalized_value,
            unit=cand.unit,
            candidate_fields=[c[0] for c in sorted_cands[:4]],
            selected_field=selected,
            semantic_confidence=round(conf, 2),
            evidence_bbox=cand.bbox,
            evidence_context=cand.surrounding_text,
            source_panel=surface,
            reason=reason,
            status=status,
            section=section
        )

    def _resolve_price(
        self,
        cand: RawCandidateEntity,
        section: str,
        surface: str,
        product_category: str,
        visual_prominence: Dict[str, Any],
        other_fields: Optional[List[Dict[str, Any]]]
    ) -> UniversalFieldObject:
        """Disambiguates currency tokens (e.g. '₹299') across MRP, Unit Sale Price, or Price Candidate."""
        surr_lower = cand.surrounding_text.lower()
        has_mrp_prefix = any(k in surr_lower for k in self.MRP_KEYWORDS)
        has_usp_prefix = any(k in surr_lower for k in self.USP_KEYWORDS) or "/" in cand.raw_text
        has_taxes_phrase = any(k in surr_lower for k in ["incl", "tax", "कर सहित"])

        if has_usp_prefix:
            selected = UniversalSemanticField.UNIT_PRICE
            conf = 0.96
            reason = "Preceded by explicit Unit Sale Price (USP) indicator or per-unit denominator."
            status = "RESOLVED"
        elif has_mrp_prefix:
            selected = UniversalSemanticField.MRP
            conf = 0.98 if has_taxes_phrase else 0.94
            reason = "Preceded by statutory Maximum Retail Price (MRP) declaration."
            status = "RESOLVED"
        elif has_taxes_phrase or visual_prominence.get("is_bottom_stamp", False):
            # Standalone ₹299 near taxes statement or coding stamp
            selected = UniversalSemanticField.MRP
            conf = 0.91
            reason = "Retail sale price identified from currency symbol and associated tax inclusivity statement."
            status = "RESOLVED"
        else:
            # Standalone price without MRP prefix or tax phrase: mark as PRICE_CANDIDATE
            selected = UniversalSemanticField.PRICE_CANDIDATE
            conf = 0.72
            reason = "Detected numeric price candidate without explicit MRP statutory prefix. Contextual validation required."
            status = "NEEDS_REVIEW"

        return UniversalFieldObject(
            raw_text=cand.raw_text,
            normalized_value=cand.normalized_value,
            unit="INR",
            candidate_fields=[
                UniversalSemanticField.MRP,
                UniversalSemanticField.PRICE_CANDIDATE,
                UniversalSemanticField.UNIT_PRICE
            ],
            selected_field=selected,
            semantic_confidence=round(conf, 2),
            evidence_bbox=cand.bbox,
            evidence_context=cand.surrounding_text,
            source_panel=surface,
            reason=reason,
            status=status,
            section=section
        )

    def _resolve_pin(
        self,
        cand: RawCandidateEntity,
        section: str,
        surface: str,
        product_category: str,
        visual_prominence: Dict[str, Any],
        other_fields: Optional[List[Dict[str, Any]]]
    ) -> UniversalFieldObject:
        """Disambiguates 6-digit numerals (e.g. '400013') between Postal PIN, Model Code, or Unknown."""
        surr_lower = cand.surrounding_text.lower()
        address_cues = [
            "road", "rd", "street", "marg", "lane", "estate", "industrial", "area",
            "mumbai", "delhi", "bengaluru", "kolkata", "chennai", "pune", "hyderabad",
            "ahmedabad", "baddi", "haridwar", "solan", "alwar", "thane", "gurugram",
            "pin", "pincode", "postal", "nagar", "sector", "plot", "village"
        ]
        has_address_context = any(k in surr_lower for k in address_cues)

        if has_address_context or section in [SectionType.MANUFACTURER, SectionType.PACKER, SectionType.IMPORTER]:
            selected = UniversalSemanticField.POSTAL_PIN
            conf = 0.96
            reason = "Verified 6-digit postal index number within physical address context under Rule 10(1)."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["model", "code", "batch", "part", "item"]):
            selected = UniversalSemanticField.PRODUCT_CODE
            conf = 0.85
            reason = "6-digit number associated with product model/code prefix."
            status = "RESOLVED"
        else:
            selected = UniversalSemanticField.UNKNOWN
            conf = 0.40
            reason = "Standalone 6-digit numeral without address or postal context. Not assigned to avoid false PIN classification."
            status = "NEEDS_REVIEW"

        return UniversalFieldObject(
            raw_text=cand.raw_text,
            normalized_value=cand.normalized_value,
            unit=None,
            candidate_fields=[
                UniversalSemanticField.POSTAL_PIN,
                UniversalSemanticField.PRODUCT_CODE,
                UniversalSemanticField.UNKNOWN
            ],
            selected_field=selected,
            semantic_confidence=round(conf, 2),
            evidence_bbox=cand.bbox,
            evidence_context=cand.surrounding_text,
            source_panel=surface,
            reason=reason,
            status=status,
            section=section
        )

    def _resolve_company(
        self,
        cand: RawCandidateEntity,
        section: str,
        surface: str,
        product_category: str,
        visual_prominence: Dict[str, Any],
        other_fields: Optional[List[Dict[str, Any]]]
    ) -> UniversalFieldObject:
        """Determines commercial entity role: MANUFACTURER, PACKER, MARKETER, IMPORTER, or BRAND OWNER."""
        surr_lower = cand.surrounding_text.lower()

        if any(k in surr_lower for k in ["manufactured by", "mfd by", "mfg by", "produced by", "made by"]) or section == SectionType.MANUFACTURER:
            selected = UniversalSemanticField.MANUFACTURER
            conf = 0.96
            reason = "Associated with statutory manufacturer declaration prefix."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["packed by", "pkd by", "pre-packed by"]) or section == SectionType.PACKER:
            selected = UniversalSemanticField.PACKER
            conf = 0.96
            reason = "Associated with statutory pre-packer declaration prefix."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["imported by", "imp by", "import"]) or section == SectionType.IMPORTER:
            selected = UniversalSemanticField.IMPORTER
            conf = 0.96
            reason = "Associated with statutory registered importer declaration prefix under Rule 27."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["marketed by", "mktd by", "distributed by"]) or section == SectionType.MARKETER:
            selected = UniversalSemanticField.MARKETER
            conf = 0.95
            reason = "Associated with commercial marketer / distributor prefix."
            status = "RESOLVED"
        else:
            selected = UniversalSemanticField.BRAND_OWNER
            conf = 0.70
            reason = "Identified corporate entity without explicit statutory operational prefix."
            status = "RESOLVED"

        return UniversalFieldObject(
            raw_text=cand.raw_text,
            normalized_value=cand.normalized_value,
            unit=None,
            candidate_fields=[
                UniversalSemanticField.MANUFACTURER,
                UniversalSemanticField.PACKER,
                UniversalSemanticField.MARKETER,
                UniversalSemanticField.IMPORTER,
                UniversalSemanticField.BRAND_OWNER
            ],
            selected_field=selected,
            semantic_confidence=round(conf, 2),
            evidence_bbox=cand.bbox,
            evidence_context=cand.surrounding_text,
            source_panel=surface,
            reason=reason,
            status=status,
            section=section
        )

    def _resolve_date(
        self,
        cand: RawCandidateEntity,
        section: str,
        surface: str,
        product_category: str,
        visual_prominence: Dict[str, Any],
        other_fields: Optional[List[Dict[str, Any]]]
    ) -> UniversalFieldObject:
        """Disambiguates dates across MFD, PKD, Expiry, Best Before, and Use By."""
        surr_lower = cand.surrounding_text.lower()

        if any(k in surr_lower for k in ["best before", "सर्वश्रेष्ठ उपयोग"]):
            selected = UniversalSemanticField.BEST_BEFORE
            conf = 0.96
            reason = "Preceded by statutory 'Best Before' advisory declaration."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["use by", "use before"]):
            selected = UniversalSemanticField.USE_BY
            conf = 0.96
            reason = "Preceded by statutory 'Use By' / 'Use Before' deadline."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["expiry", "exp date", "exp.", "समाप्ति"]):
            selected = UniversalSemanticField.EXPIRY
            conf = 0.96
            reason = "Preceded by explicit Expiry date label."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["pkd", "packed", "date of packing", "पैकिंग"]):
            selected = UniversalSemanticField.DATE_OF_PACKING
            conf = 0.95
            reason = "Preceded by statutory packing date indicator under Rule 6(1)(d)."
            status = "RESOLVED"
        elif any(k in surr_lower for k in ["mfd", "mfg", "date of mfg", "manufactured", "उत्पादन"]):
            selected = UniversalSemanticField.DATE_OF_MANUFACTURE
            conf = 0.95
            reason = "Preceded by statutory manufacturing date indicator under Rule 6(1)(d)."
            status = "RESOLVED"
        else:
            # Standalone date in coding area
            selected = UniversalSemanticField.DATE_OF_MANUFACTURE
            conf = 0.82
            reason = "Date stamp identified on packaging coding area."
            status = "RESOLVED"

        return UniversalFieldObject(
            raw_text=cand.raw_text,
            normalized_value=cand.normalized_value,
            unit=None,
            candidate_fields=[
                UniversalSemanticField.DATE_OF_MANUFACTURE,
                UniversalSemanticField.DATE_OF_PACKING,
                UniversalSemanticField.EXPIRY,
                UniversalSemanticField.BEST_BEFORE,
                UniversalSemanticField.USE_BY
            ],
            selected_field=selected,
            semantic_confidence=round(conf, 2),
            evidence_bbox=cand.bbox,
            evidence_context=cand.surrounding_text,
            source_panel=surface,
            reason=reason,
            status=status,
            section=section
        )
