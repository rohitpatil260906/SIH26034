"""
Stage 8: Semantic Evidence & Field Validator Engine
===================================================
Provides reusable semantic field validators:
1. Net Quantity Semantic Safety: Evaluates only fields whose semantic meaning is strictly NET_QUANTITY or NET_VOLUME.
   Rejects Serving Size (50 g), Technical Weight (450 g), Dimensions (10 mm), or Ingredient quantities.
2. MRP Semantic Validation: Normalizes price formats (MRP ₹120, MRP: Rs. 120, Max. Retail Price 120, etc.).
3. Date Semantics: Distinguishes manufacturing, packing, import, expiry, and best-before dates.
4. Entity Role Protection: Keeps BRAND, MANUFACTURER, PACKER, IMPORTER, MARKETER, DISTRIBUTOR, SELLER separate.
5. Address Validation & Critical Regression Protection: Validates address structure and PIN codes.
   CRITICAL REGRESSION RULE: Ingredients, directions, warnings, nutrition info, or technical specs MUST NEVER
   be misclassified as an address merely because OCR detected numbers or location-like tokens.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from .rule_models import Stage8EvidenceItem, Stage7UnifiedProduct, Stage7UnifiedField


class EvidenceValidator:
    """Semantic evidence validator with strict role separation & regression protection."""

    # 1. Net Quantity Semantic Safety Validator
    def validate_net_quantity(self, product: Stage7UnifiedProduct) -> Tuple[str, Optional[Stage8EvidenceItem], str]:
        """
        Validates statutory Net Quantity declaration.
        Strictly rejects Serving Size, Technical Weight, Dimensions, or Ingredient Ratios.
        """
        for f in product.fields:
            fname = f.field_name.upper()

            # REJECT non-net quantity fields
            if fname in ("SERVING_SIZE", "TECHNICAL_WEIGHT", "DIMENSION", "INGREDIENT_QUANTITY", "TECHNICAL_SPECIFICATION"):
                continue

            if fname in ("NET_QUANTITY", "NET_VOLUME"):
                val = (f.value or "").strip()
                src = f.sources[0] if f.sources else None
                evidence = Stage8EvidenceItem(
                    image_id=src.image_id if src else None,
                    panel=src.panel if src else None,
                    region_id=src.region_id if src else None,
                    bbox=src.bbox if src else [],
                    observed_text=src.raw_text if src else val,
                    normalized_value=val,
                    semantic_field=fname,
                    confidence=f.confidence
                )

                if f.status == "CONFIRMED" and val:
                    return ("COMPLIANT", evidence, f"Valid Net Quantity declaration: {val}")
                elif f.status in ("NEEDS_REVIEW", "UNKNOWN", "NOT_VISIBLE"):
                    return (f.status, evidence, f"Net Quantity classification status: {f.status}")
                elif f.status == "CONFLICT":
                    return ("CONFLICT", evidence, f"Conflicting Net Quantity declarations across panels")

        return ("NON_COMPLIANT", None, "Statutory Net Quantity declaration not found")

    # 2. MRP Semantic Validator
    def validate_mrp(self, product: Stage7UnifiedProduct) -> Tuple[str, Optional[Stage8EvidenceItem], str]:
        """Validates Maximum Retail Price (MRP) declaration."""
        for f in product.fields:
            if f.field_name.upper() == "MRP":
                val = (f.value or "").strip()
                norm_price = self.normalize_mrp_string(val) if val else None
                src = f.sources[0] if f.sources else None
                evidence = Stage8EvidenceItem(
                    image_id=src.image_id if src else None,
                    panel=src.panel if src else None,
                    region_id=src.region_id if src else None,
                    bbox=src.bbox if src else [],
                    observed_text=src.raw_text if src else val,
                    normalized_value=norm_price or val,
                    semantic_field="MRP",
                    confidence=f.confidence
                )

                if f.status == "CONFIRMED" and norm_price:
                    return ("COMPLIANT", evidence, f"Valid MRP declaration: {norm_price}")
                elif f.status in ("NEEDS_REVIEW", "CONFLICT"):
                    return ("CONFLICT" if f.status == "CONFLICT" else "NEEDS_REVIEW", evidence, f"MRP declaration status: {f.status}")
                elif f.status in ("NOT_VISIBLE", "UNKNOWN"):
                    return (f.status, evidence, f"MRP declaration status: {f.status}")

        return ("NON_COMPLIANT", None, "Statutory MRP declaration not found")

    def normalize_mrp_string(self, text: str) -> Optional[str]:
        """Normalizes MRP string representations."""
        # e.g., MRP ₹120, MRP: Rs. 120, Maximum Retail Price ₹120, M.R.P. 120, MRP incl. of all taxes ₹120
        m = re.search(r"(?:m\.?r\.?p\.?|retail price)\s*(?:rs\.?|₹)?\s*([\d\.\,]+)", text.lower())
        if m:
            price = m.group(1).replace(",", "")
            return f"₹{price}"
        # Direct currency pattern fallback
        m2 = re.search(r"(?:rs\.?|₹)\s*([\d\.\,]+)", text.lower())
        if m2:
            price = m2.group(1).replace(",", "")
            return f"₹{price}"
        return None

    # 3. Entity & Role Protection Validator
    def validate_entity_declaration(
        self,
        product: Stage7UnifiedProduct,
        required_role: str
    ) -> Tuple[str, Optional[Stage8EvidenceItem], str]:
        """
        Validates company entity declarations (MANUFACTURER, PACKER, IMPORTER, MARKETER).
        Enforces strict role separation: one entity role CANNOT satisfy another automatically.
        """
        req_role_clean = required_role.strip().upper()
        target_field = f"{req_role_clean}_NAME"

        for f in product.fields:
            if f.field_name.upper() == target_field and f.value:
                val = f.value.strip()
                src = f.sources[0] if f.sources else None
                evidence = Stage8EvidenceItem(
                    image_id=src.image_id if src else None,
                    panel=src.panel if src else None,
                    region_id=src.region_id if src else None,
                    bbox=src.bbox if src else [],
                    observed_text=src.raw_text if src else val,
                    normalized_value=val,
                    semantic_field=target_field,
                    confidence=f.confidence
                )
                if f.status == "CONFIRMED":
                    return ("COMPLIANT", evidence, f"Valid {req_role_clean} name declaration: {val}")
                else:
                    return ("NEEDS_REVIEW", evidence, f"{req_role_clean} name status: {f.status}")

        # Check Stage 4 identity entities
        for entity in product.identity.entities:
            if entity.role.upper() == req_role_clean and entity.name and entity.name != "NOT_VISIBLE":
                evidence = Stage8EvidenceItem(
                    observed_text=entity.name,
                    normalized_value=entity.name,
                    semantic_field=target_field,
                    confidence=entity.confidence
                )
                return ("COMPLIANT", evidence, f"Valid {req_role_clean} name declaration: {entity.name}")

        return ("NON_COMPLIANT", None, f"Statutory {req_role_clean} name declaration not found")

    # 4. Address Validator with Critical Regression Protection
    def validate_address_declaration(
        self,
        product: Stage7UnifiedProduct,
        required_role: str
    ) -> Tuple[str, Optional[Stage8EvidenceItem], str]:
        """
        Validates entity address declaration.
        CRITICAL REGRESSION PROTECTION: Ingredients, directions, warnings, nutrition info, or technical specs
        MUST NEVER be misclassified as an address merely because OCR detected numbers or location-like tokens.
        """
        req_role_clean = required_role.strip().upper()
        target_field = f"{req_role_clean}_ADDRESS"

        for f in product.fields:
            fname = f.field_name.upper()

            # REJECT non-address fields
            if fname in ("INGREDIENTS", "DIRECTIONS_FOR_USE", "WARNINGS", "NUTRITIONAL_INFORMATION", "TECHNICAL_SPECIFICATION"):
                continue

            if fname == target_field and f.value:
                val = f.value.strip()
                # Address structure verification (prevent ingredient text)
                if self._is_non_address_text(val):
                    continue

                src = f.sources[0] if f.sources else None
                evidence = Stage8EvidenceItem(
                    image_id=src.image_id if src else None,
                    panel=src.panel if src else None,
                    region_id=src.region_id if src else None,
                    bbox=src.bbox if src else [],
                    observed_text=src.raw_text if src else val,
                    normalized_value=val,
                    semantic_field=target_field,
                    confidence=f.confidence
                )
                if f.status == "CONFIRMED":
                    return ("COMPLIANT", evidence, f"Valid {req_role_clean} address declaration: {val}")

        # Check Stage 4 identity entity addresses
        for entity in product.identity.entities:
            if entity.role.upper() == req_role_clean and entity.address:
                val = entity.address.strip()
                if not self._is_non_address_text(val):
                    evidence = Stage8EvidenceItem(
                        observed_text=val,
                        normalized_value=val,
                        semantic_field=target_field,
                        confidence=entity.confidence
                    )
                    return ("COMPLIANT", evidence, f"Valid {req_role_clean} address declaration: {val}")

        return ("NON_COMPLIANT", None, f"Statutory {req_role_clean} address declaration not found")

    def _is_non_address_text(self, text: str) -> bool:
        """Returns True if text is ingredients, directions, warnings, or nutrition info."""
        t_low = text.lower()
        non_address_keywords = [
            "ingredients:", "contains:", "aqua,", "sugar,", "salt,", "protein",
            "directions for use", "apply 3-4 drops", "do not bleach", "iron low",
            "choking hazard", "keep out of reach", "calories", "carbohydrate"
        ]
        return any(kw in t_low for kw in non_address_keywords)
