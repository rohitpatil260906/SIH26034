"""
Stage 4: Brand, Product Name, & Variant Resolver
================================================
Resolves:
- Product name (with CONFIRMED, PARTIAL, NOT_VISIBLE statuses)
- Brand name (strictly separated from Manufacturer/Company)
- Product variant (e.g. Lemon, Mint, Extra Strong, Pack of 10)

CRITICAL RULES:
- Back-panel-only images without product name -> product_name.status = "NOT_VISIBLE", value = "NOT_VISIBLE"
- Brand != Manufacturer (Never merge them automatically)
- Never invent/hallucinate missing product names
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from ...models import (
    Stage2TextRegion,
    Stage3SemanticField,
    Stage4ValueWithStatus
)


from .address_associator import AddressAssociatorService


class BrandProductResolverService:
    """Disambiguates and resolves Brand, Product Name, and Variant."""

    def __init__(self):
        self.address_service = AddressAssociatorService()

    # Common variant tokens
    VARIANT_PATTERNS = [
        re.compile(r'\b(?:lemon|lime|mint|orange|strawberry|chocolate|vanilla|almond|neem|tulsi|aloe\s*vera)\b', re.I),
        re.compile(r'\b(?:extra\s*strong|mild|classic|premium|deluxe|gold|silver|platinum|regular|diet|sugar\s*free|zero|ultra|pro)\b', re.I),
        re.compile(r'\b(?:small|medium|large|xl|xxl|pack\s*of\s*\d+|\d+\s*pcs?|combo)\b', re.I),
        re.compile(r'\b(?:red|blue|green|black|white|silver|matte|glossy)\b', re.I)
    ]

    # Category descriptor keywords that often appear in product names
    PRODUCT_DESCRIPTOR_WORDS = {
        "biscuits", "cookies", "chips", "tea", "coffee", "oil", "flour", "atta", "rice", "salt",
        "sugar", "jam", "sauce", "shampoo", "soap", "face wash", "serum", "lotion", "cream",
        "detergent", "cleaner", "liquid", "sanitizer", "toothpaste", "mouse", "keyboard",
        "charger", "adapter", "bulb", "notebook", "shirt", "t-shirt", "towel", "battery",
        "cable", "juice", "water", "perfume", "deodorant", "gel"
    }

    # Brand keywords to strip if explicit
    BRAND_PREFIX_REGEX = re.compile(r'^(?:brand|brand\s*name|tm|trademark)[:\s\-]*', re.I)

    def resolve_brand_product_variant(
        self,
        regions: List[Stage2TextRegion],
        semantic_fields: List[Stage3SemanticField],
        detected_company_names: List[str],
        source_panel: str = "UNKNOWN"
    ) -> Tuple[Stage4ValueWithStatus, Stage4ValueWithStatus, Stage4ValueWithStatus]:
        """Resolves (product_name, brand, variant) with strict status and confidence."""
        product_name = Stage4ValueWithStatus(value="NOT_VISIBLE", status="NOT_VISIBLE", confidence=0.0)
        brand = Stage4ValueWithStatus(value="NOT_VISIBLE", status="NOT_VISIBLE", confidence=0.0)
        variant = Stage4ValueWithStatus(value="", status="NOT_VISIBLE", confidence=0.0)

        # 1. Extract potential header / title regions (filtering statutory, company, numbers, and address)
        non_statutory_regions: List[Stage2TextRegion] = []
        for reg in regions:
            txt = (reg.normalized_text or reg.raw_text or "").strip()
            # Skip if statutory declaration
            if re.search(r'\b(?:mrp|net\s+qty|mfg|packed|marketed|imported|ingredients|nutrition|best\s+before|batch|exp)\b', txt, re.I):
                continue
            # Skip if company name
            if any(comp.lower() in txt.lower() for comp in detected_company_names):
                continue
            # Skip if address or postal PIN
            if self.address_service.is_address_text(txt):
                continue
            # Skip numbers or prices
            if re.match(r'^(?:₹|rs\.?|\d+)', txt, re.I):
                continue
            # Skip short punctuation noise
            if len(txt) < 3 or not any(c.isalpha() for c in txt):
                continue
            non_statutory_regions.append(reg)

        # 2. Check candidate title regions for Brand and Product Name
        if non_statutory_regions:
            sorted_candidates = sorted(non_statutory_regions, key=lambda r: (r.reading_order_index, r.bbox[1] if r.bbox else 0))
            
            # Check for explicit brand prefix (e.g. "Brand: PureBake")
            for reg in sorted_candidates:
                txt = (reg.normalized_text or reg.raw_text or "").strip()
                if self.BRAND_PREFIX_REGEX.search(txt):
                    brand_val = self.BRAND_PREFIX_REGEX.sub('', txt).strip()
                    if brand_val and brand.status == "NOT_VISIBLE":
                        brand = Stage4ValueWithStatus(
                            value=brand_val,
                            status="CONFIRMED",
                            confidence=0.95,
                            source_region_ids=[reg.region_id]
                        )

            # Look for Product Name and Brand in the top regions
            top_regions = [r for r in sorted_candidates if not self.BRAND_PREFIX_REGEX.search(r.raw_text)]
            if len(top_regions) >= 2:
                t1 = (top_regions[0].normalized_text or top_regions[0].raw_text or "").strip()
                t2 = (top_regions[1].normalized_text or top_regions[1].raw_text or "").strip()
                
                t1_has_desc = any(desc in t1.lower() for desc in self.PRODUCT_DESCRIPTOR_WORDS)
                t2_has_desc = any(desc in t2.lower() for desc in self.PRODUCT_DESCRIPTOR_WORDS)
                
                if t2_has_desc and not t1_has_desc:
                    # t1 is Brand, t2 is Product Name
                    if brand.status == "NOT_VISIBLE":
                        brand = Stage4ValueWithStatus(value=t1, status="CONFIRMED", confidence=0.92, source_region_ids=[top_regions[0].region_id])
                    product_name = Stage4ValueWithStatus(value=t2, status="CONFIRMED", confidence=0.94, source_region_ids=[top_regions[1].region_id])
                elif t1_has_desc and not t2_has_desc:
                    product_name = Stage4ValueWithStatus(value=t1, status="CONFIRMED", confidence=0.94, source_region_ids=[top_regions[0].region_id])
                    if brand.status == "NOT_VISIBLE":
                        brand = Stage4ValueWithStatus(value=t2, status="CONFIRMED", confidence=0.92, source_region_ids=[top_regions[1].region_id])
                else:
                    # Default: First line = Brand, Second line = Product Name
                    if brand.status == "NOT_VISIBLE":
                        brand = Stage4ValueWithStatus(value=t1, status="CONFIRMED", confidence=0.88, source_region_ids=[top_regions[0].region_id])
                    product_name = Stage4ValueWithStatus(value=t2, status="CONFIRMED", confidence=0.90, source_region_ids=[top_regions[1].region_id])
            
            elif len(top_regions) == 1:
                txt = (top_regions[0].normalized_text or top_regions[0].raw_text or "").strip()
                has_desc = any(desc in txt.lower() for desc in self.PRODUCT_DESCRIPTOR_WORDS)
                if has_desc:
                    product_name = Stage4ValueWithStatus(
                        value=txt,
                        status="CONFIRMED",
                        confidence=0.88,
                        source_region_ids=[top_regions[0].region_id]
                    )
                else:
                    # If on front panel, could be Brand or partial Product Name
                    if source_panel == "FRONT":
                        brand = Stage4ValueWithStatus(value=txt, status="CONFIRMED", confidence=0.80, source_region_ids=[top_regions[0].region_id])
                    elif source_panel != "BACK":
                        product_name = Stage4ValueWithStatus(value=txt, status="PARTIAL", confidence=0.65, source_region_ids=[top_regions[0].region_id])

        # 3. If product_name still NOT_VISIBLE, check Stage 3 confirmed field as fallback
        if product_name.status == "NOT_VISIBLE" and source_panel != "BACK":
            s3_prod_field = next((f for f in semantic_fields if f.semantic_type == "PRODUCT_NAME" and f.status == "CONFIRMED"), None)
            if s3_prod_field and not any(s3_prod_field.value.lower() == comp.lower() for comp in detected_company_names):
                product_name = Stage4ValueWithStatus(
                    value=s3_prod_field.value,
                    status="CONFIRMED",
                    confidence=s3_prod_field.semantic_confidence,
                    source_region_ids=s3_prod_field.source_region_ids
                )

        if brand.status == "NOT_VISIBLE":
            s3_brand_field = next((f for f in semantic_fields if f.semantic_type == "BRAND_NAME" and f.status == "CONFIRMED"), None)
            if s3_brand_field:
                brand = Stage4ValueWithStatus(
                    value=s3_brand_field.value,
                    status="CONFIRMED",
                    confidence=s3_brand_field.semantic_confidence,
                    source_region_ids=s3_brand_field.source_region_ids
                )

        # 4. Detect Variant
        # Scan all text for variant matches
        for reg in regions:
            txt = (reg.normalized_text or reg.raw_text or "").strip()
            for vpat in self.VARIANT_PATTERNS:
                vmatch = vpat.search(txt)
                if vmatch:
                    var_val = vmatch.group(0).strip()
                    # Don't duplicate full product name as variant
                    if var_val.lower() != product_name.value.lower():
                        variant = Stage4ValueWithStatus(
                            value=var_val.capitalize(),
                            status="CONFIRMED",
                            confidence=0.90,
                            source_region_ids=[reg.region_id]
                        )
                        break
            if variant.status == "CONFIRMED":
                break

        # 5. Panel Awareness Rule:
        # If Back Panel or Side Panel only, and product name was not explicitly identified in non-statutory lines
        if source_panel in ("BACK", "SIDE", "BOTTOM") and product_name.status != "CONFIRMED":
            product_name = Stage4ValueWithStatus(value="NOT_VISIBLE", status="NOT_VISIBLE", confidence=0.0)

        return product_name, brand, variant
