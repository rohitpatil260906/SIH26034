"""
LM-COMPASS Stage 3 Automated Regression Test Suite
==================================================
Tests Universal Text Meaning & Semantic Understanding across all mandatory scenarios:
- TEST 1: "Net Quantity 50 g" -> NET_QUANTITY = 50 g
- TEST 2: "Serving Size 50 g" -> SERVING_SIZE = 50 g
- TEST 3: "Ingredients: Vitamin C 50 mg" -> INGREDIENTS section, Vitamin C 50 mg is ingredient info, NOT NET_QUANTITY
- TEST 4: "MRP ₹299" -> MRP = ₹299
- TEST 5: "₹299" alone -> PRICE_CANDIDATE or UNKNOWN (NEEDS_REVIEW)
- TEST 6: "Ingredients: Water, Glycerin, Niacinamide" -> INGREDIENTS, NOT ADDRESS
- TEST 7: "Marketed By ABC Pvt Ltd" -> MARKETER_NAME = ABC Pvt Ltd
- TEST 8: "Manufactured By XYZ Foods Pvt Ltd" -> MANUFACTURER_NAME = XYZ Foods Pvt Ltd
- TEST 9: "Best Before 24 Months" -> BEST_BEFORE_DATE / SHELF_LIFE
- TEST 10: "10 mm" -> DIMENSION / TECHNICAL_SPECIFICATION if context supports it
- TEST 11: "400013" alone -> NOT automatically classified as PIN without address context
- TEST 12: Back-panel image only -> Functions without requiring front PDP
- TEST 13: Table understanding: "Serving Size | 50 g" -> SERVING_SIZE, NOT NET_QUANTITY
- TEST 14: Separate Manufacturer & Packer on same package
- TEST 15: Strict No-Hallucination Policy
"""

import io
import os
import sys
import unittest
from PIL import Image, ImageDraw

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models import (
    Stage2Response,
    Stage2TextRegion,
    Stage2WordBox,
    Stage2TableInfo,
    Stage2TableCell
)
from backend.services.stage3_semantic import Stage3Pipeline


def make_stage2_region(reg_id: str, text: str, bbox=None, conf=0.95, order=1):
    """Helper to create a Stage2TextRegion object."""
    b = bbox or [50.0, float(order * 30), 200.0, 20.0]
    return Stage2TextRegion(
        region_id=reg_id,
        raw_text=text,
        normalized_text=text,
        bbox=b,
        original_bbox=b,
        detection_confidence=0.95,
        ocr_confidence=conf,
        status="DETECTED",
        reading_order_index=order
    )


