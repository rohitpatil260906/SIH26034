"""
Stage 6: Contextual Semantic Quantity & Value Differentiator
=============================================================
Disambiguates similar-looking numbers and unit measurements:
- Distinguishes Net Quantity vs Serving Size vs Ingredient Quantity vs Technical Weight.
- Distinguishes Net Volume vs Liquid Capacity vs Technical Capacity.
- Distinguishes Technical Dimensions (e.g. 10 mm) vs Statutory Declarations.
Ensures no value is classified solely based on its physical unit.
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from ...models import Stage3SemanticField, Stage3Response, Stage2TextRegion


class SemanticDifferentiator:
    """Disambiguates numerical quantities using Stage 3 relationships, headings, and category context."""

    def differentiate_quantity(
        self,
        raw_text: str,
        value: str,
        unit: Optional[str],
        semantic_type: Optional[str] = None,
        heading_text: Optional[str] = None,
        category: str = "UNKNOWN",
        source_region_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Determines true semantic field classification for a numerical quantity."""
        
        context_str = f"{raw_text} {heading_text or ''} {source_region_text or ''}".lower()
        unit_clean = (unit or "").lower().strip()

        # 1. Electronics / Electrical / Hardware / Tool Context
        if category in ("ELECTRONICS", "ELECTRICAL", "HARDWARE", "TOOLS"):
            # Check weight in tech specs
            if any(term in context_str for term in ["weight", "net weight", "item weight", "product weight", "mass", "weight:"]):
                if not any(term in context_str for term in ["net quantity", "net qty", "net vol", "net content"]):
                    return {
                        "differentiated_type": "TECHNICAL_WEIGHT",
                        "is_net_quantity": False,
                        "explanation": "Weight in electronics/technical specifications context"
                    }
            # Check dimensions (mm, cm, m, inch)
            if unit_clean in ("mm", "cm", "m", "inch", "inches", "mm²"):
                return {
                    "differentiated_type": "DIMENSION",
                    "is_net_quantity": False,
                    "explanation": "Technical dimension measurement"
                }

        # 2. Serving Size vs Net Quantity
        if any(term in context_str for term in ["serving size", "per serving", "serving", "per 100g", "per 100ml", "portion"]):
            if not any(term in context_str for term in ["net quantity", "net qty", "net weight", "net volume", "net content", "net wt"]):
                return {
                    "differentiated_type": "SERVING_SIZE",
                    "is_net_quantity": False,
                    "explanation": "Serving size declaration within nutrition context"
                }

        # 3. Ingredient Quantity
        if any(term in context_str for term in ["ingredients:", "contains:", "composition:", "active ingredients"]):
            # If inside ingredients block and not explicit Net Qty heading
            if not any(term in context_str for term in ["net quantity", "net qty"]):
                if semantic_type == "INGREDIENTS":
                    return {
                        "differentiated_type": "INGREDIENTS",
                        "is_net_quantity": False,
                        "explanation": "Entire ingredients list"
                    }
                return {
                    "differentiated_type": "INGREDIENT_QUANTITY",
                    "is_net_quantity": False,
                    "explanation": "Ingredient ratio or component quantity"
                }

        # 4. Dimension / Technical Spec Check
        if unit_clean in ("mm", "cm", "inches", "inch") or any(term in context_str for term in ["dimension", "size:", "length", "width", "height", "thickness"]):
            if category not in ("TEXTILE", "GARMENT", "FOOTWEAR"):
                return {
                    "differentiated_type": "TECHNICAL_SPECIFICATION",
                    "is_net_quantity": False,
                    "explanation": "Physical dimension or technical specification"
                }

        # 5. Net Volume vs Liquid Capacity
        if unit_clean in ("ml", "l", "ltr", "liter", "litres"):
            if any(term in context_str for term in ["capacity:", "volume capacity", "tank capacity", "holding capacity"]):
                return {
                    "differentiated_type": "LIQUID_CAPACITY",
                    "is_net_quantity": False,
                    "explanation": "Technical liquid capacity"
                }

        # 6. Explicit Net Quantity / Net Volume Signals
        if any(term in context_str for term in ["net quantity", "net qty", "net weight", "net volume", "net wt", "net content", "n.w.", "vol."]):
            is_vol = unit_clean in ("ml", "l", "ltr", "liter", "litres")
            return {
                "differentiated_type": "NET_VOLUME" if is_vol else "NET_QUANTITY",
                "is_net_quantity": True,
                "explanation": "Statutory Net Quantity / Net Volume declaration"
            }

        # 7. Fallback based on Stage 3 semantic type if passed
        if semantic_type and semantic_type not in ("NET_QUANTITY", "NET_VOLUME", "QUANTITY", "WEIGHT", "UNKNOWN"):
            return {
                "differentiated_type": semantic_type,
                "is_net_quantity": False,
                "explanation": f"Preserved Stage 3 semantic type: {semantic_type}"
            }

        # Default fallback for unknown quantity fields
        is_volume = unit_clean in ("ml", "l", "ltr", "liter", "litres")
        return {
            "differentiated_type": "NET_VOLUME" if is_volume else "NET_QUANTITY",
            "is_net_quantity": True,
            "explanation": "Standard quantity measurement"
        }
