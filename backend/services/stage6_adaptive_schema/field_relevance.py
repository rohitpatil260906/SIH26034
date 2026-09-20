"""
Stage 6: Category Field Relevance Engine
========================================
Calculates the dynamic relevance score (0.0 to 1.0) of each semantic field
based on the identified product category and subcategory.
"""

from typing import Dict, Any, List, Tuple


class FieldRelevanceEngine:
    """Calculates field relevance scores tailored to product category."""

    def __init__(self):
        # Universal Core Fields (High relevance across almost all CPG categories)
        self.universal_core_fields = {
            "PRODUCT_NAME", "BRAND", "PRODUCT_VARIANT", "MANUFACTURER", "MANUFACTURER_ADDRESS",
            "MARKETER", "MARKETER_ADDRESS", "PACKER", "PACKER_ADDRESS", "IMPORTER", "IMPORTER_ADDRESS",
            "COUNTRY_OF_ORIGIN", "MRP", "NET_QUANTITY", "NET_VOLUME", "BATCH_NUMBER",
            "MANUFACTURING_DATE", "EXPIRY_DATE", "BEST_BEFORE", "CONSUMER_CARE"
        }

        # Category-Specific Field Relevance Matrices
        self.category_relevance_matrix: Dict[str, Dict[str, float]] = {
            "FOOD": {
                "INGREDIENTS": 0.98,
                "COMPOSITION": 0.95,
                "NUTRITIONAL_INFORMATION": 0.98,
                "SERVING_SIZE": 0.92,
                "VEGETARIAN_DECLARATION": 0.95,
                "ALLERGEN_INFORMATION": 0.90,
                "STORAGE_INSTRUCTIONS": 0.85,
                "FSSAI_LICENSE": 0.95,
                "MODEL_NUMBER": 0.02,
                "SERIAL_NUMBER": 0.02,
                "TECHNICAL_SPECIFICATION": 0.02,
                "VOLTAGE": 0.0,
                "POWER": 0.0,
                "FABRIC_COMPOSITION": 0.0,
                "GARMENT_SIZE": 0.0,
                "CARE_INSTRUCTIONS": 0.0,
                "AGE_RANGE": 0.0,
                "CHOKING_WARNING": 0.0
            },
            "BEVERAGE": {
                "INGREDIENTS": 0.98,
                "NUTRITIONAL_INFORMATION": 0.98,
                "FLAVOUR": 0.92,
                "NET_VOLUME": 0.98,
                "STORAGE_INSTRUCTIONS": 0.85,
                "FSSAI_LICENSE": 0.95,
                "MODEL_NUMBER": 0.02,
                "VOLTAGE": 0.0,
                "FABRIC_COMPOSITION": 0.0,
                "GARMENT_SIZE": 0.0
            },
            "COSMETIC": {
                "INGREDIENTS": 0.98,
                "KEY_INGREDIENTS": 0.95,
                "DIRECTIONS_FOR_USE": 0.92,
                "WARNINGS": 0.90,
                "PRECAUTIONS": 0.90,
                "PERIOD_AFTER_OPENING": 0.88,
                "MANUFACTURING_LICENCE": 0.92,
                "NUTRITIONAL_INFORMATION": 0.02,
                "MODEL_NUMBER": 0.02,
                "VOLTAGE": 0.0,
                "FABRIC_COMPOSITION": 0.0
            },
            "PERSONAL_CARE": {
                "INGREDIENTS": 0.95,
                "DIRECTIONS_FOR_USE": 0.90,
                "WARNINGS": 0.90,
                "PERIOD_AFTER_OPENING": 0.85,
                "NUTRITIONAL_INFORMATION": 0.02,
                "MODEL_NUMBER": 0.02,
                "VOLTAGE": 0.0
            },
            "HOUSEHOLD_CLEANING": {
                "COMPOSITION": 0.92,
                "INGREDIENTS": 0.90,
                "DIRECTIONS_FOR_USE": 0.95,
                "WARNINGS": 0.95,
                "PRECAUTIONS": 0.95,
                "STORAGE_INSTRUCTIONS": 0.88,
                "NUTRITIONAL_INFORMATION": 0.0,
                "MODEL_NUMBER": 0.02
            },
            "ELECTRONICS": {
                "MODEL_NUMBER": 0.98,
                "SERIAL_NUMBER": 0.95,
                "TECHNICAL_SPECIFICATION": 0.98,
                "VOLTAGE": 0.95,
                "POWER": 0.95,
                "CURRENT": 0.90,
                "FREQUENCY": 0.90,
                "BATTERY_CAPACITY": 0.92,
                "WARRANTY_INFORMATION": 0.90,
                "CERTIFICATION": 0.92,
                "SKU": 0.90,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "SERVING_SIZE": 0.0,
                "FABRIC_COMPOSITION": 0.0,
                "GARMENT_SIZE": 0.0
            },
            "ELECTRICAL": {
                "MODEL_NUMBER": 0.95,
                "TECHNICAL_SPECIFICATION": 0.98,
                "VOLTAGE": 0.98,
                "POWER": 0.98,
                "CURRENT": 0.95,
                "FREQUENCY": 0.92,
                "CERTIFICATION": 0.92,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "FABRIC_COMPOSITION": 0.0
            },
            "TEXTILE": {
                "FABRIC_COMPOSITION": 0.98,
                "MATERIAL": 0.95,
                "DIMENSION": 0.92,
                "CARE_INSTRUCTIONS": 0.95,
                "STYLE_NUMBER": 0.88,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "VOLTAGE": 0.0
            },
            "GARMENT": {
                "GARMENT_SIZE": 0.98,
                "FABRIC_COMPOSITION": 0.98,
                "CARE_INSTRUCTIONS": 0.95,
                "STYLE_NUMBER": 0.90,
                "ARTICLE_NUMBER": 0.88,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "VOLTAGE": 0.0
            },
            "FOOTWEAR": {
                "FOOTWEAR_SIZE": 0.98,
                "UPPER_MATERIAL": 0.95,
                "SOLE_MATERIAL": 0.90,
                "MATERIAL": 0.92,
                "CARE_INSTRUCTIONS": 0.85,
                "ARTICLE_NUMBER": 0.90,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "VOLTAGE": 0.0
            },
            "TOYS": {
                "AGE_RANGE": 0.98,
                "CHOKING_WARNING": 0.98,
                "SAFETY_INSTRUCTIONS": 0.95,
                "MODEL_NUMBER": 0.88,
                "BIS_CERTIFICATION": 0.92,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "VOLTAGE": 0.02
            },
            "STATIONERY": {
                "PAGES_COUNT": 0.90,
                "PAPER_GSM": 0.90,
                "DIMENSION": 0.88,
                "ITEM_COUNT": 0.92,
                "ARTICLE_NUMBER": 0.85,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "VOLTAGE": 0.0
            },
            "HARDWARE": {
                "DIMENSION": 0.92,
                "TECHNICAL_SPECIFICATION": 0.95,
                "PART_NUMBER": 0.90,
                "MATERIAL": 0.90,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0,
                "VOLTAGE": 0.02
            },
            "TOOLS": {
                "TECHNICAL_SPECIFICATION": 0.95,
                "MODEL_NUMBER": 0.92,
                "PART_NUMBER": 0.90,
                "MATERIAL": 0.88,
                "INGREDIENTS": 0.0,
                "NUTRITIONAL_INFORMATION": 0.0
            },
            "AGRICULTURAL": {
                "COMPOSITION": 0.95,
                "BATCH_NUMBER": 0.95,
                "MANUFACTURING_DATE": 0.95,
                "LICENSE_NUMBER": 0.92,
                "DIRECTIONS_FOR_USE": 0.90,
                "WARNINGS": 0.90,
                "NUTRITIONAL_INFORMATION": 0.0
            }
        }

    def get_field_relevance(self, field_name: str, category: str) -> float:
        """Returns relevance score (0.0 to 1.0) for a field under given category."""
        norm_field = field_name.upper().strip()
        cat_u = category.upper().strip()

        # Check category matrix first
        if cat_u in self.category_relevance_matrix:
            if norm_field in self.category_relevance_matrix[cat_u]:
                return self.category_relevance_matrix[cat_u][norm_field]

        # Check universal core fields
        if norm_field in self.universal_core_fields:
            return 0.95

        # Default fallback
        if cat_u in ("UNKNOWN", "OTHER"):
            return 0.50

        return 0.10

    def is_field_applicable(self, field_name: str, category: str) -> bool:
        """Determines if a field is applicable to a given product category."""
        rel = self.get_field_relevance(field_name, category)
        return rel >= 0.15
