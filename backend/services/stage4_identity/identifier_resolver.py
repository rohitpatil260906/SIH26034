"""
Stage 4: Identifier & Country of Origin Resolver Service
========================================================
Extracts and strictly segregates technical identifiers from manufacturing lot data:
- Technical identifiers: Model Number, SKU, Article Number, Product Code
- Manufacturing identifiers: Batch Number, Lot Number, Serial Number
- Country of Origin: Explicit country declarations (Made in India, Country of Origin: China, etc.)

RULE: Never confuse Model/SKU with Batch/Lot numbers!
Do not infer Country of Origin solely from company address.
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from ...models import Stage2TextRegion, Stage3SemanticField


class IdentifierResolverService:
    """Disambiguates model numbers, SKUs, batches, lots, and country of origin."""

    # Model / SKU regexes
    MODEL_REGEX = re.compile(r'\b(?:model\s*no\.?|model\s*number|model)[:\s\-]*([A-Za-z0-9\-_/]+)', re.I)
    SKU_REGEX = re.compile(r'\b(?:sku\s*no\.?|sku)[:\s\-]*([A-Za-z0-9\-_/]+)', re.I)
    ARTICLE_REGEX = re.compile(r'\b(?:article\s*no\.?|item\s*no\.?|art\.\s*no\.?)[:\s\-]*([A-Za-z0-9\-_/]+)', re.I)
    PRODUCT_CODE_REGEX = re.compile(r'\b(?:product\s*code|part\s*no\.?|p\/n)[:\s\-]*([A-Za-z0-9\-_/]+)', re.I)

    # Batch / Lot / Serial regexes
    BATCH_REGEX = re.compile(r'\b(?:batch\s*no\.?|batch)[:\s\-]*([A-Za-z0-9\-_/]+)', re.I)
    LOT_REGEX = re.compile(r'\b(?:lot\s*no\.?|lot)[:\s\-]*([A-Za-z0-9\-_/]+)', re.I)
    SERIAL_REGEX = re.compile(r'\b(?:serial\s*no\.?|s\/n)[:\s\-]*([A-Za-z0-9\-_/]+)', re.I)

    # Country of Origin regexes
    COUNTRY_REGEX = re.compile(
        r'\b(?:country\s*o[fr]\s*origin|made\s+in|product\s+of|imported\s+from|mfd\s+in)\s*[:\s\-]*([A-Za-z\s]+)',
        re.I
    )

    KNOWN_COUNTRIES = {
        "india", "china", "germany", "japan", "usa", "united states", "vietnam",
        "thailand", "bangladesh", "indonesia", "italy", "france", "united kingdom", "uk",
        "taiwan", "south korea", "korea", "malaysia", "switzerland", "netherlands"
    }

    def extract_identifiers(
        self,
        regions: List[Stage2TextRegion],
        semantic_fields: List[Stage3SemanticField]
    ) -> Dict[str, Optional[str]]:
        """Extracts technical numbers, manufacturing batches, and country of origin."""
        res: Dict[str, Optional[str]] = {
            "model_number": None,
            "sku": None,
            "article_number": None,
            "product_code": None,
            "batch_number": None,
            "lot_number": None,
            "serial_number": None,
            "country_of_origin": None
        }

        # 1. Check Stage 3 semantic fields first
        for f in semantic_fields:
            if f.semantic_type == "BATCH_NUMBER" and not res["batch_number"]:
                res["batch_number"] = f.value
            elif f.semantic_type == "LOT_NUMBER" and not res["lot_number"]:
                res["lot_number"] = f.value
            elif f.semantic_type == "COUNTRY_OF_ORIGIN" and not res["country_of_origin"]:
                res["country_of_origin"] = f.value
            elif f.semantic_type == "MODEL_NUMBER" and not res["model_number"]:
                res["model_number"] = f.value

        # 2. Scan text regions
        for reg in regions:
            txt = (reg.normalized_text or reg.raw_text or "").strip()

            # Technical Identifiers
            if not res["model_number"]:
                m = self.MODEL_REGEX.search(txt)
                if m:
                    res["model_number"] = m.group(1).strip()

            if not res["sku"]:
                m = self.SKU_REGEX.search(txt)
                if m:
                    res["sku"] = m.group(1).strip()

            if not res["article_number"]:
                m = self.ARTICLE_REGEX.search(txt)
                if m:
                    res["article_number"] = m.group(1).strip()

            if not res["product_code"]:
                m = self.PRODUCT_CODE_REGEX.search(txt)
                if m:
                    res["product_code"] = m.group(1).strip()

            # Batch / Lot / Serial
            if not res["batch_number"]:
                m = self.BATCH_REGEX.search(txt)
                if m:
                    res["batch_number"] = m.group(1).strip()

            if not res["lot_number"]:
                m = self.LOT_REGEX.search(txt)
                if m:
                    res["lot_number"] = m.group(1).strip()

            if not res["serial_number"]:
                m = self.SERIAL_REGEX.search(txt)
                if m:
                    res["serial_number"] = m.group(1).strip()

            # Country of origin
            if not res["country_of_origin"]:
                m = self.COUNTRY_REGEX.search(txt)
                if m:
                    country_cand = m.group(1).strip()
                    # Clean punctuation
                    country_cand = re.sub(r'[,.;].*$', '', country_cand).strip()
                    # Verify it matches a known country or contains country word
                    first_words = country_cand.lower().split()
                    if first_words:
                        candidate_name = first_words[0]
                        if len(first_words) >= 2 and f"{first_words[0]} {first_words[1]}" in self.KNOWN_COUNTRIES:
                            candidate_name = f"{first_words[0]} {first_words[1]}"
                        
                        if candidate_name in self.KNOWN_COUNTRIES:
                            res["country_of_origin"] = candidate_name.title()
                        elif len(country_cand) >= 3 and country_cand.isalpha():
                            res["country_of_origin"] = country_cand.title()

        return res
