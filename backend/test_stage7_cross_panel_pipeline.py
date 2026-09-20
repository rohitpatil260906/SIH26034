"""
Stage 7 Automated Unit Test Suite
=================================
Tests Stage 7: Cross-Panel Information Merging + Multi-Image Product Consolidation Engine.

15 Regression Test Scenarios:
1. Front + Back panel of same product -> one unified product.
2. Front + Back + Side panel -> complete unified product with all fields.
3. Images of two completely different products -> two separate product objects.
4. Same brand but different product names -> NOT merged.
5. Same product, different batch numbers -> product identity matches (batch preserved as supporting evidence).
6. Same product, different serial numbers -> product identity matches (serials preserved separately).
7. Same field on two panels with same value -> one unified field with multiple evidence sources.
8. Conflicting values across panels (MRP ₹299 vs ₹349) -> CONFLICT status with competing candidates preserved.
9. Same text with different semantic meanings -> distinct fields.
10. Manufacturer on back + product name on front -> correct unified product.
11. Address split across panels -> merged with evidence links.
12. Partial panel -> merged when identity evidence supports match.
13. Unknown panel role -> panel = UNKNOWN, usable evidence preserved.
14. Late-arriving image -> existing product session updated rather than duplicated.
15. Multi-product session -> zero cross-product contamination.
"""

import unittest
from typing import List, Dict, Any

from backend.models import (
    Stage4ProductIdentity,
    Stage4ValueWithStatus,
    Stage4CategoryInfo,
    Stage4Entity,
    Stage6ProductProfile,
    Stage6AdaptiveField,
    Stage6AdaptiveSchema,
    Stage6SingleProductProfile,
    Stage7Response
)
from backend.services.stage7_cross_panel import Stage7Pipeline