class TestStage3SemanticPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = Stage3Pipeline()

    def test_01_net_quantity_context(self):
        """TEST 1: 'Net Quantity 50 g' -> NET_QUANTITY = 50 g."""
        reg1 = make_stage2_region("R1", "Net Quantity: 50 g", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST1", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        net_fields = [f for f in res.semantic_fields if f.semantic_type == "NET_QUANTITY"]
        self.assertGreaterEqual(len(net_fields), 1)
        self.assertTrue("50 g" in net_fields[0].value or "50" in net_fields[0].value)
        self.assertEqual(net_fields[0].status, "CONFIRMED")

    def test_02_serving_size_context(self):
        """TEST 2: 'Serving Size 50 g' -> SERVING_SIZE = 50 g (NOT NET_QUANTITY)."""
        reg1 = make_stage2_region("R1", "Serving Size: 50 g", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST2", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        serving_fields = [f for f in res.semantic_fields if f.semantic_type == "SERVING_SIZE"]
        self.assertGreaterEqual(len(serving_fields), 1)
        self.assertTrue("50 g" in serving_fields[0].value or "50" in serving_fields[0].value)

        # Ensure it was NOT classified as NET_QUANTITY
        net_fields = [f for f in res.semantic_fields if f.semantic_type == "NET_QUANTITY"]
        self.assertEqual(len(net_fields), 0)

    def test_03_ingredient_quantity_shielding(self):
        """TEST 3: 'Ingredients: Vitamin C 50 mg' -> INGREDIENTS section, Vitamin C 50 mg is ingredient info, NOT NET_QUANTITY."""
        reg1 = make_stage2_region("R1", "Ingredients: Refined Flour, Vitamin C 50 mg, Cocoa", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST3", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        # Must NOT be classified as NET_QUANTITY
        net_fields = [f for f in res.semantic_fields if f.semantic_type == "NET_QUANTITY"]
        self.assertEqual(len(net_fields), 0)

        # Must be recognized in INGREDIENTS
        ing_fields = [f for f in res.semantic_fields if f.semantic_type in ("INGREDIENTS", "INGREDIENT_QUANTITY")]
        self.assertGreaterEqual(len(ing_fields), 1)

    def test_04_mrp_explicit_context(self):
        """TEST 4: 'MRP ₹299' -> MRP = ₹299."""
        reg1 = make_stage2_region("R1", "MRP: ₹299.00 (Incl. of all taxes)", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST4", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        mrp_fields = [f for f in res.semantic_fields if f.semantic_type == "MRP"]
        self.assertGreaterEqual(len(mrp_fields), 1)
        self.assertTrue("299" in mrp_fields[0].value)
        self.assertEqual(mrp_fields[0].status, "CONFIRMED")

    def test_05_isolated_price_candidate(self):
        """TEST 5: '₹299' alone -> PRICE_CANDIDATE or UNKNOWN if context is insufficient (NEEDS_REVIEW)."""
        reg1 = make_stage2_region("R1", "₹299", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST5", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        # Must NOT automatically declare CONFIRMED MRP
        confirmed_mrp = [f for f in res.semantic_fields if f.semantic_type == "MRP" and f.status == "CONFIRMED"]
        self.assertEqual(len(confirmed_mrp), 0)

        # Must be present in ambiguous_fields or candidate types
        all_fields = res.semantic_fields + res.ambiguous_fields
        price_items = [f for f in all_fields if "299" in f.value]
        self.assertGreaterEqual(len(price_items), 1)
        self.assertEqual(price_items[0].status, "NEEDS_REVIEW")

    def test_06_ingredients_not_address(self):
        """TEST 6: 'Ingredients: Water, Glycerin, Niacinamide' -> INGREDIENTS, NOT ADDRESS."""
        reg1 = make_stage2_region("R1", "Ingredients: Water, Glycerin, Niacinamide, Vitamin E", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST6", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        # Must NOT be classified as ADDRESS or MANUFACTURER_ADDRESS
        addr_fields = [f for f in res.semantic_fields if "ADDRESS" in f.semantic_type]
        self.assertEqual(len(addr_fields), 0)

        # Must be classified as INGREDIENTS
        ing_fields = [f for f in res.semantic_fields if f.semantic_type == "INGREDIENTS"]
        self.assertGreaterEqual(len(ing_fields), 1)

    def test_07_marketed_by_entity(self):
        """TEST 7: 'Marketed By ABC Pvt Ltd' -> MARKETER_NAME = ABC Pvt Ltd."""
        reg1 = make_stage2_region("R1", "Marketed By: ABC Consumer Products Pvt Ltd", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST7", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        mkt_fields = [f for f in res.semantic_fields if f.semantic_type == "MARKETER_NAME"]
        self.assertGreaterEqual(len(mkt_fields), 1)
        self.assertTrue("ABC" in mkt_fields[0].value)

    def test_08_manufactured_by_entity(self):
        """TEST 8: 'Manufactured By XYZ Foods Pvt Ltd' -> MANUFACTURER_NAME = XYZ Foods Pvt Ltd."""
        reg1 = make_stage2_region("R1", "Manufactured By: XYZ Foods Pvt Ltd", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST8", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        mfg_fields = [f for f in res.semantic_fields if f.semantic_type == "MANUFACTURER_NAME"]
        self.assertGreaterEqual(len(mfg_fields), 1)
        self.assertTrue("XYZ" in mfg_fields[0].value)

    def test_09_best_before_shelf_life(self):
        """TEST 9: 'Best Before 24 Months' -> BEST_BEFORE_DATE / SHELF_LIFE."""
        reg1 = make_stage2_region("R1", "Best Before 24 Months from Packaging", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST9", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        self.assertEqual(res.semantic_status, "COMPLETED")

        date_fields = [f for f in res.semantic_fields if f.semantic_type == "BEST_BEFORE_DATE"]
        self.assertGreaterEqual(len(date_fields), 1)
        self.assertTrue("24 Months" in date_fields[0].value or "24" in date_fields[0].value)

    def test_10_dimension_understanding(self):
        """TEST 10: '10 mm' -> DIMENSION / TECHNICAL_SPECIFICATION if context supports it."""
        # Case A: With technical context
        reg1 = make_stage2_region("R1", "Adapter Plug Thickness: 10 mm", order=1)
        s2_a = Stage2Response(scan_id="STAGE2-TEST10A", regions=[reg1])
        res_a = self.pipeline.process_stage2_output(s2_a)
        tech_fields = [f for f in res_a.semantic_fields if f.semantic_type in ("DIMENSION", "TECHNICAL_SPECIFICATION")]
        self.assertGreaterEqual(len(tech_fields), 1)

        # Case B: Alone without context -> marked UNKNOWN / NEEDS_REVIEW
        reg2 = make_stage2_region("R2", "10 mm", order=1)
        s2_b = Stage2Response(scan_id="STAGE2-TEST10B", regions=[reg2])
        res_b = self.pipeline.process_stage2_output(s2_b)
        all_b = res_b.semantic_fields + res_b.ambiguous_fields
        dim_items = [f for f in all_b if "10 mm" in f.value]
        self.assertGreaterEqual(len(dim_items), 1)
        self.assertEqual(dim_items[0].status, "NEEDS_REVIEW")

    def test_11_postal_pin_strict_context(self):
        """TEST 11: '400013' alone -> do NOT automatically classify as PIN without address context."""
        reg1 = make_stage2_region("R1", "400013", order=1)
        s2 = Stage2Response(scan_id="STAGE2-TEST11", regions=[reg1])

        res = self.pipeline.process_stage2_output(s2)
        # Must NOT be a confirmed POSTAL_PIN
        confirmed_pin = [f for f in res.semantic_fields if f.semantic_type == "POSTAL_PIN" and f.status == "CONFIRMED"]
        self.assertEqual(len(confirmed_pin), 0)

        # Case B: Supported by address context
        reg_addr = make_stage2_region("R2", "Mumbai - 400013, Maharashtra", order=1)
        s2_addr = Stage2Response(scan_id="STAGE2-TEST11B", regions=[reg_addr])
        res_addr = self.pipeline.process_stage2_output(s2_addr)
        addr_fields = [f for f in res_addr.semantic_fields if "ADDRESS" in f.semantic_type or f.semantic_type == "POSTAL_PIN"]
        self.assertGreaterEqual(len(addr_fields), 1)

    def test_12_back_panel_only(self):
        """TEST 12: Back-panel image only -> semantic understanding functions without front PDP."""
        lines = [
            make_stage2_region("R1", "NUTRITIONAL FACTS PER 100g", order=1),
            make_stage2_region("R2", "Ingredients: Wheat, Sugar, Salt", order=2),
            make_stage2_region("R3", "Manufactured By: Baker Foods Ltd", order=3),
            make_stage2_region("R4", "Plot 5, Industrial Area, Pune - 411001", order=4),
            make_stage2_region("R5", "Consumer Care: care@bakerfoods.com", order=5)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST12", regions=lines)
        res = self.pipeline.process_stage2_output(s2)

        self.assertEqual(res.semantic_status, "COMPLETED")
        self.assertGreaterEqual(len(res.sections), 2)
        self.assertGreaterEqual(len(res.semantic_fields), 3)

    def test_13_table_understanding_serving_size(self):
        """TEST 13: Table structure 'Serving Size | 50 g' -> SERVING_SIZE, NOT NET_QUANTITY."""
        cell0 = Stage2TableCell(row_index=0, col_index=0, row_span=1, col_span=1, text="Serving Size", bbox=[10, 10, 50, 20])
        cell1 = Stage2TableCell(row_index=0, col_index=1, row_span=1, col_span=1, text="50 g", bbox=[60, 10, 50, 20])
        table = Stage2TableInfo(table_id="TBL-01", bbox=[10, 10, 100, 30], rows_count=1, cols_count=2, cells=[cell0, cell1])

        s2 = Stage2Response(scan_id="STAGE2-TEST13", tables=[table])
        res = self.pipeline.process_stage2_output(s2)

        serving_fields = [f for f in res.semantic_fields if f.semantic_type == "SERVING_SIZE"]
        self.assertGreaterEqual(len(serving_fields), 1)
        self.assertEqual(serving_fields[0].value, "50 g")

        # Must NOT be NET_QUANTITY
        net_fields = [f for f in res.semantic_fields if f.semantic_type == "NET_QUANTITY"]
        self.assertEqual(len(net_fields), 0)

    def test_14_separate_mfg_and_packer(self):
        """TEST 14: Both Manufacturer and Packer on same package must be kept distinct."""
        lines = [
            make_stage2_region("R1", "Manufactured By: Golden Bakery Pvt Ltd", order=1),
            make_stage2_region("R2", "Packed By: Express Logistics Ltd", order=2)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST14", regions=lines)
        res = self.pipeline.process_stage2_output(s2)

        mfg_fields = [f for f in res.semantic_fields if f.semantic_type == "MANUFACTURER_NAME"]
        pkd_fields = [f for f in res.semantic_fields if f.semantic_type == "PACKER_NAME"]

        self.assertGreaterEqual(len(mfg_fields), 1)
        self.assertGreaterEqual(len(pkd_fields), 1)
        self.assertTrue("Golden Bakery" in mfg_fields[0].value)
        self.assertTrue("Express Logistics" in pkd_fields[0].value)

    def test_15_no_hallucination_guarantee(self):
        """TEST 15: No-hallucination guarantee: Missing fields are never fabricated."""
        lines = [
            make_stage2_region("R1", "PRODUCT NAME ONLY", order=1)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST15", regions=lines)
        res = self.pipeline.process_stage2_output(s2)

        # There is no MRP, no Net Qty, no Manufacturer in input
        mrp_fields = [f for f in res.semantic_fields if f.semantic_type == "MRP"]
        qty_fields = [f for f in res.semantic_fields if f.semantic_type == "NET_QUANTITY"]
        mfg_fields = [f for f in res.semantic_fields if f.semantic_type == "MANUFACTURER_NAME"]

        self.assertEqual(len(mrp_fields), 0)
        self.assertEqual(len(qty_fields), 0)
        self.assertEqual(len(mfg_fields), 0)

    def test_16_end_to_end_image_pipeline(self):
        """TEST 16: End-to-end pipeline execution from raw image bytes through Stage 1, Stage 2, and Stage 3."""
        w, h = 800, 600
        img = Image.new("RGB", (w, h), (200, 200, 200))
        draw = ImageDraw.Draw(img)
        # Draw box
        draw.rectangle([80, 50, 720, 550], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
        
        lines = [
            "HERBAL SHAMPOO",
            "Net Volume: 200 ml",
            "MRP: Rs. 149.00",
            "Best Before 24 Months",
            "Manufactured By: Green Herbal Care Pvt Ltd"
        ]
        curr_y = 80
        for line in lines:
            draw.text((120, curr_y), line, fill=(0, 0, 0))
            curr_y += 50

        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

        # Run complete pipeline
        res = self.pipeline.process_image_bytes(image_bytes)

        self.assertIsNotNone(res)
        self.assertTrue(res.scan_id.startswith("STAGE3-"))
        self.assertIn(res.semantic_status, ["COMPLETED", "NEEDS_REVIEW"])
        self.assertGreaterEqual(len(res.semantic_fields), 2)

        # Check detected fields
        field_types = {f.semantic_type for f in res.semantic_fields}
        self.assertTrue(any(t in field_types for t in ["NET_QUANTITY", "MRP", "MANUFACTURER_NAME", "SHELF_LIFE", "BEST_BEFORE_DATE"]))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage3SemanticPipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

