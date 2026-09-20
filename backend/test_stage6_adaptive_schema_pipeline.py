"""
LM-COMPASS Stage 6 Automated Regression Test Suite
===================================================
Tests 18 representative product category scenarios and adaptive schema features:
1.  Packaged food (FOOD category + ingredients/nutrition schema)
2.  Cosmetic face serum (COSMETIC category + serum/skin care fields)
3.  Wireless mouse (ELECTRONICS category + model/technical specification fields)
4.  Detergent (HOUSEHOLD_CLEANING category)
5.  T-Shirt (TEXTILE / GARMENT category + size/material/care fields)
6.  Shoes (FOOTWEAR category + size/material fields)
7.  Toy (TOYS category + age range & choking warning fields)
8.  Stationery (STATIONERY category + paper/pages fields)
9.  Hardware tool (HARDWARE / TOOLS category + technical specs)
10. Ambiguous product (UNKNOWN or candidates + NEEDS_REVIEW)
11. "50 g" under Serving Size (SERVING_SIZE differentiation)
12. "50 g" under Net Quantity (NET_QUANTITY differentiation)
13. "450 g" under Weight in electronics specifications (TECHNICAL_WEIGHT, not Net Qty)
14. "10 mm" in technical specifications (DIMENSION / TECHNICAL_SPECIFICATION)
15. Multiple products in one image (separate product_001 & product_002 profiles)
16. Category-specific field not visible (NOT_VISIBLE status)
17. Irrelevant category field (NOT_APPLICABLE status)
18. Insufficient category evidence (UNKNOWN / NEEDS_REVIEW status)
"""

import unittest
from typing import List

from backend.models import (
    Stage1Response,
    Stage1InputMetadata,
    Stage1QualityResult,
    Stage1PackageDetection,
    Stage1PanelInfo,
    Stage1GeometryResult,
    Stage2Response,
    Stage2TextRegion,
    Stage3Response,
    Stage3SemanticField,
    Stage3CategoryCandidate,
    Stage4Response,
    Stage4ProductIdentity,
    Stage4ValueWithStatus,
    Stage4CategoryInfo,
    Stage4Entity,
    Stage6Response,
    Stage6SingleProductProfile,
    Stage6AdaptiveField
)
from backend.services.stage6_adaptive_schema import Stage6Pipeline
from backend.services.stage6_adaptive_schema.semantic_differentiator import SemanticDifferentiator
from backend.services.stage6_adaptive_schema.field_relevance import FieldRelevanceEngine


