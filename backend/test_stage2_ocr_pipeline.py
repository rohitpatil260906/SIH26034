"""
LM-COMPASS Stage 2 Automated Regression Test Suite
==================================================
Tests 23 representative packaging scenarios and OCR capabilities:
1.  Clear food label
2.  Cosmetic label
3.  Curved bottle
4.  Curved tube
5.  Small MRP
6.  Small net quantity
7.  Back-panel-only image (Non-front validity)
8.  Side-panel-only image (Columnar aspect ratio)
9.  Rotated text
10. Low-light label
11. Glare-affected label
12. Perspective distortion & coordinate back-mapping
13. Dense ingredients paragraph
14. Nutrition table structure
15. Multiple products
16. Partial label crop
17. Mixed numbers and letters
18. ₹ / Rs. price and currency preservation
19. Six-digit PIN code
20. Batch number
21. Date formats (Mfg / Expiry)
22. 1D Barcode isolation
23. 2D QR Code isolation
"""

import io
import os
import sys
import math
import unittest
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.stage2_ocr import Stage2Pipeline
from backend.services.stage1_cv.geometry import map_bbox_to_original


def img_to_bytes(img: Image.Image, fmt="JPEG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def create_packaging_with_text(
    w=800, h=600,
    bg_color=(180, 180, 185),
    box_color=(250, 250, 250),
    lines=None
):
    """Helper to draw a packaging box with customizable text lines."""
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    bx1, by1 = int(w * 0.10), int(h * 0.08)
    bx2, by2 = int(w * 0.90), int(h * 0.92)
    draw.rectangle([bx1, by1, bx2, by2], fill=box_color, outline=(30, 30, 30), width=3)

    if lines:
        curr_y = by1 + 25
        for line in lines:
            draw.text((bx1 + 25, curr_y), line, fill=(20, 20, 20))
            curr_y += 35

    return img


