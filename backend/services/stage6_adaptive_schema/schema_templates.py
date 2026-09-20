"""
Stage 6: Product Category Adaptive Schema Templates
===================================================
Defines domain-specific schema definitions and expected field lists per primary product category.
"""

from typing import List, Dict, Any, Set

UNIVERSAL_CORE_FIELDS: List[str] = [
    "PRODUCT_NAME",
    "BRAND",
    "PRODUCT_VARIANT",
    "CATEGORY",
    "SUBCATEGORY",
    "MANUFACTURER",
    "MANUFACTURER_ADDRESS",
    "PACKER",
    "PACKER_ADDRESS",
    "MARKETER",
    "MARKETER_ADDRESS",
    "IMPORTER",
    "IMPORTER_ADDRESS",
    "DISTRIBUTOR",
    "DISTRIBUTOR_ADDRESS",
    "COUNTRY_OF_ORIGIN",
    "MRP",
    "NET_QUANTITY",
    "NET_VOLUME",
    "BATCH_NUMBER",
    "LOT_NUMBER",
    "SERIAL_NUMBER",
    "MODEL_NUMBER",
    "SKU",
    "ARTICLE_NUMBER",
    "MANUFACTURING_DATE",
    "PACKING_DATE",
    "IMPORT_DATE",
    "EXPIRY_DATE",
    "USE_BY_DATE",
    "BEST_BEFORE",
    "CONSUMER_CARE"
]

CATEGORY_SCHEMA_TEMPLATES: Dict[str, List[str]] = {
    "FOOD": [
        "INGREDIENTS",
        "COMPOSITION",
        "NUTRITIONAL_INFORMATION",
        "SERVING_SIZE",
        "VEGETARIAN_DECLARATION",
        "ALLERGEN_INFORMATION",
        "STORAGE_INSTRUCTIONS",
        "DIRECTIONS_FOR_USE",
        "WARNINGS",
        "FSSAI_LICENSE"
    ],
    "BEVERAGE": [
        "FLAVOUR",
        "INGREDIENTS",
        "NUTRITIONAL_INFORMATION",
        "NET_VOLUME",
        "STORAGE_INSTRUCTIONS",
        "WARNINGS",
        "FSSAI_LICENSE"
    ],
    "COSMETIC": [
        "INGREDIENTS",
        "KEY_INGREDIENTS",
        "DIRECTIONS_FOR_USE",
        "WARNINGS",
        "PRECAUTIONS",
        "PERIOD_AFTER_OPENING",
        "MANUFACTURING_LICENCE",
        "STORAGE_INSTRUCTIONS"
    ],
    "PERSONAL_CARE": [
        "INGREDIENTS",
        "DIRECTIONS_FOR_USE",
        "WARNINGS",
        "PRECAUTIONS",
        "PERIOD_AFTER_OPENING"
    ],
    "HOUSEHOLD_CLEANING": [
        "COMPOSITION",
        "INGREDIENTS",
        "DIRECTIONS_FOR_USE",
        "WARNINGS",
        "PRECAUTIONS",
        "STORAGE_INSTRUCTIONS"
    ],
    "ELECTRONICS": [
        "MODEL_NUMBER",
        "SERIAL_NUMBER",
        "TECHNICAL_SPECIFICATION",
        "VOLTAGE",
        "CURRENT",
        "POWER",
        "FREQUENCY",
        "BATTERY_CAPACITY",
        "TECHNICAL_WEIGHT",
        "DIMENSION",
        "WARRANTY_INFORMATION",
        "CERTIFICATION"
    ],
    "ELECTRICAL": [
        "MODEL_NUMBER",
        "TECHNICAL_SPECIFICATION",
        "VOLTAGE",
        "CURRENT",
        "POWER",
        "FREQUENCY",
        "TECHNICAL_WEIGHT",
        "DIMENSION",
        "CERTIFICATION"
    ],
    "TEXTILE": [
        "FABRIC_COMPOSITION",
        "MATERIAL",
        "DIMENSION",
        "CARE_INSTRUCTIONS",
        "STYLE_NUMBER",
        "ARTICLE_NUMBER"
    ],
    "GARMENT": [
        "GARMENT_SIZE",
        "FABRIC_COMPOSITION",
        "CARE_INSTRUCTIONS",
        "STYLE_NUMBER",
        "ARTICLE_NUMBER"
    ],
    "FOOTWEAR": [
        "FOOTWEAR_SIZE",
        "UPPER_MATERIAL",
        "SOLE_MATERIAL",
        "MATERIAL",
        "CARE_INSTRUCTIONS",
        "ARTICLE_NUMBER"
    ],
    "TOYS": [
        "AGE_RANGE",
        "CHOKING_WARNING",
        "SAFETY_INSTRUCTIONS",
        "MODEL_NUMBER",
        "BIS_CERTIFICATION"
    ],
    "STATIONERY": [
        "PAGES_COUNT",
        "PAPER_GSM",
        "DIMENSION",
        "ITEM_COUNT",
        "ARTICLE_NUMBER"
    ],
    "HARDWARE": [
        "TECHNICAL_SPECIFICATION",
        "DIMENSION",
        "PART_NUMBER",
        "MATERIAL"
    ],
    "TOOLS": [
        "TECHNICAL_SPECIFICATION",
        "MODEL_NUMBER",
        "PART_NUMBER",
        "MATERIAL"
    ],
    "AGRICULTURAL": [
        "COMPOSITION",
        "LICENSE_NUMBER",
        "DIRECTIONS_FOR_USE",
        "WARNINGS"
    ]
}


def get_template_fields_for_category(category: str) -> List[str]:
    """Returns category-specific field list combined with universal core fields."""
    cat_u = category.upper().strip()
    specific = CATEGORY_SCHEMA_TEMPLATES.get(cat_u, [])
    # Return unique combined list preserving order
    combined = list(dict.fromkeys(UNIVERSAL_CORE_FIELDS + specific))
    return combined