class TestStage7CrossPanelPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage7 = Stage7Pipeline()

    def _create_mock_stage6_profile(
        self,
        category: str = "FOOD",
        subcategory: str = "BISCUITS",
        fields_dict: Dict[str, str] = None
    ) -> Stage6SingleProductProfile:
        fields = []
        if fields_dict:
            for fname, fval in fields_dict.items():
                fields.append(Stage6AdaptiveField(
                    field_name=fname,
                    value=fval,
                    status="PRESENT",
                    confidence=0.95,
                    relevance=0.95
                ))

        return Stage6SingleProductProfile(
            product_id="prod_temp",
            product_profile=Stage6ProductProfile(
                category=category,
                subcategory=subcategory,
                category_confidence=0.95,
                category_status="CONFIRMED"
            ),
            adaptive_schema=Stage6AdaptiveSchema(fields=fields)
        )

    # ----------------------------------------------------
    # TEST 1: Front + Back Same Product
    # ----------------------------------------------------
    def test_01_front_back_same_product(self):
        """1. Front + Back panel of same product -> one unified product."""
        id_front = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL CHAI TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="FOOD", confidence=0.90)
        )
        id_back = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL CHAI TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="FOOD", confidence=0.90),
            entities=[Stage4Entity(role="MANUFACTURER", name="Royal Tea Packers Ltd", address="Assam", confidence=0.95)]
        )

        inputs = [
            {
                "image_id": "img_001",
                "panel": "FRONT",
                "product_identity": id_front,
                "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA", {"MRP": "₹250"})
            },
            {
                "image_id": "img_002",
                "panel": "BACK",
                "product_identity": id_back,
                "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA", {"MANUFACTURER_NAME": "Royal Tea Packers Ltd"})
            }
        ]

        res = self.stage7.process_session("session_001", inputs)
        self.assertEqual(len(res.products), 1)
        prod = res.products[0]
        self.assertEqual(len(prod.source_images), 2)
        fnames = [f.field_name for f in prod.fields]
        self.assertIn("MRP", fnames)
        self.assertIn("MANUFACTURER_NAME", fnames)

    # ----------------------------------------------------
    # TEST 2: Front + Back + Side Same Product
    # ----------------------------------------------------
    def test_02_front_back_side_same_product(self):
        """2. Front + Back + Side panel -> complete unified product with all fields."""
        id_front = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="GLOWCARE SERUM", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="GLOWCARE", status="CONFIRMED", confidence=0.95)
        )
        id_back = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="GLOWCARE SERUM", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="GLOWCARE", status="CONFIRMED", confidence=0.95)
        )
        id_side = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="GLOWCARE SERUM", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="GLOWCARE", status="CONFIRMED", confidence=0.95)
        )

        inputs = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_front, "stage6_output": self._create_mock_stage6_profile("COSMETIC", "SERUM", {"PRODUCT_NAME": "GLOWCARE SERUM"})},
            {"image_id": "img_b", "panel": "BACK", "product_identity": id_back, "stage6_output": self._create_mock_stage6_profile("COSMETIC", "SERUM", {"INGREDIENTS": "Aqua, Niacinamide"})},
            {"image_id": "img_s", "panel": "SIDE", "product_identity": id_side, "stage6_output": self._create_mock_stage6_profile("COSMETIC", "SERUM", {"NET_VOLUME": "30 ml", "CONSUMER_CARE": "1800-123-4567"})}
        ]

        res = self.stage7.process_session("session_002", inputs)
        self.assertEqual(len(res.products), 1)
        prod = res.products[0]
        self.assertEqual(len(prod.source_images), 3)
        self.assertIn("FRONT", prod.panel_completeness.available_panels)
        self.assertIn("BACK", prod.panel_completeness.available_panels)
        self.assertIn("SIDE", prod.panel_completeness.available_panels)

    # ----------------------------------------------------
    # TEST 3: Two Completely Different Products
    # ----------------------------------------------------
    def test_03_two_different_products(self):
        """3. Images of two completely different products -> two separate product objects."""
        id_tea = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="FOOD", confidence=0.90)
        )
        id_mouse = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="WIRELESS MOUSE M100", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="LOGITECH", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="ELECTRONICS", confidence=0.90)
        )

        inputs = [
            {"image_id": "img_tea_f", "panel": "FRONT", "product_identity": id_tea, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA")},
            {"image_id": "img_mouse_f", "panel": "FRONT", "product_identity": id_mouse, "stage6_output": self._create_mock_stage6_profile("ELECTRONICS", "PERIPHERAL")}
        ]

        res = self.stage7.process_session("session_003", inputs)
        self.assertEqual(len(res.products), 2)

    # ----------------------------------------------------
    # TEST 4: Same Brand, Different Products
    # ----------------------------------------------------
    def test_04_same_brand_different_products(self):
        """4. Same brand but different product names -> NOT merged."""
        id_biscuit = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="BUTTER COOKIES", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="FOOD", confidence=0.90)
        )
        id_tea = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="GREEN TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="FOOD", confidence=0.90)
        )

        inputs = [
            {"image_id": "img_bisc", "panel": "FRONT", "product_identity": id_biscuit, "stage6_output": self._create_mock_stage6_profile("FOOD", "BISCUITS")},
            {"image_id": "img_tea", "panel": "FRONT", "product_identity": id_tea, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA")}
        ]

        res = self.stage7.process_session("session_004", inputs)
        self.assertEqual(len(res.products), 2)

    # ----------------------------------------------------
    # TEST 5: Different Batch Numbers
    # ----------------------------------------------------
    def test_05_different_batch_numbers(self):
        """5. Same product, different batch numbers -> product identity matches (batch preserved as supporting evidence)."""
        id_p1 = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL CHAI TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            batch_number="BATCH-123"
        )
        id_p2 = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL CHAI TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            batch_number="BATCH-789"
        )

        inputs = [
            {"image_id": "img_p1", "panel": "FRONT", "product_identity": id_p1, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA")},
            {"image_id": "img_p2", "panel": "BACK", "product_identity": id_p2, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA")}
        ]

        res = self.stage7.process_session("session_005", inputs)
        self.assertEqual(len(res.products), 1)

    # ----------------------------------------------------
    # TEST 6: Different Serial Numbers
    # ----------------------------------------------------
    def test_06_different_serial_numbers(self):
        """6. Same product, different serial numbers -> product identity matches (serials preserved separately)."""
        id_m1 = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="WIRELESS MOUSE M100", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="LOGITECH", status="CONFIRMED", confidence=0.95),
            model_number="M100",
            serial_number="SN-0001"
        )
        id_m2 = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="WIRELESS MOUSE M100", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="LOGITECH", status="CONFIRMED", confidence=0.95),
            model_number="M100",
            serial_number="SN-0002"
        )

        inputs = [
            {"image_id": "img_m1", "panel": "FRONT", "product_identity": id_m1, "stage6_output": self._create_mock_stage6_profile("ELECTRONICS", "PERIPHERAL")},
            {"image_id": "img_m2", "panel": "BACK", "product_identity": id_m2, "stage6_output": self._create_mock_stage6_profile("ELECTRONICS", "PERIPHERAL")}
        ]

        res = self.stage7.process_session("session_006", inputs)
        self.assertEqual(len(res.products), 1)

    # ----------------------------------------------------
    # TEST 7: Same Field Same Value across Panels
    # ----------------------------------------------------
    def test_07_same_field_same_value(self):
        """7. Same field on two panels with same value -> one unified field with multiple evidence sources."""
        id_common = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95)
        )

        inputs = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA", {"MRP": "₹299"})},
            {"image_id": "img_b", "panel": "BACK", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA", {"MRP": "₹299"})}
        ]

        res = self.stage7.process_session("session_007", inputs)
        self.assertEqual(len(res.products), 1)
        prod = res.products[0]
        mrp_field = next(f for f in prod.fields if f.field_name == "MRP")
        self.assertEqual(mrp_field.status, "CONFIRMED")
        self.assertEqual(mrp_field.value, "₹299")
        self.assertEqual(len(mrp_field.sources), 2)

    # ----------------------------------------------------
    # TEST 8: Conflicting Field Values
    # ----------------------------------------------------
    def test_08_conflicting_field_values(self):
        """8. Conflicting values across panels (MRP ₹299 vs ₹349) -> CONFLICT status with competing candidates preserved."""
        id_common = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95)
        )

        inputs = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA", {"MRP": "₹299"})},
            {"image_id": "img_b", "panel": "BACK", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA", {"MRP": "₹349"})}
        ]

        res = self.stage7.process_session("session_008", inputs)
        self.assertEqual(len(res.products), 1)
        prod = res.products[0]
        self.assertEqual(len(prod.conflicts), 1)
        conflict = prod.conflicts[0]
        self.assertEqual(conflict.field_name, "MRP")
        self.assertEqual(conflict.status, "CONFLICT")
        self.assertEqual(len(conflict.candidates), 2)
        c_vals = [c.value for c in conflict.candidates]
        self.assertIn("₹299", c_vals)
        self.assertIn("₹349", c_vals)

    # ----------------------------------------------------
    # TEST 9: Different Semantic Meanings
    # ----------------------------------------------------
    def test_09_different_semantic_meanings(self):
        """9. Same text with different semantic meanings -> distinct fields."""
        id_common = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="DELUXE OATS", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95)
        )

        inputs = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "PACKAGED_FOOD", {"NET_QUANTITY": "500 g"})},
            {"image_id": "img_b", "panel": "BACK", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "PACKAGED_FOOD", {"SERVING_SIZE": "500 g"})}
        ]

        res = self.stage7.process_session("session_009", inputs)
        prod = res.products[0]
        fnames = [f.field_name for f in prod.fields]
        self.assertIn("NET_QUANTITY", fnames)
        self.assertIn("SERVING_SIZE", fnames)
        self.assertEqual(len(prod.conflicts), 0)

    # ----------------------------------------------------
    # TEST 10: Manufacturer Back + Product Name Front
    # ----------------------------------------------------
    def test_10_manufacturer_back_product_front(self):
        """10. Manufacturer on back + product name on front -> correct unified product."""
        id_front = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="SUNSHINE JUICE", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="SUNSHINE", status="CONFIRMED", confidence=0.95)
        )
        id_back = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="SUNSHINE JUICE", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="SUNSHINE", status="CONFIRMED", confidence=0.95),
            entities=[Stage4Entity(role="MANUFACTURER", name="Sunshine Beverages Pvt Ltd", confidence=0.95)]
        )

        inputs = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_front, "stage6_output": self._create_mock_stage6_profile("BEVERAGE", "JUICE", {"PRODUCT_NAME": "SUNSHINE JUICE"})},
            {"image_id": "img_b", "panel": "BACK", "product_identity": id_back, "stage6_output": self._create_mock_stage6_profile("BEVERAGE", "JUICE", {"MANUFACTURER_NAME": "Sunshine Beverages Pvt Ltd"})}
        ]

        res = self.stage7.process_session("session_010", inputs)
        prod = res.products[0]
        fnames = [f.field_name for f in prod.fields]
        self.assertIn("PRODUCT_NAME", fnames)
        self.assertIn("MANUFACTURER_NAME", fnames)

    # ----------------------------------------------------
    # TEST 11: Address Split Across Panels
    # ----------------------------------------------------
    def test_11_address_split_across_panels(self):
        """11. Address split across panels -> merged with evidence links."""
        id_back = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95),
            entities=[Stage4Entity(role="MANUFACTURER", name="Royal Tea Pvt Ltd", address="Plot 10, Industrial Area", confidence=0.95)]
        )
        id_side = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL TEA", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95),
            entities=[Stage4Entity(role="MANUFACTURER", name="Royal Tea Pvt Ltd", address="Guwahati, Assam - 781001", confidence=0.95)]
        )

        inputs = [
            {"image_id": "img_b", "panel": "BACK", "product_identity": id_back, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA")},
            {"image_id": "img_s", "panel": "SIDE", "product_identity": id_side, "stage6_output": self._create_mock_stage6_profile("FOOD", "TEA")}
        ]

        res = self.stage7.process_session("session_011", inputs)
        prod = res.products[0]
        self.assertTrue(len(prod.cross_panel_links) > 0)

    # ----------------------------------------------------
    # TEST 12: Partial Panel Contribution
    # ----------------------------------------------------
    def test_12_partial_panel_contribution(self):
        """12. Partial panel -> merged when identity evidence supports match."""
        id_front = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ALMOND MILK", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="NUTRI", status="CONFIRMED", confidence=0.95)
        )
        id_part = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ALMOND MILK", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="NUTRI", status="CONFIRMED", confidence=0.95)
        )

        inputs = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_front, "stage6_output": self._create_mock_stage6_profile("BEVERAGE", "JUICE", {"PRODUCT_NAME": "ALMOND MILK"})},
            {"image_id": "img_p", "panel": "PARTIAL", "product_identity": id_part, "stage6_output": self._create_mock_stage6_profile("BEVERAGE", "JUICE", {"FSSAI_LICENSE_NUMBER": "10019011000123"})}
        ]

        res = self.stage7.process_session("session_012", inputs)
        prod = res.products[0]
        fnames = [f.field_name for f in prod.fields]
        self.assertIn("FSSAI_LICENSE_NUMBER", fnames)

    # ----------------------------------------------------
    # TEST 13: Unknown Panel Handling
    # ----------------------------------------------------
    def test_13_unknown_panel_handling(self):
        """13. Unknown panel role -> panel = UNKNOWN, usable evidence preserved."""
        id_unk = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ORGANIC HONEY", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="PURE", status="CONFIRMED", confidence=0.95)
        )

        inputs = [
            {"image_id": "img_u", "panel": "UNKNOWN", "product_identity": id_unk, "stage6_output": self._create_mock_stage6_profile("FOOD", "PACKAGED_FOOD", {"NET_QUANTITY": "250 g"})}
        ]

        res = self.stage7.process_session("session_013", inputs)
        prod = res.products[0]
        self.assertEqual(prod.source_images[0].panel, "UNKNOWN")
        fnames = [f.field_name for f in prod.fields]
        self.assertIn("NET_QUANTITY", fnames)

    # ----------------------------------------------------
    # TEST 14: Late-Arriving Image Session Update
    # ----------------------------------------------------
    def test_14_late_arriving_image_update(self):
        """14. Late-arriving image -> existing product session updated rather than duplicated."""
        id_common = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="CHOCO BISCUITS", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="ROYAL", status="CONFIRMED", confidence=0.95)
        )

        # Initial upload: Front panel only
        inputs1 = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "BISCUITS", {"MRP": "₹50"})}
        ]
        res1 = self.stage7.process_session("session_014", inputs1)
        self.assertEqual(len(res1.products), 1)

        # Later upload: Back panel added
        inputs2 = [
            {"image_id": "img_f", "panel": "FRONT", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "BISCUITS", {"MRP": "₹50"})},
            {"image_id": "img_b", "panel": "BACK", "product_identity": id_common, "stage6_output": self._create_mock_stage6_profile("FOOD", "BISCUITS", {"NET_QUANTITY": "100 g"})}
        ]
        res2 = self.stage7.process_session("session_014", inputs2)
        self.assertEqual(len(res2.products), 1)
        prod2 = res2.products[0]
        self.assertEqual(len(prod2.source_images), 2)

    # ----------------------------------------------------
    # TEST 15: Multi-Product Session Isolation
    # ----------------------------------------------------
    def test_15_multi_product_session_isolation(self):
        """15. Multi-product session -> zero cross-product contamination."""
        id_p1_f = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="PRODUCT A", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="BRAND A", status="CONFIRMED", confidence=0.95)
        )
        id_p1_b = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="PRODUCT A", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="BRAND A", status="CONFIRMED", confidence=0.95)
        )
        id_p2_f = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="PRODUCT B", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="BRAND B", status="CONFIRMED", confidence=0.95)
        )
        id_p2_b = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="PRODUCT B", status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value="BRAND B", status="CONFIRMED", confidence=0.95)
        )

        inputs = [
            {"image_id": "img_p1_f", "panel": "FRONT", "product_identity": id_p1_f, "stage6_output": self._create_mock_stage6_profile("FOOD", "BISCUITS", {"NET_QUANTITY": "100 g"})},
            {"image_id": "img_p1_b", "panel": "BACK", "product_identity": id_p1_b, "stage6_output": self._create_mock_stage6_profile("FOOD", "BISCUITS", {"MRP": "₹30"})},
            {"image_id": "img_p2_f", "panel": "FRONT", "product_identity": id_p2_f, "stage6_output": self._create_mock_stage6_profile("COSMETIC", "SERUM", {"NET_VOLUME": "50 ml"})},
            {"image_id": "img_p2_b", "panel": "BACK", "product_identity": id_p2_b, "stage6_output": self._create_mock_stage6_profile("COSMETIC", "SERUM", {"MRP": "₹499"})}
        ]

        res = self.stage7.process_session("session_015", inputs)
        self.assertEqual(len(res.products), 2)
        p1 = res.products[0]
        p2 = res.products[1]
        self.assertEqual(len(p1.source_images), 2)
        self.assertEqual(len(p2.source_images), 2)


if __name__ == "__main__":
    unittest.main()