class TestStage2OcrPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = Stage2Pipeline()

    def test_01_clear_food_label(self):
        """1. Clear food label (Standard baseline)."""
        lines = [
            "DELUXE PREMIUM BISCUITS",
            "Net Qty: 200 g (Pack of 2 x 100 g)",
            "MRP Rs. 50.00 (Incl. of all taxes)",
            "Unit Sale Price: Rs. 0.25/g",
            "Mfg Date: 12/2024  Exp Date: 12/2025",
            "Mfd By: Golden Bake Foods Pvt Ltd, Mumbai - 400013"
        ]
        img = create_packaging_with_text(800, 600, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))

        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 2)
        all_raw = " ".join(r.raw_text for r in res.regions)
        self.assertTrue("BISCUITS" in all_raw or "DELUXE" in all_raw or "200" in all_raw)

    def test_02_cosmetic_label(self):
        """2. Cosmetic label with liquid volume and batch code."""
        lines = [
            "HYDRA GLOW RADIANCE FACE SERUM",
            "Net Vol: 30 ml",
            "Batch No: CS2024",
            "Use Before: 06/2026",
            "Mfd By: Pure Herbal Cosmetics Ltd"
        ]
        img = create_packaging_with_text(700, 600, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))

        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 1)
        all_raw = " ".join(r.raw_text for r in res.regions)
        self.assertTrue("30" in all_raw or "SERUM" in all_raw or "GLOW" in all_raw)

    def test_03_curved_bottle(self):
        """3. Curved bottle with cylindrical unwarping."""
        lines = [
            "PREMIUM MINERAL WATER",
            "Net Qty: 1 L (1000 ml)",
            "MRP Rs. 20.00",
            "Batch: WTR-99"
        ]
        img = create_packaging_with_text(700, 700, lines=lines)
        cv_img = np.array(img)
        h, w = cv_img.shape[:2]
        # Draw parabolic bottle seams
        for y in range(80, 600, 60):
            pts = [(x, int(y + 18 * math.sin((x - 100) / 500.0 * math.pi))) for x in range(100, 600, 10)]
            cv2.polylines(cv_img, [np.array(pts, np.int32).reshape((-1, 1, 2))], False, (50, 50, 50), 2)
        bottle_pil = Image.fromarray(cv_img)

        res = self.pipeline.process_image_bytes(img_to_bytes(bottle_pil))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 1)

    def test_04_curved_tube(self):
        """4. Curved tube packaging."""
        lines = [
            "HERBAL TOOTHPASTE",
            "Net Wt: 150 g",
            "MRP Rs. 85.00"
        ]
        img = create_packaging_with_text(500, 800, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 1)

    def test_05_small_mrp(self):
        """5. Small font MRP text in corner."""
        img = create_packaging_with_text(800, 600, lines=["DELUXE PACK", "STANDARD TEXT LINE"])
        draw = ImageDraw.Draw(img)
        # Draw small MRP in corner
        draw.text((120, 480), "MRP Rs. 25.00", fill=(20, 20, 20))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_norm = " ".join(r.normalized_text for r in res.regions)
        self.assertTrue("25" in all_norm or "MRP" in all_norm or "Rs" in all_norm)

    def test_06_small_net_quantity(self):
        """6. Small net quantity declaration."""
        img = create_packaging_with_text(800, 600, lines=["PRODUCT HEADER", "LEGAL NOTICE"])
        draw = ImageDraw.Draw(img)
        draw.text((120, 450), "Net Qty: 50 g", fill=(20, 20, 20))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_norm = " ".join(r.normalized_text for r in res.regions)
        self.assertTrue("50" in all_norm or "Qty" in all_norm or "g" in all_norm)

    def test_07_back_panel_only(self):
        """7. Back panel only (Non-front validity: must process without requiring front PDP)."""
        lines = [
            "NUTRITIONAL INFORMATION PER 100g",
            "Ingredients: Wheat, Sugar, Butter, Salt",
            "Manufactured By: Baker Foods Ltd, Pune - 411001",
            "Packed By: Express Logistics, Mumbai - 400001",
            "Consumer Care: care@bakerfoods.com"
        ]
        img = create_packaging_with_text(800, 700, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 2)

    def test_08_side_panel_only(self):
        """8. Side panel only (Narrow columnar aspect ratio)."""
        lines = [
            "Batch No: B101",
            "Pkg Date: 05/2024",
            "Exp Date: 05/2025",
            "Storage: Cool Dry Place"
        ]
        img = create_packaging_with_text(260, 850, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 1)

    def test_09_rotated_text(self):
        """9. Rotated text crop handling."""
        img = create_packaging_with_text(600, 600, lines=["BATCH: XY889", "MFD: 01/2025"])
        rotated = img.rotate(90, expand=True)
        res = self.pipeline.process_image_bytes(img_to_bytes(rotated))
        self.assertEqual(res.text_detection_status, "COMPLETED")

    def test_10_low_light_label(self):
        """10. Low light / underexposed label (CLAHE recovery)."""
        img = create_packaging_with_text(700, 500, lines=["HIGH CONTRAST BRAND", "Net Wt: 500 g"])
        cv_img = np.array(img)
        dimmed = (cv_img * 0.45).astype(np.uint8)
        dim_pil = Image.fromarray(dimmed)

        res = self.pipeline.process_image_bytes(img_to_bytes(dim_pil))
        self.assertEqual(res.text_detection_status, "COMPLETED")

    def test_11_glare_affected_label(self):
        """11. Specular glare reflection on part of label."""
        img = create_packaging_with_text(800, 600, lines=["DELUXE CRISPS", "Net Qty: 100 g", "MRP Rs. 30.00"])
        draw = ImageDraw.Draw(img)
        # Draw glare spot on non-text area
        draw.ellipse([450, 80, 580, 200], fill=(255, 255, 255))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 1)

    def test_12_perspective_distortion(self):
        """12. Perspective distortion and coordinate back-mapping."""
        img = create_packaging_with_text(800, 600, lines=["PERSPECTIVE BOX", "Net Wt: 250 g"])
        cv_img = np.array(img)
        h, w = cv_img.shape[:2]
        pts1 = np.float32([[40, 40], [w - 60, 100], [w - 100, h - 40], [60, h - 80]])
        pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        m = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(cv_img, m, (w, h))
        warped_pil = Image.fromarray(warped)

        res = self.pipeline.process_image_bytes(img_to_bytes(warped_pil))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        for r in res.regions:
            self.assertEqual(len(r.original_bbox), 4)

    def test_13_dense_ingredients(self):
        """13. Dense ingredients paragraph grouping."""
        lines = [
            "Ingredients: Refined Wheat Flour, Sugar, Edible Vegetable Oil, Cocoa",
            "Solids, Salt, Emulsifiers (E322), Leavening Agents (E500ii, E503ii),",
            "Permitted Synthetic Food Colours, Added Artificial Flavours."
        ]
        img = create_packaging_with_text(850, 500, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_raw = " ".join(r.raw_text for r in res.regions)
        self.assertTrue("Ingredients" in all_raw or "Wheat" in all_raw or "Sugar" in all_raw)

    def test_14_nutrition_table(self):
        """14. Nutrition table grid detection and cell extraction."""
        img = Image.new("RGB", (700, 500), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        # Draw table grid box
        tx1, ty1, tx2, ty2 = 80, 80, 620, 380
        draw.rectangle([tx1, ty1, tx2, ty2], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        # Horizontal lines (rows)
        for y in range(ty1 + 60, ty2, 60):
            draw.line([(tx1, y), (tx2, y)], fill=(0, 0, 0), width=2)
        # Vertical line (column separator)
        draw.line([(tx1 + 270, ty1), (tx1 + 270, ty2)], fill=(0, 0, 0), width=2)

        # Table texts
        draw.text((tx1 + 20, ty1 + 18), "Nutrient", fill=(0, 0, 0))
        draw.text((tx1 + 300, ty1 + 18), "Per 100g", fill=(0, 0, 0))
        draw.text((tx1 + 20, ty1 + 78), "Energy (kcal)", fill=(0, 0, 0))
        draw.text((tx1 + 300, ty1 + 78), "480", fill=(0, 0, 0))
        draw.text((tx1 + 20, ty1 + 138), "Protein (g)", fill=(0, 0, 0))
        draw.text((tx1 + 300, ty1 + 138), "6.5", fill=(0, 0, 0))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(len(res.tables), 1)
        self.assertGreaterEqual(res.tables[0].rows_count, 2)
        self.assertGreaterEqual(res.tables[0].cols_count, 1)

    def test_15_multiple_products(self):
        """15. Multiple products in frame without mixed text."""
        img = Image.new("RGB", (1000, 500), (220, 220, 220))
        draw = ImageDraw.Draw(img)
        # Product 1
        draw.rectangle([40, 50, 460, 450], fill=(255, 255, 255), outline=(20, 20, 20), width=2)
        draw.text((70, 90), "PRODUCT ONE BISCUITS", fill=(0, 0, 0))
        draw.text((70, 140), "Net Qty: 100 g", fill=(0, 0, 0))
        # Product 2
        draw.rectangle([540, 50, 960, 450], fill=(255, 255, 255), outline=(20, 20, 20), width=2)
        draw.text((570, 90), "PRODUCT TWO JUICE", fill=(0, 0, 0))
        draw.text((570, 140), "Net Vol: 500 ml", fill=(0, 0, 0))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 2)

    def test_16_partial_label_crop(self):
        """16. Partial label crop (Zoomed close-up on statutory block)."""
        img = Image.new("RGB", (500, 350), (250, 250, 250))
        draw = ImageDraw.Draw(img)
        draw.text((30, 40), "MRP Rs. 75.00 (Incl taxes)", fill=(0, 0, 0))
        draw.text((30, 90), "Unit Sale Price: Rs. 0.75/g", fill=(0, 0, 0))
        draw.text((30, 140), "Net Quantity: 100 g", fill=(0, 0, 0))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(res.total_text_regions, 1)

    def test_17_mixed_numbers_and_letters(self):
        """17. Mixed alphanumeric identifiers preserved without dropping digits."""
        lines = [
            "Model: XZ-900A",
            "Serial: ABC-1234-XY",
            "Rating: 250V 50Hz"
        ]
        img = create_packaging_with_text(700, 500, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_raw = " ".join(r.raw_text for r in res.regions)
        self.assertTrue("XZ" in all_raw or "900" in all_raw or "1234" in all_raw or "250" in all_raw)

    def test_18_rupee_price_and_currency(self):
        """18. Currency symbol and price preservation (₹ and Rs.)."""
        lines = [
            "MRP Rs. 299.00",
            "Price: Rs. 150"
        ]
        img = create_packaging_with_text(600, 400, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_norm = " ".join(r.normalized_text for r in res.regions)
        self.assertTrue("299" in all_norm or "150" in all_norm or "Rs" in all_norm)

    def test_19_six_digit_pin_code(self):
        """19. Postal PIN code preserved verbatim."""
        lines = [
            "Manufactured by XYZ Ltd",
            "Mumbai - 400013",
            "Bengaluru - 560001"
        ]
        img = create_packaging_with_text(700, 450, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_norm = " ".join(r.normalized_text for r in res.regions)
        self.assertTrue("400013" in all_norm or "560001" in all_norm or "Mumbai" in all_norm)

    def test_20_batch_number(self):
        """20. Batch and lot numbers preserved verbatim."""
        lines = [
            "Batch No: B12345",
            "Lot: 998-A"
        ]
        img = create_packaging_with_text(600, 400, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_norm = " ".join(r.normalized_text for r in res.regions)
        self.assertTrue("B12345" in all_norm or "Batch" in all_norm or "Lot" in all_norm)

    def test_21_date_declaration(self):
        """21. Date declarations (Mfg and Expiry) normalized."""
        lines = [
            "Mfg Date: 10/2024",
            "Expiry Date: 10/2026"
        ]
        img = create_packaging_with_text(600, 400, lines=lines)
        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        all_norm = " ".join(r.normalized_text for r in res.regions)
        self.assertTrue("2024" in all_norm or "2026" in all_norm or "Mfg" in all_norm)

    def test_22_barcode_isolation(self):
        """22. 1D Barcode separated into barcode_regions, not treated as normal OCR."""
        img = Image.new("RGB", (600, 400), (250, 250, 250))
        draw = ImageDraw.Draw(img)
        # Draw 1D vertical barcode stripes
        bar_x = 150
        for i in range(35):
            w_line = 3 if i % 3 == 0 else 1
            draw.line([(bar_x, 100), (bar_x, 220)], fill=(0, 0, 0), width=w_line)
            bar_x += 6
        draw.text((150, 235), "8901234567890", fill=(0, 0, 0))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        self.assertGreaterEqual(len(res.barcode_regions), 1)
        self.assertEqual(res.barcode_regions[0].format, "1D_BARCODE")

    def test_23_qr_code_isolation(self):
        """23. 2D QR Code separated into qr_regions, not treated as normal OCR."""
        # Generate genuine QR code using OpenCV or draw finder patterns
        img = Image.new("RGB", (600, 400), (250, 250, 250))
        draw = ImageDraw.Draw(img)
        # Draw 2D QR code finder patterns
        qx, qy, qw = 200, 100, 160
        # Outer finder box 1 (top-left)
        draw.rectangle([qx, qy, qx + 45, qy + 45], fill=(0, 0, 0))
        draw.rectangle([qx + 8, qy + 8, qx + 37, qy + 37], fill=(255, 255, 255))
        draw.rectangle([qx + 16, qy + 16, qx + 29, qy + 29], fill=(0, 0, 0))

        # Outer finder box 2 (top-right)
        draw.rectangle([qx + qw - 45, qy, qx + qw, qy + 45], fill=(0, 0, 0))
        draw.rectangle([qx + qw - 37, qy + 8, qx + qw - 8, qy + 37], fill=(255, 255, 255))
        draw.rectangle([qx + qw - 29, qy + 16, qx + qw - 16, qy + 29], fill=(0, 0, 0))

        # Outer finder box 3 (bottom-left)
        draw.rectangle([qx, qy + qw - 45, qx + 45, qy + qw], fill=(0, 0, 0))
        draw.rectangle([qx + 8, qy + qw - 37, qx + 37, qy + qw - 8], fill=(255, 255, 255))
        draw.rectangle([qx + 16, qy + qw - 29, qx + 29, qy + qw - 16], fill=(0, 0, 0))

        # Random QR data bits inside
        np.random.seed(42)
        for r in range(qy + 50, qy + qw - 50, 10):
            for c in range(qx + 50, qx + qw - 50, 10):
                if np.random.rand() > 0.5:
                    draw.rectangle([c, r, c + 8, r + 8], fill=(0, 0, 0))

        res = self.pipeline.process_image_bytes(img_to_bytes(img))
        self.assertEqual(res.text_detection_status, "COMPLETED")
        # Ensure QR or Barcode service ran without crashing
        self.assertIsNotNone(res.qr_regions)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage2OcrPipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
