"""
Stage 8: Statutory Rule Loader
==============================
Loads statutory Legal Metrology rules from backend/data/rules_library_v2024.json
and populates the RuleRegistry with verified metadata schemas.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from .rule_models import Stage8RuleDefinition
from .rule_registry import RuleRegistry

logger = logging.getLogger(__name__)


def load_statutory_rules(registry: RuleRegistry, json_path: Optional[str] = None) -> int:
    """Loads statutory rules from JSON file into registry."""
    if not json_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "rules_library_v2024.json")

    if not os.path.exists(json_path):
        logger.warning(f"Rules library JSON not found at {json_path}. Injecting standard verified rules.")
        _inject_standard_rules(registry)
        return len(registry.list_all_rules())

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rules_list = data.get("rules", [])
        canonical_map = {
            "RULE_06_1_A": "RULE_06_NAME_ADDRESS",
            "RULE_06_1_B": "RULE_06_PRODUCT_NAME",
            "RULE_06_1_C": "RULE_06_NET_QUANTITY",
            "RULE_06_1_D": "RULE_06_DATE",
            "RULE_06_1_E": "RULE_06_MRP",
            "RULE_06_1_F": "RULE_06_CONSUMER_CARE",
            "RULE_06_1_EA": "RULE_06_COUNTRY_ORIGIN",
            "RULE_06_1_G": "RULE_06_BATCH"
        }

        for rdata in rules_list:
            v_stat = rdata.get("verification_status", "MANDATORY").upper()
            if v_stat in ("UNVERIFIED", "DRAFT"):
                v_status = "UNVERIFIED"
            elif v_stat in ("SUPERSEDED", "EXPIRED"):
                v_status = "SUPERSEDED"
            else:
                v_status = "VERIFIED"

            raw_rid = rdata.get("rule_id", "RULE_01").upper()
            rid = canonical_map.get(raw_rid, raw_rid)
            req_fields = _determine_required_fields(rid, rdata.get("rule_title", ""))

            rule = Stage8RuleDefinition(
                rule_id=rid,
                act_name=data.get("statutory_act", "The Legal Metrology Act, 2009"),
                rules_name=data.get("statutory_rules", "Legal Metrology (Packaged Commodities) Rules, 2011"),
                rule_number=rdata.get("rule_no", "RULE 1"),
                sub_rule=rdata.get("sub_rule"),
                clause=rdata.get("clause"),
                title=rdata.get("rule_title", "General Rule"),
                requirement_text=rdata.get("required_declaration") or rdata.get("validation_condition") or "Statutory requirement",
                requirement_type=_determine_requirement_type(rid, rdata.get("rule_title", "")),
                applicable_product_categories=["ALL"],
                applicable_packaging_types=["ALL"],
                applicable_market_context="RETAIL",
                applicability_conditions=[rdata.get("validation_condition")] if rdata.get("validation_condition") else [],
                exceptions=[rdata.get("exception_condition")] if rdata.get("exception_condition") else [],
                required_fields=req_fields,
                effective_from=rdata.get("version_date", "2011-03-07"),
                jurisdiction="INDIA",
                source_name=rdata.get("source", "Gazette of India"),
                source_version=data.get("version", "2024.1"),
                verification_status=v_status,
                notes=rdata.get("penal_provision")
            )
            registry.register_rule(rule)

    except Exception as e:
        logger.error(f"Error loading rules from {json_path}: {e}")
        _inject_standard_rules(registry)

    return len(registry.list_all_rules())


def _determine_required_fields(rule_id: str, title: str) -> List[str]:
    t = title.lower()
    rid = rule_id.upper()
    if "rule_06_name_address" in rid or "rule_06_1_a" in rid or "name and complete address" in t:
        return ["MANUFACTURER_NAME", "MANUFACTURER_ADDRESS"]
    if "rule_06_product_name" in rid or "rule_06_1_b" in rid or "common or generic name" in t:
        return ["PRODUCT_NAME"]
    if "rule_06_net_quantity" in rid or "rule_06_1_c" in rid or "net quantity" in t:
        return ["NET_QUANTITY"]
    if "rule_06_date" in rid or "rule_06_1_d" in rid or "month and year" in t:
        return ["MANUFACTURING_DATE"]
    if "rule_06_mrp" in rid or "rule_06_1_e" in rid or "maximum retail price" in t or "mrp" in t:
        return ["MRP"]
    if "rule_06_consumer_care" in rid or "rule_06_1_f" in rid or "consumer care" in t:
        return ["CONSUMER_CARE"]
    if "country_origin" in rid or "rule_06_1_ea" in rid or "country of origin" in t:
        return ["IMPORTER_NAME", "IMPORTER_ADDRESS", "COUNTRY_OF_ORIGIN"]
    if "batch" in t or "rule_06_1_g" in rid:
        return ["BATCH_NUMBER"]
    return ["PRODUCT_NAME"]


def _determine_requirement_type(rule_id: str, title: str) -> str:
    t = title.lower()
    rid = rule_id.upper()
    if "country_origin" in rid or "rule_06_1_ea" in rid or "country of origin" in t:
        return "IMPORTER"
    if "net_quantity" in rid or "net quantity" in t or "rule_06_1_c" in rid:
        return "NET_QUANTITY"
    if "mrp" in rid or "price" in t or "rule_06_1_e" in rid:
        return "MRP"
    if "consumer_care" in rid or "consumer care" in t or "rule_06_1_f" in rid:
        return "CONSUMER_CARE"
    return "DECLARATION"


def _inject_standard_rules(registry: RuleRegistry) -> None:
    """Fallback standard verified Legal Metrology (Packaged Commodities) Rules 2011."""
    std_rules = [
        Stage8RuleDefinition(
            rule_id="RULE_06_NAME_ADDRESS",
            rule_number="Rule 6(1)(a)",
            sub_rule="6(1)(a)",
            title="Name and address of Manufacturer/Packer/Importer",
            requirement_text="Every package shall bear the name and address of the manufacturer, or packer, or importer.",
            requirement_type="DECLARATION",
            required_fields=["MANUFACTURER_NAME", "MANUFACTURER_ADDRESS"],
            verification_status="VERIFIED"
        ),
        Stage8RuleDefinition(
            rule_id="RULE_06_PRODUCT_NAME",
            rule_number="Rule 6(1)(b)",
            sub_rule="6(1)(b)",
            title="Generic or common name of commodity",
            requirement_text="The name of the commodity contained in the package shall be stated.",
            requirement_type="DECLARATION",
            required_fields=["PRODUCT_NAME"],
            verification_status="VERIFIED"
        ),
        Stage8RuleDefinition(
            rule_id="RULE_06_NET_QUANTITY",
            rule_number="Rule 6(1)(c)",
            sub_rule="6(1)(c)",
            title="Net quantity declaration",
            requirement_text="The net quantity in terms of standard unit of weight or measure or number shall be stated.",
            requirement_type="NET_QUANTITY",
            required_fields=["NET_QUANTITY"],
            verification_status="VERIFIED"
        ),
        Stage8RuleDefinition(
            rule_id="RULE_06_DATE",
            rule_number="Rule 6(1)(d)",
            sub_rule="6(1)(d)",
            title="Month and year of manufacture/packing/import",
            requirement_text="The month and year in which the commodity is manufactured or pre-packed or imported shall be stated.",
            requirement_type="DECLARATION",
            required_fields=["MANUFACTURING_DATE"],
            verification_status="VERIFIED"
        ),
        Stage8RuleDefinition(
            rule_id="RULE_06_MRP",
            rule_number="Rule 6(1)(e)",
            sub_rule="6(1)(e)",
            title="Maximum Retail Price (MRP)",
            requirement_text="The retail sale price of the package shall be stated as 'Maximum or Max. Retail Price Rs./₹... incl. of all taxes'.",
            requirement_type="MRP",
            required_fields=["MRP"],
            verification_status="VERIFIED"
        ),
        Stage8RuleDefinition(
            rule_id="RULE_06_CONSUMER_CARE",
            rule_number="Rule 6(2)",
            sub_rule="6(2)",
            title="Consumer Care contact details",
            requirement_text="Every package shall bear name, address, telephone number, e-mail address of person/office for consumer complaints.",
            requirement_type="CONSUMER_CARE",
            required_fields=["CONSUMER_CARE"],
            verification_status="VERIFIED"
        ),
        Stage8RuleDefinition(
            rule_id="RULE_06_COUNTRY_ORIGIN",
            rule_number="Rule 6(1)(ea)",
            sub_rule="6(1)(ea)",
            title="Country of Origin for imported products",
            requirement_text="Name of the country of origin or manufacture or assembly shall be mentioned on the package.",
            requirement_type="IMPORTER",
            required_fields=["COUNTRY_OF_ORIGIN"],
            verification_status="VERIFIED"
        )
    ]
    for r in std_rules:
        registry.register_rule(r)
