"""
Stage 6: Multi-Signal Product Category Classifier
===================================================
Classifies product images into primary categories and subcategories by combining:
1. Product Name & Brand signals from Stage 4
2. Category Candidates from Stage 3
3. Semantic fields, ingredients, technical specifications, units, headings, and warnings
4. Domain vocabulary keyword matchers
5. Imported product evidence detection
6. Multi-candidate preservation & conservative safety gating when evidence is ambiguous
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from ...models import (
    Stage1Response,
    Stage2Response,
    Stage3Response,
    Stage4Response,
    Stage4ProductIdentity,
    Stage6ProductProfile,
    Stage6CategoryCandidate
)
from .category_hierarchy import PRIMARY_CATEGORIES, SUBCATEGORIES, normalize_category_name


class CategoryClassifier:
    """Multi-signal product category classifier."""

    def __init__(self):
        # Domain Vocabulary Signal Patterns
        self.vocab_patterns: Dict[str, Dict[str, Any]] = {
            "FOOD": {
                "keywords": [
                    "biscuit", "biscuits", "tea", "chai", "coffee", "spice", "spices", "masala",
                    "flour", "atta", "maida", "rice", "wheat", "dal", "oil", "ghee", "butter",
                    "snack", "chips", "chocolate", "candy", "milk", "paneer", "cheese", "noodle",
                    "sauce", "jam", "honey", "almond", "almonds", "cashew", "dry fruit", "sugar",
                    "salt", "edible", "nutritional", "nutrition", "calories", "carbohydrate", "protein",
                    "veg", "non-veg", "ingredients", "best before", "mfg date", "exp date", "fssai"
                ],
                "units": ["g", "kg", "mg", "ml", "l"],
                "sub_map": {
                    "BISCUITS": ["biscuit", "cookies", "wafer", "rusk"],
                    "TEA": ["tea", "chai", "green tea", "black tea"],
                    "SPICES": ["spice", "masala", "turmeric", "chilli", "coriander", "cumin"],
                    "FLOUR": ["flour", "atta", "maida", "suji", "besan"],
                    "SNACKS": ["snack", "chips", "namkeen", "bhujia", "popcorn"],
                    "PACKAGED_FOOD": ["almond", "almonds", "cashew", "raisin", "dry fruit", "honey", "jam"]
                }
            },
            "BEVERAGE": {
                "keywords": [
                    "drink", "juice", "soda", "water", "beverage", "cola", "pepsi", "coke",
                    "energy drink", "syrup", "squash", "nectar", "brew", "iced tea", "cold coffee"
                ],
                "units": ["ml", "l", "ltr"],
                "sub_map": {
                    "SOFT_DRINK": ["soda", "cola", "carbonated", "fizzy"],
                    "JUICE": ["juice", "nectar", "pulp", "fruit drink"],
                    "WATER": ["mineral water", "packaged drinking water", "spring water"],
                    "ENERGY_DRINK": ["energy drink", "caffeine", "taurine"]
                }
            },
            "COSMETIC": {
                "keywords": [
                    "serum", "cream", "lotion", "moisturizer", "sunscreen", "cleanser", "face wash",
                    "toner", "lipstick", "makeup", "foundation", "concealer", "mascara", "shampoo",
                    "conditioner", "hair oil", "soap", "body wash", "perfume", "fragrance", "deodorant",
                    "retinol", "niacinamide", "hyaluronic", "vitamin c", "aqua", "glycerin", "paraben",
                    "skin", "face", "hair", "dermatologically", "apply", "caution", "external use"
                ],
                "units": ["ml", "g"],
                "sub_map": {
                    "SERUM": ["serum", "dropper", "concentrate"],
                    "FACE_CARE": ["face wash", "face cream", "cleanser", "toner", "face mask"],
                    "SKIN_CARE": ["lotion", "moisturizer", "body lotion", "skin cream"],
                    "HAIR_CARE": ["shampoo", "conditioner", "hair oil", "hair serum"],
                    "MAKEUP": ["lipstick", "foundation", "concealer", "mascara", "eyeliner", "nail polish"],
                    "SOAP": ["soap", "bathing bar", "handwash"]
                }
            },
            "PERSONAL_CARE": {
                "keywords": [
                    "toothbrush", "toothpaste", "mouthwash", "shaving", "razor", "aftershave",
                    "sanitary", "pad", "diaper", "wipes", "cotton swabs", "hygiene"
                ],
                "units": ["g", "ml", "pcs", "pack"],
                "sub_map": {
                    "ORAL_CARE": ["toothbrush", "toothpaste", "mouthwash", "floss"],
                    "SHAVING": ["shaving", "razor", "blade", "shaving cream"],
                    "HYGIENE": ["wipes", "sanitary", "diaper", "hand sanitizer"]
                }
            },
            "HOUSEHOLD_CLEANING": {
                "keywords": [
                    "detergent", "washing powder", "fabric conditioner", "cleaner", "surface cleaner",
                    "floor cleaner", "toilet cleaner", "dishwash", "dishwashing", "bleach", "disinfectant",
                    "insecticide", "mosquito", "repellent", "air freshener", "phenyl", "acid"
                ],
                "units": ["g", "kg", "ml", "l"],
                "sub_map": {
                    "DETERGENT": ["detergent", "washing powder", "laundry", "fabric conditioner"],
                    "CLEANER": ["floor cleaner", "surface cleaner", "glass cleaner", "bathroom cleaner"],
                    "DISINFECTANT": ["disinfectant", "sanitizer", "antiseptic", "phenyl"],
                    "DISHWASH": ["dishwash", "dishwashing", "vessel cleaner"]
                }
            },
            "ELECTRONICS": {
                "keywords": [
                    "wireless", "bluetooth", "mouse", "keyboard", "headphones", "earphones", "earbuds",
                    "speaker", "charger", "adapter", "cable", "usb", "power bank", "powerbank", "mobile",
                    "phone", "smartphone", "laptop", "monitor", "camera", "led", "smartwatch", "gadget",
                    "input", "output", "voltage", "current", "mah", "watt", "frequency", "model", "serial no"
                ],
                "units": ["v", "a", "w", "mah", "hz", "ghz", "mb", "gb"],
                "sub_map": {
                    "COMPUTER_ACCESSORY": ["mouse", "keyboard", "webcam", "monitor", "dock"],
                    "MOBILE_ACCESSORY": ["charger", "adapter", "cable", "usb", "power bank", "case"],
                    "AUDIO": ["headphones", "earphones", "earbuds", "speaker", "soundbar", "mic"],
                    "GADGET": ["smartwatch", "fitness band", "tracker"]
                }
            },
            "ELECTRICAL": {
                "keywords": [
                    "bulb", "tube light", "led light", "switch", "socket", "wire", "cable", "mcb",
                    "extension board", "plug", "holder", "stabilizer", "transformer", "fan", "heater"
                ],
                "units": ["v", "w", "a", "meter", "m"],
                "sub_map": {
                    "BULB": ["bulb", "led bulb", "tube light", "spotlight"],
                    "WIRE_CABLE": ["wire", "cable", "copper wire", "flex cord"],
                    "SWITCH": ["switch", "socket", "plug", "mcb"]
                }
            },
            "TEXTILE": {
                "keywords": [
                    "fabric", "bedsheet", "pillow cover", "towel", "curtain", "blanket", "quilt",
                    "linen", "cotton fabric", "polyester fabric", "yarn", "thread", "suiting", "shirting"
                ],
                "units": ["m", "meter", "cm", "inch", "count"],
                "sub_map": {
                    "BEDDING": ["bedsheet", "pillow cover", "blanket", "quilt"],
                    "TOWEL": ["towel", "bath towel", "hand towel"],
                    "FABRIC": ["fabric", "suiting", "shirting", "dress material"]
                }
            },
            "GARMENT": {
                "keywords": [
                    "t-shirt", "tshirt", "shirt", "pants", "trousers", "jeans", "shorts", "dress",
                    "skirt", "jacket", "coat", "sweater", "hoodie", "innerwear", "briefs", "vest",
                    "cotton", "polyester", "elastane", "fabric composition", "care instructions",
                    "wash care", "do not bleach", "iron", "size"
                ],
                "units": ["size", "s", "m", "l", "xl", "xxl", "cm"],
                "sub_map": {
                    "TSHIRT": ["t-shirt", "tshirt", "polo"],
                    "SHIRT": ["formal shirt", "casual shirt", "shirt"],
                    "PANTS": ["pants", "trousers", "jeans", "chinos"],
                    "INNERWEAR": ["innerwear", "briefs", "vest", "socks"]
                }
            },
            "FOOTWEAR": {
                "keywords": [
                    "shoes", "sneakers", "running shoes", "sandals", "slippers", "flip flops",
                    "boots", "footwear", "sole", "upper material", "rubber sole", "leather shoes"
                ],
                "units": ["size", "uk", "us", "eu"],
                "sub_map": {
                    "SHOES": ["shoes", "sneakers", "running shoes", "formal shoes", "boots"],
                    "SANDALS": ["sandals", "floaters"],
                    "SLIPPERS": ["slippers", "flip flops", "chappal"]
                }
            },
            "TOYS": {
                "keywords": [
                    "toy", "toys", "action figure", "doll", "puzzle", "board game", "building blocks",
                    "lego", "car toy", "rc car", "plush", "soft toy", "rattle", "educational toy",
                    "age 3+", "age 6+", "choking hazard", "safety warning", "not suitable for children"
                ],
                "units": ["years", "age", "pieces"],
                "sub_map": {
                    "ACTION_FIGURE": ["action figure", "hero", "figurine"],
                    "PUZZLE": ["puzzle", "jigsaw", "board game"],
                    "EDUCATIONAL": ["learning toy", "building blocks", "stem toy"]
                }
            },
            "STATIONERY": {
                "keywords": [
                    "notebook", "register", "notepad", "pen", "ballpen", "gel pen", "pencil",
                    "eraser", "sharpener", "ruler", "scale", "marker", "highlighter", "stapler",
                    "paper", "a4 paper", "pages", "gsm", "geometry box", "drawing book"
                ],
                "units": ["pages", "gsm", "mm", "pcs"],
                "sub_map": {
                    "NOTEBOOK": ["notebook", "register", "notepad", "drawing book"],
                    "PEN_PENCIL": ["pen", "ballpen", "gel pen", "pencil", "marker", "highlighter"]
                }
            },
            "HARDWARE": {
                "keywords": [
                    "screw", "bolt", "nut", "washer", "nail", "hinge", "lock", "padlock", "handle",
                    "pipe", "fitting", "pvc pipe", "valve", "bracket", "fastener", "hardware"
                ],
                "units": ["mm", "inch", "pcs", "kg"],
                "sub_map": {
                    "FASTENERS": ["screw", "bolt", "nut", "washer", "nail"],
                    "LOCKS": ["lock", "padlock", "latch"],
                    "PLUMBING": ["pipe", "fitting", "valve", "pvc"]
                }
            },
            "TOOLS": {
                "keywords": [
                    "screwdriver", "wrench", "spanner", "pliers", "hammer", "drill", "power drill",
                    "saw", "tape measure", "level", "chisel", "chrome vanadium", "torque", "tool"
                ],
                "units": ["mm", "inch", "v", "watt"],
                "sub_map": {
                    "HAND_TOOL": ["screwdriver", "wrench", "spanner", "pliers", "hammer"],
                    "POWER_TOOL": ["drill", "power drill", "grinder", "saw"],
                    "MEASURING_TOOL": ["tape measure", "level", "caliper"]
                }
            },
            "AGRICULTURAL": {
                "keywords": [
                    "seeds", "seed", "fertilizer", "npk", "pesticide", "insecticide", "fungicide",
                    "herbicide", "crop", "hybrid seeds", "germination", "purity", "grain feed"
                ],
                "units": ["g", "kg", "ml", "l"],
                "sub_map": {
                    "SEEDS": ["seeds", "seed", "hybrid seeds"],
                    "FERTILIZER": ["fertilizer", "npk", "urea", "compost"],
                    "PESTICIDE": ["pesticide", "insecticide", "fungicide", "herbicide"]
                }
            }
        }

    def classify_product(
        self,
        stage4_output: Optional[Stage4Response] = None,
        stage3_output: Optional[Stage3Response] = None,
        stage2_output: Optional[Stage2Response] = None,
        stage1_output: Optional[Stage1Response] = None,
        product_identity: Optional[Stage4ProductIdentity] = None
    ) -> Stage6ProductProfile:
        """Analyzes all available multi-stage signals to classify product category & subcategory."""
        
        scores: Dict[str, float] = {cat: 0.0 for cat in PRIMARY_CATEGORIES}
        evidence_by_cat: Dict[str, List[str]] = {cat: [] for cat in PRIMARY_CATEGORIES}

        # Collect text corpus
        combined_texts: List[str] = []

        # 1. Inspect Stage 4 Identity
        product_name = ""
        brand = ""
        stage4_cat = ""
        if product_identity:
            product_name = product_identity.product_name.value if product_identity.product_name else ""
            brand = product_identity.brand.value if product_identity.brand else ""
            stage4_cat = product_identity.category.value if product_identity.category else ""
        elif stage4_output and stage4_output.identity:
            product_name = stage4_output.identity.product_name.value if stage4_output.identity.product_name else ""
            brand = stage4_output.identity.brand.value if stage4_output.identity.brand else ""
            stage4_cat = stage4_output.identity.category.value if stage4_output.identity.category else ""

        if product_name and product_name != "NOT_VISIBLE":
            combined_texts.append(product_name.lower())
        if brand and brand != "NOT_VISIBLE":
            combined_texts.append(brand.lower())
        if stage4_cat and stage4_cat != "UNKNOWN":
            norm_s4 = normalize_category_name(stage4_cat)
            if norm_s4 in scores:
                scores[norm_s4] += 0.45
                evidence_by_cat[norm_s4].append(f"Stage 4 Category Signal: {stage4_cat}")

        # 2. Inspect Stage 3 Semantic Outputs
        if stage3_output:
            # Stage 3 category candidates
            if stage3_output.category_candidates:
                for cand in stage3_output.category_candidates:
                    norm_c = normalize_category_name(cand.category)
                    if norm_c in scores:
                        scores[norm_c] += cand.confidence * 0.40
                        evidence_by_cat[norm_c].append(f"Stage 3 Category Candidate: {cand.category} ({cand.confidence:.2f})")

            # Semantic fields
            for sf in stage3_output.semantic_fields:
                val = (sf.value or "").lower()
                combined_texts.append(val)
                stype = sf.semantic_type
                if stype in ("INGREDIENTS", "COMPOSITION"):
                    scores["FOOD"] += 0.30
                    scores["COSMETIC"] += 0.25
                    evidence_by_cat["FOOD"].append(f"Ingredients field present: {sf.value[:30]}")
                    evidence_by_cat["COSMETIC"].append(f"Ingredients field present: {sf.value[:30]}")
                elif stype == "NUTRITIONAL_INFORMATION":
                    scores["FOOD"] += 0.55
                    evidence_by_cat["FOOD"].append("Nutritional information table present")
                elif stype in ("MODEL_NUMBER", "SERIAL_NUMBER", "TECHNICAL_SPECIFICATION"):
                    scores["ELECTRONICS"] += 0.45
                    scores["ELECTRICAL"] += 0.35
                    evidence_by_cat["ELECTRONICS"].append(f"Technical/Model identifier: {sf.semantic_type}={sf.value}")
                elif stype == "AGE_RANGE":
                    scores["TOYS"] += 0.60
                    evidence_by_cat["TOYS"].append(f"Age range declaration: {sf.value}")
                elif stype == "CARE_INSTRUCTIONS":
                    scores["TEXTILE"] += 0.40
                    scores["GARMENT"] += 0.45
                    evidence_by_cat["GARMENT"].append(f"Care instructions: {sf.value[:30]}")

        # 3. Inspect Stage 2 Text Regions
        if stage2_output and stage2_output.regions:
            for reg in stage2_output.regions:
                txt = (reg.normalized_text or reg.raw_text or "").lower()
                combined_texts.append(txt)

        corpus_str = " ".join(combined_texts)

        # 4. Multi-Domain Vocabulary Keyword Matching
        for cat, config in self.vocab_patterns.items():
            for kw in config["keywords"]:
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = len(re.findall(pattern, corpus_str))
                if matches > 0:
                    weight = 0.15 if len(kw) > 3 else 0.08
                    add_score = min(0.40, matches * weight)
                    scores[cat] += add_score
                    evidence_by_cat[cat].append(f"Matched keyword '{kw}' ({matches}x)")

        # 5. Imported Product Detection Signal
        imported_terms = ["imported by", "importer", "country of origin", "made in", "product of"]
        if any(term in corpus_str for term in imported_terms):
            scores["IMPORTED_PRODUCT"] += 0.30
            evidence_by_cat["IMPORTED_PRODUCT"].append("Import evidence detected")

        # 6. Rank Candidates & Determine Subcategory
        ranked_candidates: List[Stage6CategoryCandidate] = []
        for cat, score in scores.items():
            if cat in ("UNKNOWN", "OTHER") or score < 0.15:
                continue

            # Subcategory determination
            sub_name: Optional[str] = None
            if cat in self.vocab_patterns and "sub_map" in self.vocab_patterns[cat]:
                for sub, sub_kws in self.vocab_patterns[cat]["sub_map"].items():
                    if any(skw in corpus_str for skw in sub_kws):
                        sub_name = sub
                        break

            conf = round(min(0.99, score), 2)
            ranked_candidates.append(
                Stage6CategoryCandidate(
                    category=cat,
                    subcategory=sub_name,
                    confidence=conf,
                    evidence=list(dict.fromkeys(evidence_by_cat[cat]))[:4]
                )
            )

        ranked_candidates.sort(key=lambda c: c.confidence, reverse=True)

        if not ranked_candidates:
            return Stage6ProductProfile(
                category="UNKNOWN",
                subcategory=None,
                category_confidence=0.0,
                category_status="NEEDS_REVIEW",
                category_evidence=["Insufficient visible category evidence"],
                category_candidates=[]
            )

        top_cand = ranked_candidates[0]

        # Multi-Candidate Ambiguity Check
        if len(ranked_candidates) > 1:
            second_cand = ranked_candidates[1]
            # If top two candidates are very close (confidence delta < 0.12 and top < 0.70)
            if (top_cand.confidence - second_cand.confidence < 0.12) and top_cand.confidence < 0.70:
                return Stage6ProductProfile(
                    category="UNKNOWN",
                    subcategory=top_cand.subcategory,
                    category_confidence=top_cand.confidence,
                    category_status="NEEDS_REVIEW",
                    category_evidence=top_cand.evidence,
                    category_candidates=ranked_candidates[:3]
                )

        if top_cand.confidence >= 0.55:
            status = "CONFIRMED"
        elif top_cand.confidence >= 0.35:
            status = "NEEDS_REVIEW"
        else:
            return Stage6ProductProfile(
                category="UNKNOWN",
                subcategory=None,
                category_confidence=top_cand.confidence,
                category_status="NEEDS_REVIEW",
                category_evidence=top_cand.evidence,
                category_candidates=ranked_candidates[:3]
            )

        return Stage6ProductProfile(
            category=top_cand.category,
            subcategory=top_cand.subcategory,
            category_confidence=top_cand.confidence,
            category_status=status,
            category_evidence=top_cand.evidence,
            category_candidates=ranked_candidates[:3]
        )
