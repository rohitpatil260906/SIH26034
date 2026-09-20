"""
LM-COMPASS Stage 1 Automated Regression Test Suite
==================================================
Tests 18 representative packaging scenarios and edge cases:
1.  Flat cardboard package (ideal condition)
2.  Rotated package (90 degrees optical rotation)
3.  Strong perspective angle (tilted box / skewed label)
4.  Cylindrical package (bottle label curvature)
5.  Cylindrical package (curved tube label)
6.  Glare interference (harsh reflection hotspot on glossy label)
7.  Low-light condition (dim retail environment)
8.  Micro-text / small package (high DPI / upscaling needed)
9.  Heavy blur (insufficient quality detection -> zero false violations)
10. Partial label crop (tight zoom on statutory block)
11. Back panel only (non-front validity guarantee)
12. Side panel only (narrow columnar label)
13. Multi-panel composite (two panels in one image)
14. Two products in frame (multi-product segmentation)
15. Occlusion by hand / finger (holding the package)
16. Folded / wrinkled pouch packaging (surface distortion)
17. High-resolution crisp image (ideal baseline)
18. Extremely low-resolution image (insufficient quality trap)
Plus:
19. Corrupted/Invalid byte input safety (Zero-crash guarantee)
20. Bidirectional coordinate inverse mapping verification
"""

import io
import os
import sys
import math
import unittest

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import cv2

from backend.services.stage1_cv import (
    Stage1Pipeline,
    map_point_to_original,
    map_bbox_to_original
)
from backend.services.stage1_cv.geometry import order_corner_points


def create_base_packaging_image(w=800, h=600, bg_color=(175, 175, 180)):
    """Creates a synthetic packaging box with contrasting retail background and text."""
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)
    # Box rectangle
    box_margin_x = int(w * 0.12)
    box_margin_y = int(h * 0.10)
    box_x2 = w - box_margin_x
    box_y2 = h - box_margin_y
    draw.rectangle([box_margin_x, box_margin_y, box_x2, box_y2], fill=(250, 250, 250), outline=(30, 30, 30), width=3)
    
    # Brand banner
    draw.rectangle([box_margin_x + 5, box_margin_y + 5, box_x2 - 5, box_margin_y + 55], fill=(30, 80, 160))
    draw.text((box_margin_x + 20, box_margin_y + 20), "DELUXE PREMIUM BISCUITS", fill=(255, 255, 255))

    # Mock statutory text lines
    line_y = box_margin_y + 75
    draw.text((box_margin_x + 25, line_y), "Net Qty: 200 g (Pack of 2 x 100 g)", fill=(30, 30, 30))
    line_y += 35
    draw.text((box_margin_x + 25, line_y), "MRP Rs. 50.00 (Incl. of all taxes)", fill=(30, 30, 30))
    line_y += 30
    draw.text((box_margin_x + 25, line_y), "Unit Sale Price: Rs. 0.25/g", fill=(30, 30, 30))
    line_y += 30
    draw.text((box_margin_x + 25, line_y), "Mfg Date: 12/2024  Exp Date: 12/2025", fill=(30, 30, 30))
    line_y += 30
    draw.text((box_margin_x + 25, line_y), "Mfd By: Golden Bake Foods Pvt Ltd, Mumbai - 400013", fill=(30, 30, 30))
    line_y += 30
    draw.text((box_margin_x + 25, line_y), "Consumer Care: 1800-222-333 / care@goldenbake.com", fill=(30, 30, 30))
    return img


