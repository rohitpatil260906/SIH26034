"""
LM-COMPASS Stage 4 Automated Regression Test Suite
==================================================
Tests Universal Product, Company, and Entity Identification across all mandatory scenarios:
- TEST 1: Front panel with brand + product.
- TEST 2: Back panel containing manufacturer + address + PIN.
- TEST 3: Back panel without product name (manufacturer identified, product_name = NOT_VISIBLE).
- TEST 4: Side panel containing importer + model + country of origin.
- TEST 5: Partial company name (partial_entity = True, no hallucination).
- TEST 6: Brand and manufacturer are different (strictly separate entities).
- TEST 7: Manufacturer and marketer are different (strictly separate roles).
- TEST 8: Unreadable OCR company text (filtered by anti-garbage, status = UNCERTAIN / NEEDS_REVIEW).
- TEST 9: Multiple products in one image (separate product_001 and product_002 identities).
- TEST 10: Barcode present but company text absent (supporting evidence only, no fabricated company).
- TEST 11: Country of origin explicitly visible (Made in India -> country correctly extracted).
- TEST 12: Batch number and model number both visible (strictly separate fields).
- TEST 13: End-to-end pipeline execution from raw image bytes through Stages 1, 2, 3, and 4.
"""

import io
import os
import sys
import unittest
from PIL import Image, ImageDraw

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models import (
    Stage1Response,
    Stage1PanelInfo,
    Stage2Response,
    Stage2TextRegion,
    Stage2BarcodeRegion,
    Stage3Response,
    Stage3SemanticField,
    Stage3CategoryCandidate,
    Stage4Response
)
from backend.services.stage4_identity import Stage4Pipeline


def make_s2_region(reg_id: str, text: str, bbox=None, order=1):
    """Helper to create a Stage2TextRegion object."""
    b = bbox or [50.0, float(order * 30), 300.0, 25.0]
    return Stage2TextRegion(
        region_id=reg_id,
        raw_text=text,
        normalized_text=text,
        bbox=b,
        original_bbox=b,
        ocr_confidence=0.95,
        reading_order_index=order,
        status="DETECTED"
    )


