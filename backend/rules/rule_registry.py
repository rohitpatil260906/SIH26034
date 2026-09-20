"""
Stage 8: Legal Metrology Rule Registry & Versioning Engine
===========================================================
Manages structured statutory rules for Indian Legal Metrology:
- Act: Legal Metrology Act, 2009 (Act 1 of 2010).
- Rules: Legal Metrology (Packaged Commodities) Rules, 2011 (as amended).
- Verification Gating: ONLY rules with verification_status = "VERIFIED" automatically participate in compliance evaluation.
- Rule Versioning: Matches effective_from and effective_until date context.
- Zero Fabrication: Rejects non-existent or unverified rule numbers.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .rule_models import Stage8RuleDefinition


class RuleRegistry:
    """Registry for statutory Legal Metrology rules with verification gating & versioning."""

    def __init__(self):
        self._rules: Dict[str, Stage8RuleDefinition] = {}

    def register_rule(self, rule: Stage8RuleDefinition) -> None:
        """Registers a rule definition in the registry."""
        self._rules[rule.rule_id] = rule
        alias = self._get_alias_for_rule(rule.rule_id)
        if alias and alias != rule.rule_id:
            self._rules[alias] = rule

    def _get_alias_for_rule(self, rule_id: str) -> Optional[str]:
        mapping = {
            "RULE_06_1_A": "RULE_06_NAME_ADDRESS",
            "RULE_06_1_B": "RULE_06_PRODUCT_NAME",
            "RULE_06_1_C": "RULE_06_NET_QUANTITY",
            "RULE_06_1_D": "RULE_06_DATE",
            "RULE_06_1_E": "RULE_06_MRP",
            "RULE_06_1_F": "RULE_06_CONSUMER_CARE",
            "RULE_06_1_EA": "RULE_06_COUNTRY_ORIGIN",
            "RULE_06_1_G": "RULE_06_BATCH"
        }
        return mapping.get(rule_id.upper())

    def get_rule_by_id(self, rule_id: str) -> Optional[Stage8RuleDefinition]:
        """Retrieves a rule by exact rule_id."""
        return self._rules.get(rule_id)

    def get_rule_by_number(self, rule_number: str) -> Optional[Stage8RuleDefinition]:
        """Retrieves a rule by rule_number (e.g. 'RULE 6' or 'Rule 6(1)(a)')."""
        norm_num = rule_number.strip().upper()
        for rule in self._rules.values():
            if rule.rule_number.strip().upper() == norm_num or (rule.sub_rule and rule.sub_rule.strip().upper() == norm_num):
                return rule
        return None

    def get_verified_rules(
        self,
        category: str = "ALL",
        target_date: Optional[str] = None
    ) -> List[Stage8RuleDefinition]:
        """
        Returns all VERIFIED rules applicable to a category and effective date.
        Unverified or superseded rules are excluded from automatic evaluation.
        """
        verified_map: Dict[str, Stage8RuleDefinition] = {}
        date_obj = datetime.strptime(target_date, "%Y-%m-%d") if target_date else datetime.now()

        for r_id, rule in self._rules.items():
            if rule.verification_status != "VERIFIED":
                continue

            if "ALL" not in rule.applicable_product_categories and category.upper() not in [c.upper() for c in rule.applicable_product_categories]:
                continue

            if rule.effective_from:
                eff_from = datetime.strptime(rule.effective_from, "%Y-%m-%d")
                if date_obj < eff_from:
                    continue
            if rule.effective_until:
                eff_until = datetime.strptime(rule.effective_until, "%Y-%m-%d")
                if date_obj > eff_until:
                    continue

            verified_map[rule.rule_id] = rule

        return list(verified_map.values())

    def get_applicable_rules(
        self,
        category: str = "ALL",
        target_date: Optional[str] = None
    ) -> List[Stage8RuleDefinition]:
        """
        Returns all rules (verified and unverified) applicable to a category and date.
        Unverified rules will be gated by RuleEvaluator to flag NEEDS_REVIEW.
        """
        rules_map: Dict[str, Stage8RuleDefinition] = {}
        date_obj = datetime.strptime(target_date, "%Y-%m-%d") if target_date else datetime.now()

        for r_id, rule in self._rules.items():
            if "ALL" not in rule.applicable_product_categories and category.upper() not in [c.upper() for c in rule.applicable_product_categories]:
                continue

            if rule.effective_from:
                eff_from = datetime.strptime(rule.effective_from, "%Y-%m-%d")
                if date_obj < eff_from:
                    continue
            if rule.effective_until:
                eff_until = datetime.strptime(rule.effective_until, "%Y-%m-%d")
                if date_obj > eff_until:
                    continue

            rules_map[rule.rule_id] = rule

        return list(rules_map.values())

    def list_all_rules(self) -> List[Stage8RuleDefinition]:
        """Returns list of all registered rules regardless of verification status."""
        unique_map = {rule.rule_id: rule for rule in self._rules.values()}
        return list(unique_map.values())
