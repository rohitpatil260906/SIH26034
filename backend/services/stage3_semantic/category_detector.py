"""
Stage 3: Product Category Signal Detection Service
==================================================
Generates candidate category signals based on packaging lexical evidence
without performing ungrounded, rigid final classification:
- FOOD (biscuits, flour, edible, cocoa, sugar, nutrition facts)
- BEVERAGE (juice, water, soda, drink, tea, coffee)
- COSMETIC (serum, lotion, cream, glow, skin, fragrance, face)
- PERSONAL_CARE (shampoo, soap, toothpaste, body wash)
- HOUSEHOLD / CLEANING (detergent, floor cleaner, disinfectant)
- ELECTRONICS / ELECTRICAL (adapter, charger, USB, volt, Hz, cable, mouse)
- TEXTILE / GARMENT (shirt, cotton, size, chest, polyester)
- IMPORTED_PRODUCT (country of origin, imported by)
"""

import re
from typing import List, Dict, Any, Tuple
from ...models import Stage2TextRegion, Stage3CategoryCandidate


class CategorySignalDetector:
    """Detects category signals with traceable evidence keywords."""

    CATEGORY_SIGNALS = {
        "FOOD": [
            "biscuit", "cookie", "cake", "bread", "flour", "wheat", "atta", "sugar",
            "salt", "spice", "snack", "crisp", "edible", "oil", "cocoa", "chocolate",
            "ingredients", "nutritional", "veg", "non-veg", "energy", "protein"
        ],
        "BEVERAGE": [
            "water", "mineral water", "juice", "drink", "soda", "cola", "tea",
            "coffee", "beverage", "syrup", "energy drink"
        ],
        "COSMETIC": [
            "serum", "lotion", "cream", "moisturizer", "sunscreen", "glow", "radiance",
            "anti-aging", "skin", "face", "lipstick", "makeup", "cosmetics"
        ],
        "PERSONAL_CARE": [
            "shampoo", "conditioner", "soap", "body wash", "toothpaste", "dental",
            "toothbrush", "deodorant", "hair", "shaving"
        ],
        "CLEANING": [
            "detergent", "disinfectant", "floor cleaner", "bleach", "soap powder",
            "toilet cleaner", "dishwash"
        ],
        "ELECTRONICS": [
            "adapter", "charger", "cable", "usb", "bluetooth", "wireless", "mouse",
            "keyboard", "headphones", "battery", "volt", "voltage", "hz", "watt"
        ],
        "TEXTILE": [
            "shirt", "trousers", "fabric", "cotton", "polyester", "wool", "silk",
            "garment", "chest", "waist", "cm", "apparel"
        ],
        "IMPORTED_PRODUCT": [
            "imported by", "country of origin", "made in", "origin:"
        ]
    }

    def detect_category_signals(
        self,
        regions: List[Stage2TextRegion]
    ) -> List[Stage3CategoryCandidate]:
        """Scans all visible text tokens and ranks category candidates based on signal density."""
        if not regions:
            return [Stage3CategoryCandidate(category="UNKNOWN", confidence=1.0, evidence_signals=[])]

        combined_text = " ".join((r.normalized_text or r.raw_text or "").lower() for r in regions)
        scores: Dict[str, List[str]] = {}

        for cat, keywords in self.CATEGORY_SIGNALS.items():
            matched_kw = []
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                    matched_kw.append(kw)
            if matched_kw:
                scores[cat] = matched_kw

        if not scores:
            return [Stage3CategoryCandidate(category="UNKNOWN", confidence=0.75, evidence_signals=[])]

        # Rank by number of matching distinct evidence keywords
        total_matches = sum(len(kw_list) for kw_list in scores.values())
        candidates: List[Stage3CategoryCandidate] = []

        for cat, kw_list in sorted(scores.items(), key=lambda item: len(item[1]), reverse=True):
            conf = round(min(0.98, len(kw_list) / float(max(1, len(kw_list) + 2))), 2)
            candidates.append(
                Stage3CategoryCandidate(
                    category=cat,
                    confidence=conf,
                    evidence_signals=kw_list[:6]
                )
            )

        return candidates
