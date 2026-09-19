"""
Stage 4: Product Category Resolver Service
==========================================
Resolves product category using Stage 3 candidates, product names, ingredients, and keywords:
- Categories: FOOD, BEVERAGE, COSMETIC, PERSONAL_CARE, HOUSEHOLD, CLEANING,
  ELECTRONICS, ELECTRICAL, TOYS, STATIONERY, TEXTILE, GARMENT, FOOTWEAR,
  HARDWARE, TOOLS, AGRICULTURAL, PET_PRODUCT, HEALTH_PRODUCT, IMPORTED_PRODUCT, OTHER, UNKNOWN
- If confidence is insufficient (< 0.40): category = UNKNOWN.
- Evidence-based, returns explicit evidence signals.
"""

from typing import Dict, Any, Optional, Tuple, List
from ...models import (
    Stage3CategoryCandidate,
    Stage4CategoryInfo,
    Stage2TextRegion
)


class CategoryResolverService:
    """Resolves commodity category from multimodal signals."""

    CATEGORY_KEYWORDS = {
        "FOOD": ["biscuit", "cookies", "snack", "flour", "atta", "wheat", "rice", "spice", "masala", "salt", "sugar", "chocolate", "bakery", "edible", "cereal", "noodle"],
        "BEVERAGE": ["juice", "drink", "water", "tea", "coffee", "soda", "syrup", "beverage", "squash", "cola"],
        "COSMETIC": ["serum", "lotion", "cream", "lipstick", "mascara", "foundation", "eyeliner", "sunscreen", "cosmetic", "glow", "skin"],
        "PERSONAL_CARE": ["shampoo", "conditioner", "soap", "toothpaste", "toothbrush", "face wash", "body wash", "deodorant", "hair", "perfume"],
        "CLEANING": ["detergent", "disinfectant", "floor cleaner", "toilet cleaner", "dishwash", "bleach", "stain remover"],
        "HOUSEHOLD": ["air freshener", "insecticide", "mosquito", "candle", "matchbox", "foil", "garbage bag"],
        "ELECTRONICS": ["mouse", "keyboard", "adapter", "charger", "cable", "usb", "headphone", "earphone", "bluetooth", "laptop", "battery", "display", "monitor"],
        "ELECTRICAL": ["bulb", "led", "wire", "switch", "socket", "fan", "iron", "heater", "torch"],
        "TEXTILE": ["fabric", "cloth", "yarn", "cotton", "polyester", "wool", "bedsheet", "curtain"],
        "GARMENT": ["shirt", "t-shirt", "trouser", "jeans", "dress", "saree", "kurta", "socks", "apparel", "wear"],
        "FOOTWEAR": ["shoes", "sandals", "slippers", "boots", "sneakers"],
        "STATIONERY": ["notebook", "pen", "pencil", "eraser", "ruler", "folder", "paper", "diary"],
        "TOYS": ["toy", "game", "puzzle", "doll", "action figure", "lego"],
        "HARDWARE": ["screw", "bolt", "nut", "hinge", "lock", "padlock", "nail"],
        "TOOLS": ["hammer", "screwdriver", "wrench", "pliers", "saw", "drill"],
        "AGRICULTURAL": ["seed", "fertilizer", "pesticide", "manure", "growth promoter"],
        "PET_PRODUCT": ["dog food", "cat food", "pet treat", "pet shampoo", "collar", "leash"],
        "HEALTH_PRODUCT": ["vitamin", "supplement", "capsule", "tablet", "ayurvedic", "herbal tonic", "sanitizer", "bandage"],
        "IMPORTED_PRODUCT": ["imported", "country of origin", "customs", "made in china", "made in usa", "made in germany", "made in japan"]
    }

    def resolve_category(
        self,
        s3_candidates: List[Stage3CategoryCandidate],
        product_name: str,
        regions: List[Stage2TextRegion]
    ) -> Stage4CategoryInfo:
        """Resolves the category based on fused signals."""
        scores: Dict[str, float] = {}
        evidence: Dict[str, List[str]] = {}

        # 1. Incorporate Stage 3 candidate scores
        for cand in s3_candidates:
            cat = cand.category.upper()
            scores[cat] = scores.get(cat, 0.0) + cand.confidence * 1.5
            if cat not in evidence:
                evidence[cat] = []
            evidence[cat].extend(cand.evidence_signals)

        # 2. Check product name words
        pn_lower = product_name.lower()
        for cat, kws in self.CATEGORY_KEYWORDS.items():
            for kw in kws:
                if kw in pn_lower:
                    scores[cat] = scores.get(cat, 0.0) + 1.2
                    if cat not in evidence:
                        evidence[cat] = []
                    evidence[cat].append(f"product_name:{kw}")

        # 3. Check all visible text
        all_text = " ".join(r.raw_text.lower() for r in regions)
        for cat, kws in self.CATEGORY_KEYWORDS.items():
            for kw in kws:
                if kw in all_text:
                    scores[cat] = scores.get(cat, 0.0) + 0.4
                    if cat not in evidence:
                        evidence[cat] = []
                    if f"keyword:{kw}" not in evidence[cat]:
                        evidence[cat].append(f"keyword:{kw}")

        if not scores:
            return Stage4CategoryInfo(value="UNKNOWN", confidence=0.0, evidence_signals=[])

        # Find category with highest score
        best_cat = max(scores, key=scores.get)
        raw_score = scores[best_cat]
        # Normalize confidence to 0.0 - 0.99
        conf = min(0.98, raw_score / (raw_score + 1.0))

        if conf < 0.40:
            return Stage4CategoryInfo(value="UNKNOWN", confidence=conf, evidence_signals=[])

        return Stage4CategoryInfo(
            value=best_cat,
            confidence=round(conf, 2),
            evidence_signals=list(set(evidence.get(best_cat, [])))[:5]
        )