def img_to_bytes(img: Image.Image, fmt="JPEG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


class TestStage1ImagePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = Stage1Pipeline()

    def test_01_flat_cardboard_package(self):
        """1. Flat cardboard package under normal lighting."""
        img = create_base_packaging_image(800, 600)
        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="flat_box.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertIn(res.quality.status, ["GOOD", "DEGRADED"])
        self.assertTrue(res.package_detection.detected)
        self.assertGreaterEqual(res.package_detection.products_count, 1)
        self.assertIn("upscaled", res.preprocessing)
        self.assertIn("clahe", res.preprocessing)

    def test_02_rotated_package(self):
        """2. Rotated package (90 degrees optical rotation)."""
        img = create_base_packaging_image(600, 800)
        rotated = img.rotate(90, expand=True)
        res = self.pipeline.process_image_bytes(img_to_bytes(rotated), filename="rotated.jpg")
        self.assertIn(res.status, ["READY_FOR_TEXT_DETECTION", "NEEDS_REVIEW"])
        self.assertTrue(res.package_detection.detected)
        self.assertIsNotNone(res.input.orientation)

    def test_03_strong_perspective_angle(self):
        """3. Strong perspective tilt / keystone skew."""
        img = create_base_packaging_image(800, 600)
        cv_img = np.array(img)
        h, w = cv_img.shape[:2]
        pts1 = np.float32([[50, 50], [w - 50, 120], [w - 120, h - 50], [80, h - 100]])
        pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        m = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(cv_img, m, (w, h))
        warped_pil = Image.fromarray(warped)

        res = self.pipeline.process_image_bytes(img_to_bytes(warped_pil), filename="skewed.jpg")
        self.assertIn(res.status, ["READY_FOR_TEXT_DETECTION", "NEEDS_REVIEW"])
        self.assertTrue(res.package_detection.detected)
        self.assertIsNotNone(res.geometry.transformation_matrix)

    def test_04_cylindrical_bottle_package(self):
        """4. Cylindrical bottle with horizontal curvature."""
        img = create_base_packaging_image(800, 600)
        cv_img = np.array(img)
        h, w = cv_img.shape[:2]
        # Draw curved bottle contours
        for y in range(100, 500, 40):
            pts = []
            for x in range(150, 650, 10):
                arc_y = int(y + 20 * math.sin((x - 150) / 500.0 * math.pi))
                pts.append((x, arc_y))
            pts_arr = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(cv_img, [pts_arr], False, (50, 50, 50), 2)
        bottle_pil = Image.fromarray(cv_img)

        res = self.pipeline.process_image_bytes(img_to_bytes(bottle_pil), filename="bottle.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertTrue(res.package_detection.detected)
        self.assertTrue(res.geometry.curvature_detected)

    def test_05_cylindrical_tube_package(self):
        """5. Curved squeeze tube package."""
        img = create_base_packaging_image(500, 900)
        cv_img = np.array(img)
        h, w = cv_img.shape[:2]
        # Draw parabolic curved label seam
        for y in range(150, 750, 50):
            pts = []
            for x in range(100, 400, 10):
                arc_y = int(y + 15 * math.sin((x - 100) / 300.0 * math.pi))
                pts.append((x, arc_y))
            cv2.polylines(cv_img, [np.array(pts, np.int32).reshape((-1, 1, 2))], False, (60, 60, 60), 2)
        tube_pil = Image.fromarray(cv_img)

        res = self.pipeline.process_image_bytes(img_to_bytes(tube_pil), filename="tube.jpg")
        self.assertIn(res.status, ["READY_FOR_TEXT_DETECTION", "NEEDS_REVIEW"])
        self.assertTrue(res.package_detection.detected)

    def test_06_glare_interference(self):
        """6. Specular glare reflection on glossy film."""
        img = create_base_packaging_image(800, 600)
        draw = ImageDraw.Draw(img)
        # Saturated glare hotspot
        draw.ellipse([300, 180, 450, 320], fill=(255, 255, 255))
        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="glare.jpg")
        self.assertIn(res.status, ["READY_FOR_TEXT_DETECTION", "DEGRADED", "NEEDS_REVIEW"])
        self.assertLess(res.quality.glare_score, 100.0)
        self.assertIn("glare_shadow_reduced", res.preprocessing)

    def test_07_low_light_condition(self):
        """7. Low light / underexposed retail shelf."""
        img = create_base_packaging_image(800, 600)
        cv_img = np.array(img)
        dim_img = (cv_img * 0.25).astype(np.uint8)
        dim_pil = Image.fromarray(dim_img)

        res = self.pipeline.process_image_bytes(img_to_bytes(dim_pil), filename="dim.jpg")
        self.assertIn(res.status, ["READY_FOR_TEXT_DETECTION", "NEEDS_REVIEW", "INSUFFICIENT_QUALITY"])
        self.assertTrue(res.quality.contrast_score < 100.0 or len(res.quality.issues) > 0)
        self.assertIn("clahe", res.preprocessing)

    def test_08_micro_text_small_package(self):
        """8. Micro-text packaging requiring resolution upscaling."""
        img = create_base_packaging_image(400, 300)
        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="micro.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertIn("upscaled", res.preprocessing)
        upscaled_branch = res.preprocessing["upscaled"]
        self.assertGreater(upscaled_branch["width"], 400)

    def test_09_heavy_blur_insufficient_quality(self):
        """9. Heavy blur -> must trigger INSUFFICIENT_QUALITY and NOT produce false violations."""
        img = create_base_packaging_image(800, 600)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=25))
        res = self.pipeline.process_image_bytes(img_to_bytes(blurred), filename="blurry.jpg")
        self.assertEqual(res.quality.status, "INSUFFICIENT")
        self.assertEqual(res.status, "INSUFFICIENT_QUALITY")
        self.assertLess(res.quality.blur_score, 40.0)
        self.assertIn("blur", res.quality.explanation.lower() + " ".join(res.quality.issues).lower())

    def test_10_partial_label_crop(self):
        """10. Partial label crop (tight zoom on statutory block, non-front validity)."""
        img = create_base_packaging_image(800, 600)
        # Crop tight around the text area
        cropped = img.crop((140, 100, 550, 350))
        res = self.pipeline.process_image_bytes(img_to_bytes(cropped), filename="partial.jpg")
        self.assertNotEqual(res.status, "REJECTED")
        self.assertEqual(res.panel.coverage, "PARTIAL")

    def test_11_back_panel_only(self):
        """11. Back panel only (non-front validity: must NOT be rejected)."""
        img = Image.new("RGB", (700, 900), (250, 250, 250))
        draw = ImageDraw.Draw(img)
        # Dense text grid simulating nutrition & statutory table
        draw.rectangle([40, 40, 660, 860], outline=(0, 0, 0), width=2)
        y = 60
        for i in range(25):
            draw.text((60, y), f"Statutory Declaration Line {i+1}: Standard nutrient analysis table 100g", fill=(0, 0, 0))
            y += 30
        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="back_panel.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertEqual(res.panel.type, "BACK")
        self.assertFalse(res.panel.is_front)

    def test_12_side_panel_only(self):
        """12. Side panel only (narrow columnar label: aspect ratio > 2.5)."""
        img = Image.new("RGB", (250, 850), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 230, 830], outline=(20, 20, 20), width=2)
        y = 40
        for i in range(20):
            draw.text((30, y), f"Batch: B{i}123", fill=(0, 0, 0))
            y += 35
        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="side_panel.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertEqual(res.panel.type, "SIDE")

    def test_13_multi_panel_composite(self):
        """13. Multi-panel composite (two panels in one frame)."""
        img = Image.new("RGB", (1000, 500), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        # Left panel
        draw.rectangle([40, 40, 460, 460], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.text((60, 80), "FRONT PANEL BRAND", fill=(0, 0, 0))
        # Right panel
        draw.rectangle([540, 40, 960, 460], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.text((560, 80), "BACK INGREDIENTS", fill=(0, 0, 0))

        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="dual_panel.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertTrue(res.package_detection.detected)

    def test_14_two_products_in_frame(self):
        """14. Two products in frame -> multi-product segmentation."""
        img = Image.new("RGB", (1100, 600), (235, 235, 235))
        draw = ImageDraw.Draw(img)
        # Product 1 box
        draw.rectangle([50, 80, 480, 520], fill=(255, 255, 255), outline=(10, 10, 10), width=3)
        draw.text((80, 120), "PRODUCT 1: BISCUITS 200g", fill=(0, 0, 0))
        # Product 2 box
        draw.rectangle([580, 80, 1010, 520], fill=(255, 255, 255), outline=(10, 10, 10), width=3)
        draw.text((610, 120), "PRODUCT 2: JUICE 500ml", fill=(0, 0, 0))

        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="two_products.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertGreaterEqual(res.package_detection.products_count, 2)
        self.assertEqual(res.package_detection.product_instances[0].instance_id, "product_instance_1")
        self.assertEqual(res.package_detection.product_instances[1].instance_id, "product_instance_2")

    def test_15_occlusion_by_hand(self):
        """15. Hand/finger occluding part of the package border."""
        img = create_base_packaging_image(800, 600)
        draw = ImageDraw.Draw(img)
        # Skin tone ellipse simulating finger at edge (HSV skin tone: H~15, S~150, V~200 -> RGB: ~220, 150, 120)
        draw.ellipse([650, 200, 780, 320], fill=(220, 150, 120))
        draw.ellipse([640, 280, 770, 380], fill=(215, 145, 115))

        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="hand_holding.jpg")
        self.assertIn(res.status, ["READY_FOR_TEXT_DETECTION", "NEEDS_REVIEW"])
        self.assertLess(res.quality.occlusion_score, 100.0)

    def test_16_wrinkled_pouch_packaging(self):
        """16. Wrinkled pouch packaging surface distortion."""
        img = create_base_packaging_image(800, 600)
        cv_img = np.array(img)
        h, w = cv_img.shape[:2]
        # Simulate sinusoidal wrinkle shading
        x = np.arange(w)
        wrinkle_pattern = (np.sin(x / 15.0) * 20).astype(np.int16)
        wrinkled_cv = np.clip(cv_img.astype(np.int16) + wrinkle_pattern[None, :, None], 0, 255).astype(np.uint8)
        wrinkled_pil = Image.fromarray(wrinkled_cv)

        res = self.pipeline.process_image_bytes(img_to_bytes(wrinkled_pil), filename="pouch.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertIn("adaptive_thresh", res.preprocessing)

    def test_17_high_res_crisp_image(self):
        """17. High-resolution crisp image (ideal baseline)."""
        img = create_base_packaging_image(1600, 1200)
        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="crisp.jpg")
        self.assertEqual(res.status, "READY_FOR_TEXT_DETECTION")
        self.assertEqual(res.quality.status, "GOOD")
        self.assertGreaterEqual(res.quality.overall_score, 75.0)

    def test_18_extremely_low_res_image(self):
        """18. Extremely low-resolution image (< 200px) -> insufficient quality trap."""
        img = create_base_packaging_image(120, 90)
        res = self.pipeline.process_image_bytes(img_to_bytes(img), filename="tiny.jpg")
        self.assertEqual(res.quality.status, "INSUFFICIENT")
        self.assertEqual(res.status, "INSUFFICIENT_QUALITY")
        self.assertLessEqual(res.quality.resolution_score, 20.0)

    def test_19_corrupted_input_safety(self):
        """19. Corrupted/truncated/invalid byte safety (Zero-crash guarantee)."""
        # Empty bytes
        res1 = self.pipeline.process_image_bytes(b"", filename="empty.jpg")
        self.assertEqual(res1.status, "INSUFFICIENT_QUALITY")
        self.assertEqual(res1.input.processing_status, "REJECTED")

        # Random non-image bytes
        res2 = self.pipeline.process_image_bytes(b"not_an_image_data_garbage_stream_12345", filename="corrupt.jpg")
        self.assertEqual(res2.status, "INSUFFICIENT_QUALITY")
        self.assertEqual(res2.input.processing_status, "REJECTED")

        # Invalid base64 string
        res3 = self.pipeline.process_base64_image("invalid_base64_!@#$", filename="corrupt.png")
        self.assertEqual(res3.status, "INSUFFICIENT_QUALITY")

    def test_20_coordinate_inverse_mapping(self):
        """20. Bidirectional coordinate inverse mapping verification."""
        # Simple homography matrix (e.g. scale by 2 and offset by 50)
        # Rectified (x, y) -> Original (x/2 - 25, y/2 - 25)
        m = np.array([
            [2.0, 0.0, 50.0],
            [0.0, 2.0, 50.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        _, m_inv = cv2.invert(m)

        # Test point mapping
        ox, oy = map_point_to_original(150.0, 150.0, m_inv)
        self.assertAlmostEqual(ox, 50.0, places=2)
        self.assertAlmostEqual(oy, 50.0, places=2)

        # Test bbox mapping
        mapped_box = map_bbox_to_original([150.0, 150.0, 100.0, 80.0], m_inv, orig_w=500, orig_h=500)
        self.assertAlmostEqual(mapped_box[0], 50.0, delta=1.0)
        self.assertAlmostEqual(mapped_box[1], 50.0, delta=1.0)
        self.assertAlmostEqual(mapped_box[2], 50.0, delta=1.0)
        self.assertAlmostEqual(mapped_box[3], 40.0, delta=1.0)

        # Corner point ordering
        unordered = np.array([[200, 200], [50, 200], [200, 50], [50, 50]], dtype=np.float32)
        ordered = order_corner_points(unordered)
        np.testing.assert_array_equal(ordered[0], [50, 50])    # Top-Left
        np.testing.assert_array_equal(ordered[1], [200, 50])   # Top-Right
        np.testing.assert_array_equal(ordered[2], [200, 200])  # Bottom-Right
        np.testing.assert_array_equal(ordered[3], [50, 200])   # Bottom-Left


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStage1ImagePipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        exit(1)
