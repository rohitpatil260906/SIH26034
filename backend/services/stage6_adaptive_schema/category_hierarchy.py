"""
Stage 6: Product Category Taxonomy & Hierarchy
==============================================
Defines standard primary categories and subcategories for Legal Metrology adaptive schemas.
"""

from typing import List, Dict, Optional, Set

PRIMARY_CATEGORIES: List[str] = [
    "FOOD",
    "BEVERAGE",
    "COSMETIC",
    "PERSONAL_CARE",
    "HOUSEHOLD_CLEANING",
    "ELECTRONICS",
    "ELECTRICAL",
    "TOYS",
    "STATIONERY",
    "TEXTILE",
    "GARMENT",
    "FOOTWEAR",
    "HARDWARE",
    "TOOLS",
    "AGRICULTURAL",
    "PET_PRODUCT",
    "HEALTH_PRODUCT",
    "IMPORTED_PRODUCT",
    "OTHER",
    "UNKNOWN"
]

SUBCATEGORIES: Dict[str, List[str]] = {
    "FOOD": [
        "BISCUITS", "TEA", "SPICES", "FLOUR", "SNACKS", "PACKAGED_FOOD",
        "CONFECTIONERY", "DAIRY", "OIL_EDIBLE", "GRAINS_PULSES"
    ],
    "BEVERAGE": [
        "SOFT_DRINK", "JUICE", "TEA_DRINK", "WATER", "ENERGY_DRINK", "COFFEE"
    ],
    "COSMETIC": [
        "FACE_CARE", "SKIN_CARE", "HAIR_CARE", "MAKEUP", "SOAP", "SERUM", "LOTION", "SUNSCREEN"
    ],
    "PERSONAL_CARE": [
        "ORAL_CARE", "DEODORANT", "SHAVING", "HYGIENE", "BATH"
    ],
    "HOUSEHOLD_CLEANING": [
        "DETERGENT", "CLEANER", "DISINFECTANT", "AIR_FRESHENER", "DISHWASH"
    ],
    "ELECTRONICS": [
        "MOBILE_ACCESSORY", "COMPUTER_ACCESSORY", "AUDIO", "APPLIANCE", "LIGHTING", "GADGET", "CAMERA"
    ],
    "ELECTRICAL": [
        "WIRE_CABLE", "SWITCH", "SOCKET", "BULB", "BATTERY"
    ],
    "TOYS": [
        "ACTION_FIGURE", "PUZZLE", "BOARD_GAME", "EDUCATIONAL", "PLUSH", "OUTDOOR"
    ],
    "STATIONERY": [
        "NOTEBOOK", "PEN_PENCIL", "PAPER", "DESK_ACCESSORY", "ART_SUPPLIES"
    ],
    "TEXTILE": [
        "FABRIC", "BEDDING", "TOWEL", "CURTAIN"
    ],
    "GARMENT": [
        "TSHIRT", "SHIRT", "PANTS", "DRESS", "INNERWEAR", "JACKET"
    ],
    "FOOTWEAR": [
        "SHOES", "SANDALS", "SLIPPERS", "SOCKS"
    ],
    "HARDWARE": [
        "FASTENERS", "LOCKS", "PLUMBING", "FITTINGS"
    ],
    "TOOLS": [
        "HAND_TOOL", "POWER_TOOL", "MEASURING_TOOL"
    ],
    "AGRICULTURAL": [
        "SEEDS", "FERTILIZER", "PESTICIDE", "ANIMAL_FEED"
    ],
    "PET_PRODUCT": [
        "PET_FOOD", "PET_CARE", "PET_ACCESSORY"
    ],
    "HEALTH_PRODUCT": [
        "SUPPLEMENT", "FIRST_AID", "SANITIZER"
    ]
}


def normalize_category_name(cat: str) -> str:
    """Normalizes category name to standard uppercase key."""
    if not cat:
        return "UNKNOWN"
    cat_u = cat.strip().upper().replace(" ", "_").replace("-", "_")
    if cat_u in PRIMARY_CATEGORIES:
        return cat_u
    # Map common synonyms
    synonyms = {
        "FOODS": "FOOD",
        "GROCERY": "FOOD",
        "BEVERAGES": "BEVERAGE",
        "COSMETICS": "COSMETIC",
        "BEAUTY": "COSMETIC",
        "PERSONALCARE": "PERSONAL_CARE",
        "HOUSEHOLD": "HOUSEHOLD_CLEANING",
        "CLEANING": "HOUSEHOLD_CLEANING",
        "ELECTRONIC": "ELECTRONICS",
        "GARMENTS": "GARMENT",
        "CLOTHING": "GARMENT",
        "APPAREL": "GARMENT",
        "FOOT WEAR": "FOOTWEAR",
        "TOY": "TOYS",
        "STATIONARY": "STATIONERY",
        "TOOL": "TOOLS",
        "AGRI": "AGRICULTURAL"
    }
    return synonyms.get(cat_u, "UNKNOWN")


def get_subcategories(category: str) -> List[str]:
    """Returns subcategories for a given primary category."""
    norm_cat = normalize_category_name(category)
    return SUBCATEGORIES.get(norm_cat, [])
