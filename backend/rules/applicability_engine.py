"""
Stage 8: Rule Applicability Engine
==================================
Determines rule applicability for a product before compliance evaluation:
- Evaluates Product Category, Package Type (retail vs wholesale/institutional).
- Evaluates Package Net Quantity thresholds (e.g. Rule 26 small package exemption <= 10g / 10ml).
- Evaluates Imported vs Domestic commodity status (e.g. Country of Origin requirements).
- Returns APPLICABLE, NOT_APPLICABLE, UNKNOWN, or NEEDS_REVIEW.
- Never evaluates rules blindly against irrelevant categories.
"""

from typing import List, Dict, Any, Optional, Tuple
from .rule_models import (
    Stage8RuleDefinition,
    Stage8ApplicabilityResult,
    Stage7UnifiedProduct
)


class ApplicabilityEngine:
    """Evaluates rule applicability against product identity & category context."""

    def evaluate_applicability(
        self,
        rule: Stage8RuleDefinition,
        product: Stage7UnifiedProduct,
        rule_context: Optional[Dict[str, Any]] = None
    ) -> Stage8ApplicabilityResult:
        """Determines whether a legal rule applies to a specific product."""
        rule_context = rule_context or {}
        conditions_evaluated: List[str] = []

        # 1. Product Category Matching
        prod_cat = (product.category_profile.category or "UNKNOWN").upper()
        cat_status = getattr(product.category_profile, "category_status", "CONFIRMED")

        if prod_cat in ("UNKNOWN", "UNRESOLVED") or cat_status == "NEEDS_REVIEW":
            return Stage8ApplicabilityResult(
                rule_id=rule.rule_id,
                applicability_status="NEEDS_REVIEW",
                reason="Product category UNKNOWN or NEEDS_REVIEW; category applicability cannot be determined automatically",
                conditions_evaluated=["Unknown category safety check"]
            )

        if "ALL" not in [c.upper() for c in rule.applicable_product_categories]:
            if prod_cat not in [c.upper() for c in rule.applicable_product_categories]:
                return Stage8ApplicabilityResult(
                    rule_id=rule.rule_id,
                    applicability_status="NOT_APPLICABLE",
                    reason=f"Rule category {rule.applicable_product_categories} does not match product category {prod_cat}",
                    conditions_evaluated=["Category mismatch"]
                )
        conditions_evaluated.append(f"Category match: {prod_cat}")

        # 2. Market Context (Retail / Wholesale / Institutional)
        market_ctx = (rule_context.get("market_context") or "RETAIL").upper()
        if rule.applicable_market_context.upper() not in ("ALL", market_ctx):
            return Stage8ApplicabilityResult(
                rule_id=rule.rule_id,
                applicability_status="NOT_APPLICABLE",
                reason=f"Rule context {rule.applicable_market_context} does not match product market context {market_ctx}",
                conditions_evaluated=["Market context mismatch"]
            )

        # 3. Small Package Exemption Check (Rule 26 exemption for <= 10g / 10ml)
        net_qty_str = self._extract_field_val(product, "NET_QUANTITY") or self._extract_field_val(product, "NET_VOLUME")
        if net_qty_str:
            val_num, unit = self._parse_qty_unit(net_qty_str)
            if val_num is not None and val_num <= 10.0 and unit in ("g", "ml"):
                if rule.rule_id in ("RULE_06_NET_QUANTITY", "RULE_06_MRP", "RULE_06_DATE"):
                    return Stage8ApplicabilityResult(
                        rule_id=rule.rule_id,
                        applicability_status="NOT_APPLICABLE",
                        reason=f"Small package exemption under Rule 26 (Net qty {val_num} {unit} <= 10g/ml)",
                        conditions_evaluated=["Rule 26 small package exemption"]
                    )

        # 4. Imported Product Requirement Check
        is_imported = rule_context.get("imported", False)
        if "IMPORTER" in rule.requirement_type or "COUNTRY_OF_ORIGIN" in rule.required_fields:
            if not is_imported and not self._has_imported_signals(product):
                return Stage8ApplicabilityResult(
                    rule_id=rule.rule_id,
                    applicability_status="NOT_APPLICABLE",
                    reason="Country of Origin / Importer rules apply only to imported commodities",
                    conditions_evaluated=["Domestic product, importer rule not applicable"]
                )
            conditions_evaluated.append("Imported product rule applicable")

        # 5. Ambiguous Context Safety
        if prod_cat == "UNKNOWN" and "ALL" not in rule.applicable_product_categories:
            return Stage8ApplicabilityResult(
                rule_id=rule.rule_id,
                applicability_status="NEEDS_REVIEW",
                reason="Product category UNKNOWN; applicability cannot be determined automatically",
                conditions_evaluated=["Unknown category safety check"]
            )

        return Stage8ApplicabilityResult(
            rule_id=rule.rule_id,
            applicability_status="APPLICABLE",
            reason="Rule is statutory and applicable to product profile",
            conditions_evaluated=conditions_evaluated
        )

    def _extract_field_val(self, product: Stage7UnifiedProduct, fname: str) -> Optional[str]:
        for f in product.fields:
            if f.field_name == fname and f.value:
                return f.value
        return None

    def _parse_qty_unit(self, text: str) -> Tuple[Optional[float], str]:
        import re
        m = re.search(r"([\d\.]+)\s*(g|kg|ml|l|ltr|mg)", text.lower())
        if m:
            val = float(m.group(1))
            unit = m.group(2)
            if unit == "kg":
                val *= 1000
                unit = "g"
            elif unit in ("l", "ltr"):
                val *= 1000
                unit = "ml"
            return val, unit
        return None, ""

    def _has_imported_signals(self, product: Stage7UnifiedProduct) -> bool:
        if product.identity.country_of_origin:
            return True
        for f in product.fields:
            if f.field_name in ("IMPORTER_NAME", "IMPORTER_ADDRESS", "COUNTRY_OF_ORIGIN") and f.value:
                return True
        return False
