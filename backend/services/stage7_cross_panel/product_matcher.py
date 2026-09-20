"""
Stage 7: Same-Product Matching Engine
=====================================
Determines whether two images/panels represent the SAME physical product.

Multi-signal matching:
- Brand, Product Name, Variant, Category
- Model Number, SKU, Article Number, Product Code
- Manufacturer, Packer, Marketer, Importer
- Net Quantity / Pack Size (distinguishes product family vs specific pack size)
- Batch/Lot numbers (treated as supporting evidence; different batch numbers do NOT break match)
- Serial Numbers (instance-specific; different serial numbers do NOT break product model match)
- Visual/geometry similarity (supporting evidence)

Output:
- same_product_confidence (0.0 to 1.0)
- status: MATCHED, POSSIBLE_MATCH, NOT_MATCHED, NEEDS_REVIEW
"""

from typing import List, Dict, Any, Optional, Tuple
from ...models import (
    Stage4ProductIdentity,
    Stage6ProductProfile,
    Stage7ProductMatchEvidence
)


def _clean_str(val: Optional[Any]) -> str:
    if not val:
        return ""
    if hasattr(val, "value"):
        v = str(val.value or "")
    else:
        v = str(val or "")
    v_clean = v.strip().lower()
    return "" if v_clean in ("not_visible", "unknown", "none", "") else v_clean


class ProductMatcher:
    """Multi-signal product identity matcher."""

    def evaluate_match(
        self,
        image_a: str,
        identity_a: Optional[Stage4ProductIdentity],
        profile_a: Optional[Stage6ProductProfile],
        image_b: str,
        identity_b: Optional[Stage4ProductIdentity],
        profile_b: Optional[Stage6ProductProfile],
        extra_signals_a: Optional[Dict[str, Any]] = None,
        extra_signals_b: Optional[Dict[str, Any]] = None
    ) -> Stage7ProductMatchEvidence:
        """Evaluates same-product confidence between two image/panel observations."""

        evidence: List[str] = []
        score = 0.0
        penalty = 0.0

        if not identity_a or not identity_b:
            return Stage7ProductMatchEvidence(
                image_a=image_a,
                image_b=image_b,
                same_product_confidence=0.0,
                status="NOT_MATCHED",
                evidence=["Missing identity data on one or both images"]
            )

        brand_a = _clean_str(identity_a.brand)
        brand_b = _clean_str(identity_b.brand)

        name_a = _clean_str(identity_a.product_name)
        name_b = _clean_str(identity_b.product_name)

        var_a = _clean_str(identity_a.variant)
        var_b = _clean_str(identity_b.variant)

        cat_a = _clean_str(profile_a.category if profile_a else identity_a.category)
        cat_b = _clean_str(profile_b.category if profile_b else identity_b.category)

        model_a = _clean_str(identity_a.model_number)
        model_b = _clean_str(identity_b.model_number)

        sku_a = _clean_str(identity_a.sku or identity_a.article_number or identity_a.barcode_value)
        sku_b = _clean_str(identity_b.sku or identity_b.article_number or identity_b.barcode_value)

        batch_a = _clean_str(identity_a.batch_number or identity_a.lot_number)
        batch_b = _clean_str(identity_b.batch_number or identity_b.lot_number)

        mfg_a = _extract_entity_name(identity_a, ["MANUFACTURER", "PACKER", "MARKETER"])
        mfg_b = _extract_entity_name(identity_b, ["MANUFACTURER", "PACKER", "MARKETER"])

        net_q_a = _clean_str((extra_signals_a or {}).get("NET_QUANTITY") or (extra_signals_a or {}).get("NET_VOLUME"))
        net_q_b = _clean_str((extra_signals_b or {}).get("NET_QUANTITY") or (extra_signals_b or {}).get("NET_VOLUME"))

        # 1. Strong Key Matching (Model / SKU / Product Code)
        if model_a and model_b:
            if model_a == model_b:
                score += 0.55
                evidence.append(f"Identical Model Number: {model_a}")
            else:
                penalty += 0.35
                evidence.append(f"Conflicting Model Numbers: {model_a} vs {model_b}")

        if sku_a and sku_b:
            if sku_a == sku_b:
                score += 0.50
                evidence.append(f"Identical SKU/Barcode/Article: {sku_a}")
            else:
                penalty += 0.30
                evidence.append(f"Conflicting SKU/Barcode: {sku_a} vs {sku_b}")

        # 2. Category Match / Conflict
        if cat_a and cat_b:
            if cat_a == cat_b:
                score += 0.15
                evidence.append(f"Matching Category: {cat_a}")
            else:
                penalty += 0.50
                evidence.append(f"Conflicting Categories: {cat_a} vs {cat_b}")

        # 3. Brand Match / Conflict
        if brand_a and brand_b:
            if brand_a == brand_b:
                score += 0.30
                evidence.append(f"Matching Brand: {brand_a}")
            else:
                penalty += 0.45
                evidence.append(f"Conflicting Brands: {brand_a} vs {brand_b}")

        # 4. Product Name Match / Conflict
        if name_a and name_b:
            if name_a == name_b or name_a in name_b or name_b in name_a:
                score += 0.35
                evidence.append(f"Matching Product Name: {name_a}")
            else:
                penalty += 0.40
                evidence.append(f"Conflicting Product Names: {name_a} vs {name_b}")

        # 5. Variant Check (e.g. Orange Flavour vs Lemon Flavour)
        if var_a and var_b:
            if var_a == var_b:
                score += 0.15
                evidence.append(f"Matching Variant: {var_a}")
            else:
                penalty += 0.35
                evidence.append(f"Conflicting Variants: {var_a} vs {var_b}")

        # 6. Company / Manufacturer Match
        if mfg_a and mfg_b:
            if mfg_a == mfg_b or mfg_a in mfg_b or mfg_b in mfg_a:
                score += 0.15
                evidence.append(f"Matching Manufacturer/Packer: {mfg_a}")

        # 7. Pack Size / Net Qty Differentiation (e.g. 500g vs 1kg)
        if net_q_a and net_q_b:
            if net_q_a == net_q_b:
                score += 0.10
                evidence.append(f"Matching Net Quantity/Pack Size: {net_q_a}")
            else:
                penalty += 0.35
                evidence.append(f"Conflicting Pack Sizes: {net_q_a} vs {net_q_b}")

        # 8. Batch Number (Supporting evidence, NOT absolute key)
        if batch_a and batch_b:
            if batch_a == batch_b:
                score += 0.05
                evidence.append(f"Matching Batch Number: {batch_a}")
            else:
                # Note: Different batch numbers on same product type are legitimate, do NOT penalize
                evidence.append(f"Different Batch Numbers (same product type): {batch_a} vs {batch_b}")

        # Compute final confidence
        final_conf = max(0.0, min(1.0, score - penalty))

        # Status threshold determination
        if final_conf >= 0.70:
            status = "MATCHED"
        elif final_conf >= 0.45:
            status = "NEEDS_REVIEW"
        else:
            status = "NOT_MATCHED"

        return Stage7ProductMatchEvidence(
            image_a=image_a,
            image_b=image_b,
            same_product_confidence=round(final_conf, 2),
            status=status,
            evidence=evidence
        )


def _extract_entity_name(identity: Stage4ProductIdentity, roles: List[str]) -> str:
    for entity in identity.entities:
        if entity.role.upper() in roles and entity.name:
            c = entity.name.strip().lower()
            if c and c != "not_visible":
                return c
    return ""