class TestStage6AdaptiveSchemaPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage6 = Stage6Pipeline()
        cls.differentiator = SemanticDifferentiator()
        cls.relevance_engine = FieldRelevanceEngine()

    def _create_mock_stage4_output(
        self,
        product_name: str = "DELUXE ROYAL ALMONDS",
        brand: str = "ROYAL NUTRIENTS",
        category_cand: str = "FOOD",
        entities: List[Stage4Entity] = None
    ) -> Stage4Response:
        identity = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value=product_name, status="CONFIRMED", confidence=0.95),
            brand=Stage4ValueWithStatus(value=brand, status="CONFIRMED", confidence=0.92),
            category=Stage4CategoryInfo(value=category_cand, confidence=0.90),
            country_of_origin="India",
            entities=entities or [
                Stage4Entity(role="MANUFACTURER", name="Royal Nutrients Pvt Ltd", address="Mumbai - 400013", confidence=0.95)
            ]
        )
        return Stage4Response(
            scan_id="STAGE4-TEST-001",
            identity_status="CONFIRMED",
            identity=identity,
            products=[identity]
        )

    def _create_mock_stage3_output(self, fields: List[Stage3SemanticField]) -> Stage3Response:
        return Stage3Response(
            scan_id="STAGE3-TEST-001",
            semantic_status="COMPLETED",
            semantic_fields=fields
        )

    # ----------------------------------------------------
    # TEST 1: Packaged Food
    # ----------------------------------------------------
    def test_01_packaged_food(self):
        """1. Packaged food: FOOD category and food-specific schema."""
        s4 = self._create_mock_stage4_output("DELUXE ROYAL ALMONDS", "ROYAL NUTRIENTS", "FOOD")
        s3 = self._create_mock_stage3_output([
            Stage3SemanticField(field_id="f1", semantic_type="NET_QUANTITY", value="500 g", unit="g", raw_text="Net Qty: 500 g"),
            Stage3SemanticField(field_id="f2", semantic_type="INGREDIENTS", value="Almonds", raw_text="Ingredients: Almonds"),
            Stage3SemanticField(field_id="f3", semantic_type="NUTRITIONAL_INFORMATION", value="Energy 570 kcal", raw_text="Nutrition Information")
        ])
        res = self.stage6.process_from_stages(stage4_output=s4, stage3_output=s3)
        self.assertEqual(len(res.products), 1)
        profile = res.products[0]
        self.assertEqual(profile.product_profile.category, "FOOD")
        fields_dict = {f.field_name: f for f in profile.adaptive_schema.fields}
        self.assertEqual(fields_dict["INGREDIENTS"].status, "PRESENT")
        self.assertEqual(fields_dict["NUTRITIONAL_INFORMATION"].status, "PRESENT")

    # ----------------------------------------------------
    # TEST 2: Cosmetic Face Serum
    # ----------------------------------------------------
    def test_02_cosmetic_serum(self):
        """2. Cosmetic face serum: COSMETIC category and cosmetic fields."""
        s4 = self._create_mock_stage4_output("VITAMIN C FACE SERUM", "GLOWCARE", "COSMETIC")
        s3 = self._create_mock_stage3_output([
            Stage3SemanticField(field_id="f1", semantic_type="NET_VOLUME", value="30 ml", unit="ml", raw_text="Net Vol: 30 ml"),
            Stage3SemanticField(field_id="f2", semantic_type="INGREDIENTS", value="Aqua, Niacinamide, Hyaluronic Acid", raw_text="Ingredients: Aqua..."),
            Stage3SemanticField(field_id="f3", semantic_type="DIRECTIONS_FOR_USE", value="Apply 3-4 drops on clean face", raw_text="Directions for Use")
        ])
        res = self.stage6.process_from_stages(stage4_output=s4, stage3_output=s3)
        profile = res.products[0]
        self.assertEqual(profile.product_profile.category, "COSMETIC")
        self.assertEqual(profile.product_profile.subcategory, "SERUM")
        fields_dict = {f.field_name: f for f in profile.adaptive_schema.fields}
        self.assertEqual(fields_dict["DIRECTIONS_FOR_USE"].status, "PRESENT")

    # ----------------------------------------------------
    # TEST 3: Wireless Mouse
    # ----------------------------------------------------
    def test_03_wireless_mouse(self):
        """3. Wireless mouse: ELECTRONICS category and model/technical fields."""
        s4 = self._create_mock_stage4_output("WIRELESS OPTICAL MOUSE", "TECHPRO", "ELECTRONICS")
        s4.identity.model_number = Stage4ValueWithStatus(value="WM-200", status="CONFIRMED", confidence=0.95)
        s3 = self._create_mock_stage3_output([
            Stage3SemanticField(field_id="f1", semantic_type="TECHNICAL_SPECIFICATION", value="5V 100mA", unit="V", raw_text="Input: 5V 100mA")
        ])
        res = self.stage6.process_from_stages(stage4_output=s4, stage3_output=s3)
        profile = res.products[0]
        self.assertEqual(profile.product_profile.category, "ELECTRONICS")
        fields_dict = {f.field_name: f for f in profile.adaptive_schema.fields}
        self.assertEqual(fields_dict["MODEL_NUMBER"].value, "WM-200")
        self.assertEqual(fields_dict["MODEL_NUMBER"].status, "PRESENT")

    # ----------------------------------------------------
    # TEST 4: Detergent
    # ----------------------------------------------------
    def test_04_detergent(self):
        """4. Laundry detergent: HOUSEHOLD_CLEANING category."""
        s4 = self._create_mock_stage4_output("ULTRA CLEAN LAUNDRY DETERGENT POWDER", "CLEANEX", "HOUSEHOLD_CLEANING")
        res = self.stage6.process_from_stages(stage4_output=s4)
        profile = res.products[0]
        self.assertEqual(profile.product_profile.category, "HOUSEHOLD_CLEANING")

    # ----------------------------------------------------
    # TEST 5: T-Shirt
    # ----------------------------------------------------
    def test_05_tshirt(self):
        """5. T-shirt: TEXTILE / GARMENT category with size/material/care fields."""
        s4 = self._create_mock_stage4_output("MEN COTTON ROUND NECK T-SHIRT", "URBANWEAR", "GARMENT")
        s3 = self._create_mock_stage3_output([
            Stage3SemanticField(field_id="f1", semantic_type="GARMENT_SIZE", value="L", raw_text="Size: L"),
            Stage3SemanticField(field_id="f2", semantic_type="FABRIC_COMPOSITION", value="100% Cotton", raw_text="100% Cotton"),
            Stage3SemanticField(field_id="f3", semantic_type="CARE_INSTRUCTIONS", value="Machine wash cold", raw_text="Machine Wash Cold")
        ])
        res = self.stage6.process_from_stages(stage4_output=s4, stage3_output=s3)
        profile = res.products[0]
        self.assertIn(profile.product_profile.category, ["GARMENT", "TEXTILE"])
        fields_dict = {f.field_name: f for f in profile.adaptive_schema.fields}
        self.assertEqual(fields_dict["FABRIC_COMPOSITION"].status, "PRESENT")

    # ----------------------------------------------------
    # TEST 6: Footwear
    # ----------------------------------------------------
    def test_06_shoes(self):
        """6. Shoes: FOOTWEAR category."""
        s4 = self._create_mock_stage4_output("PRO RUNNER SNEAKERS", "STRIDE", "FOOTWEAR")
        s3 = self._create_mock_stage3_output([
            Stage3SemanticField(field_id="f1", semantic_type="FOOTWEAR_SIZE", value="UK 8", raw_text="Size: UK 8"),
            Stage3SemanticField(field_id="f2", semantic_type="UPPER_MATERIAL", value="Synthetic Mesh", raw_text="Upper: Mesh")
        ])
        res = self.stage6.process_from_stages(stage4_output=s4, stage3_output=s3)
        profile = res.products[0]
        self.assertEqual(profile.product_profile.category, "FOOTWEAR")

    # ----------------------------------------------------
    # TEST 7: Toy
    # ----------------------------------------------------
    def test_07_toy(self):
        """7. Toy: TOYS category with age/warning fields."""
        s4 = self._create_mock_stage4_output("SUPER ROBOT ACTION FIGURE", "PLAYFUN", "TOYS")
        s3 = self._create_mock_stage3_output([
            Stage3SemanticField(field_id="f1", semantic_type="AGE_RANGE", value="Age 3+", raw_text="For Ages 3+"),
            Stage3SemanticField(field_id="f2", semantic_type="CHOKING_WARNING", value="Choking hazard small parts", raw_text="Warning: Small Parts")
        ])
        res = self.stage6.process_from_stages(stage4_output=s4, stage3_output=s3)
        profile = res.products[0]
        self.assertEqual(profile.product_profile.category, "TOYS")

    # ----------------------------------------------------
    # TEST 8: Stationery
    # ----------------------------------------------------
    def test_08_stationery(self):
        """8. Stationery: STATIONERY category."""
        s4 = self._create_mock_stage4_output("EXECUTIVE SPIRAL NOTEBOOK 200 PAGES", "NOTEPRO", "STATIONERY")
        res = self.stage6.process_from_stages(stage4_output=s4)
        profile = res.products[0]
        self.assertEqual(profile.product_profile.category, "STATIONERY")

    # ----------------------------------------------------
    # TEST 9: Hardware Tool
    # ----------------------------------------------------
    def test_09_hardware_tool(self):
        """9. Hardware tool: HARDWARE / TOOLS category."""
        s4 = self._create_mock_stage4_output("CHROME VANADIUM SCREWDRIVER SET", "BUILDMASTER", "TOOLS")
        res = self.stage6.process_from_stages(stage4_output=s4)
        profile = res.products[0]
        self.assertIn(profile.product_profile.category, ["TOOLS", "HARDWARE"])

    # ----------------------------------------------------
    # TEST 10: Ambiguous Product
    # ----------------------------------------------------
    def test_10_ambiguous_product(self):
        """10. Ambiguous product: UNKNOWN or category candidates + NEEDS_REVIEW."""
        s4 = self._create_mock_stage4_output("GENERIC MULTIPURPOSE SOLUTION", "GENERIC BRAND", "UNKNOWN")
        s4.identity.category.value = "UNKNOWN"
        res = self.stage6.process_from_stages(stage4_output=s4)
        profile = res.products[0]
        self.assertIn(profile.product_profile.category_status, ["NEEDS_REVIEW", "UNCERTAIN"])

    # ----------------------------------------------------
    # TEST 11: Serving Size vs Net Qty ("50 g" under Serving Size)
    # ----------------------------------------------------
    def test_11_serving_size_differentiation(self):
        """11. '50 g' under Serving Size differentiates as SERVING_SIZE."""
        diff = self.differentiator.differentiate_quantity(
            raw_text="Serving Size: 50 g",
            value="50 g",
            unit="g",
            heading_text="Nutrition Facts",
            category="FOOD"
        )
        self.assertEqual(diff["differentiated_type"], "SERVING_SIZE")
        self.assertFalse(diff["is_net_quantity"])

    # ----------------------------------------------------
    # TEST 12: Net Quantity ("50 g" under Net Quantity)
    # ----------------------------------------------------
    def test_12_net_quantity_differentiation(self):
        """12. '50 g' under Net Quantity differentiates as NET_QUANTITY."""
        diff = self.differentiator.differentiate_quantity(
            raw_text="Net Qty: 50 g",
            value="50 g",
            unit="g",
            heading_text="Statutory Declarations",
            category="FOOD"
        )
        self.assertEqual(diff["differentiated_type"], "NET_QUANTITY")
        self.assertTrue(diff["is_net_quantity"])

    # ----------------------------------------------------
    # TEST 13: Technical Weight ("450 g" in electronics specs)
    # ----------------------------------------------------
    def test_13_technical_weight_electronics(self):
        """13. '450 g' under Weight in electronics specifications differentiates as TECHNICAL_WEIGHT."""
        diff = self.differentiator.differentiate_quantity(
            raw_text="Item Weight: 450 g",
            value="450 g",
            unit="g",
            heading_text="Technical Specifications",
            category="ELECTRONICS"
        )
        self.assertEqual(diff["differentiated_type"], "TECHNICAL_WEIGHT")
        self.assertFalse(diff["is_net_quantity"])

    # ----------------------------------------------------
    # TEST 14: Technical Dimension ("10 mm" in specs)
    # ----------------------------------------------------
    def test_14_technical_dimension(self):
        """14. '10 mm' in technical specifications differentiates as DIMENSION."""
        diff = self.differentiator.differentiate_quantity(
            raw_text="Driver Diameter: 10 mm",
            value="10 mm",
            unit="mm",
            heading_text="Specifications",
            category="ELECTRONICS"
        )
        self.assertIn(diff["differentiated_type"], ["DIMENSION", "TECHNICAL_SPECIFICATION"])
        self.assertFalse(diff["is_net_quantity"])

    # ----------------------------------------------------
    # TEST 15: Multiple Products in One Image
    # ----------------------------------------------------
    def test_15_multiple_products(self):
        """15. Multiple products in one image create separate product profiles."""
        p1 = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="ROYAL ALMONDS", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="FOOD", confidence=0.90)
        )
        p2 = Stage4ProductIdentity(
            product_name=Stage4ValueWithStatus(value="GLOWCARE SERUM", status="CONFIRMED", confidence=0.95),
            category=Stage4CategoryInfo(value="COSMETIC", confidence=0.90)
        )
        s4 = Stage4Response(
            scan_id="STAGE4-MULTI-001",
            identity_status="CONFIRMED",
            products=[p1, p2]
        )
        res = self.stage6.process_from_stages(stage4_output=s4)
        self.assertEqual(len(res.products), 2)
        self.assertEqual(res.products[0].product_id, "product_001")
        self.assertEqual(res.products[1].product_id, "product_002")
        self.assertEqual(res.products[0].product_profile.category, "FOOD")
        self.assertEqual(res.products[1].product_profile.category, "COSMETIC")

    # ----------------------------------------------------
    # TEST 16: Category-Specific Field Not Visible
    # ----------------------------------------------------
    def test_16_not_visible_field(self):
        """16. Category-specific field not present on image gets NOT_VISIBLE status."""
        s4 = self._create_mock_stage4_output("DELUXE ROYAL ALMONDS", "ROYAL NUTRIENTS", "FOOD")
        res = self.stage6.process_from_stages(stage4_output=s4)
        profile = res.products[0]
        fields_dict = {f.field_name: f for f in profile.adaptive_schema.fields}
        self.assertIn("NUTRITIONAL_INFORMATION", fields_dict)
        self.assertEqual(fields_dict["NUTRITIONAL_INFORMATION"].status, "NOT_VISIBLE")
        self.assertIsNone(fields_dict["NUTRITIONAL_INFORMATION"].value)

    # ----------------------------------------------------
    # TEST 17: Irrelevant Field Not Applicable
    # ----------------------------------------------------
    def test_17_not_applicable_field(self):
        """17. Irrelevant field for category gets NOT_APPLICABLE status or low relevance."""
        s4 = self._create_mock_stage4_output("DELUXE ROYAL ALMONDS", "ROYAL NUTRIENTS", "FOOD")
        res = self.stage6.process_from_stages(stage4_output=s4)
        profile = res.products[0]
        rel = self.relevance_engine.get_field_relevance("VOLTAGE", profile.product_profile.category)
        self.assertLess(rel, 0.15)

    # ----------------------------------------------------
    # TEST 18: Insufficient Category Evidence
    # ----------------------------------------------------
    def test_18_insufficient_category_evidence(self):
        """18. Low confidence category flags UNKNOWN / NEEDS_REVIEW."""
        s4 = self._create_mock_stage4_output("ITEM XYZ", "UNKNOWN BRAND", "UNKNOWN")
        s4.identity.category.value = "UNKNOWN"
        res = self.stage6.process_from_stages(stage4_output=s4)
        profile = res.products[0]
        self.assertIn(profile.product_profile.category_status, ["NEEDS_REVIEW", "UNCERTAIN"])


if __name__ == "__main__":
    unittest.main()