class TestStage4IdentityPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = Stage4Pipeline()

    def test_01_front_panel_brand_and_product(self):
        """TEST 1: Front panel with brand + product name."""
        lines = [
            make_s2_region("R1", "GlowCare", bbox=[100.0, 50.0, 200.0, 35.0], order=1),
            make_s2_region("R2", "Vitamin C Face Serum", bbox=[100.0, 95.0, 350.0, 30.0], order=2)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST01", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertEqual(res.identity_status, "CONFIRMED")
        self.assertEqual(res.identity.brand.value, "GlowCare")
        self.assertEqual(res.identity.brand.status, "CONFIRMED")
        self.assertEqual(res.identity.product_name.value, "Vitamin C Face Serum")
        self.assertEqual(res.identity.product_name.status, "CONFIRMED")

    def test_02_back_panel_manufacturer_address_pin(self):
        """TEST 2: Back panel containing manufacturer + address + PIN."""
        lines = [
            make_s2_region("R1", "Manufactured By: XYZ Foods Pvt Ltd", order=1),
            make_s2_region("R2", "Plot 12, Industrial Area, Pune, Maharashtra", order=2),
            make_s2_region("R3", "PIN - 411001", order=3)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST02", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertGreaterEqual(len(res.identity.entities), 1)
        mfg = next((e for e in res.identity.entities if e.role == "MANUFACTURER"), None)
        self.assertIsNotNone(mfg)
        self.assertTrue("XYZ Foods" in mfg.name)
        self.assertIsNotNone(mfg.address)
        self.assertTrue("Pune" in mfg.address)
        self.assertEqual(mfg.pin, "411001")

    def test_03_back_panel_without_product_name(self):
        """TEST 3: Back panel without product name -> manufacturer identified, product_name = NOT_VISIBLE."""
        lines = [
            make_s2_region("R1", "Manufactured By: Apex Confectionery Pvt Ltd", order=1),
            make_s2_region("R2", "Plot 45, GIDC Estate, Ahmedabad - 380015", order=2),
            make_s2_region("R3", "Net Qty: 100 g", order=3),
            make_s2_region("R4", "MRP: Rs. 40.00", order=4)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST03", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        # Manufacturer must be identified
        mfg = next((e for e in res.identity.entities if e.role == "MANUFACTURER"), None)
        self.assertIsNotNone(mfg)
        self.assertTrue("Apex Confectionery" in mfg.name)

        # Product name must be NOT_VISIBLE, NOT failing the process
        self.assertEqual(res.identity.product_name.status, "NOT_VISIBLE")
        self.assertEqual(res.identity.product_name.value, "NOT_VISIBLE")
        self.assertEqual(res.identity_status, "CONFIRMED")

    def test_04_side_panel_importer_model_country(self):
        """TEST 4: Side panel containing importer + model + country."""
        lines = [
            make_s2_region("R1", "Imported By: ABC Electronics Pvt Ltd", order=1),
            make_s2_region("R2", "Model: XYZ-200", order=2),
            make_s2_region("R3", "Country of Origin: China", order=3)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST04", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        imp = next((e for e in res.identity.entities if e.role == "IMPORTER"), None)
        self.assertIsNotNone(imp)
        self.assertTrue("ABC Electronics" in imp.name)
        self.assertEqual(res.identity.model_number, "XYZ-200")
        self.assertEqual(res.identity.country_of_origin, "China")

    def test_05_partial_company_name(self):
        """TEST 5: Partial company name -> PARTIAL, no hallucination."""
        lines = [
            make_s2_region("R1", "Manufactured By: ...Consumer Products Pvt Ltd", order=1)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST05", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertGreaterEqual(len(res.identity.entities), 1)
        ent = res.identity.entities[0]
        self.assertTrue(ent.partial_entity)
        self.assertTrue("Consumer Products" in ent.name)
        # Verify it did not invent a prefix
        self.assertFalse(ent.name.startswith("ABC"))
        self.assertFalse(ent.name.startswith("XYZ"))

    def test_06_brand_and_manufacturer_different(self):
        """TEST 6: Brand and manufacturer are different -> separate entities."""
        lines = [
            make_s2_region("R1", "Brand: PureBake", bbox=[50.0, 50.0, 150.0, 25.0], order=1),
            make_s2_region("R2", "Manufactured By: Golden Foods Pvt Ltd", bbox=[50.0, 90.0, 300.0, 25.0], order=2)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST06", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertEqual(res.identity.brand.value, "PureBake")
        mfg = next((e for e in res.identity.entities if e.role == "MANUFACTURER"), None)
        self.assertIsNotNone(mfg)
        self.assertTrue("Golden Foods" in mfg.name)
        self.assertNotEqual(res.identity.brand.value, mfg.name)

    def test_07_separate_manufacturer_and_marketer(self):
        """TEST 7: Manufacturer and marketer are different -> separate roles."""
        lines = [
            make_s2_region("R1", "Manufactured By: ABC Pharma Pvt Ltd", order=1),
            make_s2_region("R2", "Marketed By: DEF Consumer Products Ltd", order=2)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST07", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        roles = [e.role for e in res.identity.entities]
        self.assertIn("MANUFACTURER", roles)
        self.assertIn("MARKETER", roles)
        mfg = next(e for e in res.identity.entities if e.role == "MANUFACTURER")
        mkt = next(e for e in res.identity.entities if e.role == "MARKETER")
        self.assertTrue("ABC Pharma" in mfg.name)
        self.assertTrue("DEF Consumer" in mkt.name)

    def test_08_unreadable_ocr_company_text(self):
        """TEST 8: Unreadable OCR company text -> IDENTITY_UNCERTAIN or NEEDS_REVIEW."""
        lines = [
            make_s2_region("R1", "AKMI 0| HA", order=1),
            make_s2_region("R2", "- a — pe—— -", order=2),
            make_s2_region("R3", "Xx_9@@", order=3)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST08", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertIn(res.identity_status, ["NEEDS_REVIEW", "UNCERTAIN"])
        # Must not fabricate a company name out of garbage
        self.assertEqual(len(res.identity.entities), 0)

    def test_09_multiple_products_in_one_image(self):
        """TEST 9: Multiple products in one image -> separate product_001 and product_002 identities."""
        # Product 1 on Left: x=50..250
        # Product 2 on Right: x=550..750
        lines = [
            make_s2_region("L1", "Product A Biscuits", bbox=[50.0, 50.0, 200.0, 25.0], order=1),
            make_s2_region("L2", "Manufactured By: Left Foods Pvt Ltd", bbox=[50.0, 85.0, 250.0, 25.0], order=2),
            make_s2_region("R1", "Product B Chips", bbox=[550.0, 50.0, 200.0, 25.0], order=3),
            make_s2_region("R2", "Manufactured By: Right Snacks Pvt Ltd", bbox=[550.0, 85.0, 250.0, 25.0], order=4)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST09", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertGreaterEqual(len(res.products), 2)
        self.assertEqual(res.products[0].product_id, "product_001")
        self.assertEqual(res.products[1].product_id, "product_002")

    def test_10_barcode_present_without_company_text(self):
        """TEST 10: Barcode present but company text absent -> supporting evidence only."""
        lines = [
            make_s2_region("R1", "DELUXE PREMIUM COOKIES", order=1)
        ]
        barcodes = [
            Stage2BarcodeRegion(
                barcode_id="BC-1",
                format="EAN_13",
                decoded_data="8901030383748",
                confidence=0.98
            )
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST10", regions=lines, barcode_regions=barcodes)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertEqual(res.identity.barcode_value, "8901030383748")
        self.assertEqual(res.identity.barcode_type, "EAN_13")
        # No company was fabricated
        self.assertEqual(len(res.identity.entities), 0)

    def test_11_country_of_origin_explicit(self):
        """TEST 11: Country of origin explicitly visible -> correctly extracted."""
        lines = [
            make_s2_region("R1", "Made in India", order=1)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST11", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertEqual(res.identity.country_of_origin, "India")

    def test_12_batch_and_model_number_segregation(self):
        """TEST 12: Batch number and model number both visible -> kept strictly separate."""
        lines = [
            make_s2_region("R1", "Model: MD-500", order=1),
            make_s2_region("R2", "Batch: BATCH-889", order=2)
        ]
        s2 = Stage2Response(scan_id="STAGE2-TEST12", regions=lines)
        s3 = self.pipeline.stage3_pipeline.process_stage2_output(s2)
        res = self.pipeline.process_stage3_output(s3, s2)

        self.assertEqual(res.identity.model_number, "MD-500")
        self.assertEqual(res.identity.batch_number, "BATCH-889")
        self.assertNotEqual(res.identity.model_number, res.identity.batch_number)

    def test_13_end_to_end_image_pipeline(self):
        """TEST 13: End-to-end pipeline execution from raw image bytes through Stages 1, 2, 3, and 4."""
        w, h = 800, 600
        img = Image.new("RGB", (w, h), (210, 210, 210))
        draw = ImageDraw.Draw(img)
        draw.rectangle([80, 50, 720, 550], fill=(255, 255, 255), outline=(0, 0, 0), width=3)

        lines = [
            "HERBAL SHAMPOO",
            "Net Volume: 200 ml",
            "MRP: Rs. 149.00",
            "Manufactured By: Green Herbal Care Pvt Ltd",
            "Plot 10, Sector 4, Gurugram, Haryana - 122001",
            "Country of Origin: India"
        ]
        curr_y = 80
        for line in lines:
            draw.text((120, curr_y), line, fill=(0, 0, 0))
            curr_y += 50

        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

        # Execute full Stage 1-4 pipeline
        res = self.pipeline.process_image_bytes(image_bytes)

        self.assertIsNotNone(res)
        self.assertTrue(res.scan_id.startswith("STAGE4-"))
        self.assertEqual(res.identity_status, "CONFIRMED")
        self.assertGreaterEqual(len(res.identity.entities), 1)

        mfg = next((e for e in res.identity.entities if e.role == "MANUFACTURER"), None)
        self.assertIsNotNone(mfg)
        self.assertTrue("Green Herbal Care" in mfg.name)
        self.assertEqual(mfg.pin, "122001")
        self.assertEqual(res.identity.country_of_origin, "India")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage4IdentityPipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
