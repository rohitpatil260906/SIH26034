"""
Service 8: Product Classification Service
=========================================
Classifies packaged commodities into Categories A through R under Legal Metrology Rules,
and dynamically computes statutory field relevance weights:
- FOOD (Category A): Net quantity, ingredients, nutrition facts, serving size, batch, dates, veg logo
- BEVERAGES (Category B): Net volume, ingredients, nutrition, best before, container recyclability
- COSMETICS (Category C): Net quantity/vol, ingredients, directions, warnings, manufacturer/marketer, batch
- CLEANING (Category D): Net quantity, usage directions, safety warnings, manufacturer, MRP
- ELECTRONICS (Category F): Model number, product code, count/units, dimensions, importer, MRP
- TEXTILES (Category I): Garment sizing (chest/waist cm), fabric composition, count (1 N), MRP
- TOYS (Category H): Count (pieces), age suitability, BIS ISI mark, warnings, manufacturer/importer
- IMPORTED (Category P): Importer details, country of origin, date of import, MRP
"""

from typing import Dict, Any, Tuple, Optional, List
from ...models import ProductCategory, ProductClassification
from ..text_processor import classify_product_category


class ProductClassificationService:
    """Classifies packaging commodity and weights statutory field expectations."""

    CATEGORY_WEIGHTS: Dict[str, Dict[str, float]] = {
        ProductCategory.FOOD: {
            "net_quantity": 1.0,
            "ingredients": 0.95,
            "nutrition": 0.95,
            "serving_size": 0.90,
            "mrp": 1.0,
            "dates": 1.0,
            "batch": 0.95,
            "manufacturer": 1.0,
            "dimensions": 0.20
        },
        ProductCategory.COSMETICS: {
            "net_quantity": 1.0,
            "ingredients": 0.95,
            "directions": 0.90,
            "warnings": 0.90,
            "mrp": 1.0,
            "dates": 0.95,
            "batch": 0.95,
            "manufacturer": 1.0,
            "serving_size": 0.05
        },
        ProductCategory.CLEANING: {
            "net_quantity": 1.0,
            "usage": 0.90,
            "warnings": 0.95,
            "manufacturer": 1.0,
            "mrp": 1.0,
            "dates": 0.85,
            "batch": 0.85
        },
        ProductCategory.ELECTRONICS: {
            "net_quantity": 0.90,
            "model_number": 0.95,
            "product_code": 0.90,
            "dimensions": 0.90,
            "manufacturer": 1.0,
            "importer": 0.95,
            "mrp": 1.0,
            "ingredients": 0.05,
            "nutrition": 0.0
        },
        ProductCategory.TEXTILES: {
            "net_quantity": 0.95,
            "size": 1.0,
            "dimensions": 0.95,
            "fabric": 0.90,
            "mrp": 1.0,
            "manufacturer": 1.0,
            "nutrition": 0.0
        },
        ProductCategory.TOYS: {
            "net_quantity": 0.95,
            "count_pieces": 0.95,
            "age_suitability": 0.95,
            "warnings": 0.95,
            "manufacturer": 1.0,
            "mrp": 1.0,
            "nutrition": 0.0
        }
    }

    def __init__(self):
        pass

    def classify_product(
        self,
        text: str,
        lines: Optional[List[str]] = None
    ) -> ProductClassification:
        """Classifies product from label transcript text."""
        return classify_product_category(text, lines)

    def get_field_relevance(self, category_code: str, field_name: str) -> float:
        """Returns the relevance score [0.0 - 1.0] of a field for the product category."""
        # Find matching category weights
        for cat_str, weights in self.CATEGORY_WEIGHTS.items():
            if category_code in cat_str or cat_str in category_code:
                return weights.get(field_name, 0.5)
        return 0.5
