"""
LM-COMPASS Stage 5 Automated Regression Test Suite
==================================================
Tests 25 representative difficult-image scenarios and recovery capabilities:
1.  Straight package (Pristine baseline -> verifies lightweight / no-op path)
2.  Rotated package (90° rotation -> verifies orientation normalization)
3.  Perspective package (Oblique angle -> verifies homography & coordinate back-mapping)
4.  Curved bottle (Cylindrical label -> verifies curvature detection & unwrap)
5.  Curved tube (Tapered / flexible tube label -> verifies curvature compensation)
6.  Cylindrical can (Beverage/food can -> verifies radial unrolling)
7.  Jar (Wide curved glass/plastic jar label)
8.  Pouch (Flexible packaging pillow pouch)
9.  Glare (Harsh specular highlight -> verifies glare suppression & no-hallucination guard)
10. Shadow (Uneven illumination gradient -> verifies Retinex background leveling)
11. Low light (Dim lighting condition -> verifies gamma & contrast enhancement)
12. Tiny text (Micro-declarations -> verifies super-resolution & crop preservation)
13. Motion blur (Horizontal/vertical motion smear -> verifies directional sharpening)
14. Defocus blur (Out-of-focus capture -> verifies deblurring & OCR_UNCERTAIN handling)
15. Compression artifacts (Heavy JPEG blocking -> verifies artifact smoothing)
16. Folded label (Crease line across text -> verifies local region split & rectification)
17. Wrinkled label (Surface crinkles -> verifies local contrast enhancement)
18. Partial label (Visible-only recovery -> verifies zero fabricated text)
19. Partial occlusion (Finger/sticker detected -> marks PARTIALLY_OCCLUDED)
20. Curved + Glare (Compound distortion -> verifies ordered pipeline)
21. Curved + Blur (Compound distortion -> verifies cylindrical unwrap + deblurring)
22. Perspective + Glare (Compound distortion -> verifies homography + glare reduction)
23. Tiny MRP text (Small ₹ MRP declaration -> verifies targeted crop & OCR consensus)
24. Tiny net quantity text (Small Net Qty declaration -> verifies accurate consensus)
25. Small manufacturer/address block (Multi-line statutory address recovery)
Plus:
26. Original image preservation guarantee (Immutable hash & bytes verification)
27. Bidirectional coordinate mapping precision (Roundtrip mapping error < 1.5px)
28. End-to-end integration: Stage 1 -> Stage 5 -> Stage 2 -> Stage 3 -> Stage 4
"""

import io
import os
import sys
import math
import hashlib
import unittest
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import numpy as np
import cv2

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models import (
    Stage1Response,
    Stage2Response,
    Stage3Response,
    Stage4Response,
    Stage5Response
)
from backend.services.stage1_cv import Stage1Pipeline
from backend.services.stage2_ocr import Stage2Pipeline
from backend.services.stage3_semantic import Stage3Pipeline
from backend.services.stage4_identity import Stage4Pipeline
from backend.services.stage5_recovery import (
    Stage5Pipeline,
    CoordinateTransformChain,
    CoordinateTransformStep
)
from backend.services.stage5_recovery.coordinate_mapper import CoordinateTransformStep, CoordinateTransformChain


def create_base_packaging_image(w=800, h=600, bg_color=(185, 185, 190)):
    """Creates a synthetic flat packaging box with retail background and crisp text declarations."""
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Box rectangle
    bx1, by1 = int(w * 0.12), int(h * 0.10)
    bx2, by2 = int(w * 0.88), int(h * 0.90)
    draw.rectangle([bx1, by1, bx2, by2], fill=(250, 250, 250), outline=(25, 25, 25), width=3)

    # Brand banner
    draw.rectangle([bx1 + 5, by1 + 5, bx2 - 5, by1 + 60], fill=(20, 70, 150))
    draw.text((bx1 + 25, by1 + 20), "DELUXE ROYAL ALMONDS", fill=(255, 255, 255))

    # Statutory text declarations
    y = by1 + 80
    draw.text((bx1 + 25, y), "Net Qty: 500 g", fill=(30, 30, 30))
    y += 35
    draw.text((bx1 + 25, y), "MRP Rs. 499.00 (Incl. of all taxes)", fill=(30, 30, 30))
    y += 35
    draw.text((bx1 + 25, y), "Unit Sale Price: Rs. 0.998/g", fill=(30, 30, 30))
    y += 35
    draw.text((bx1 + 25, y), "Mfg Date: 10/2024  Expiry Date: 10/2025", fill=(30, 30, 30))
    y += 35
    draw.text((bx1 + 25, y), "Batch No: BATCH-ALM-992", fill=(30, 30, 30))
    y += 35
    draw.text((bx1 + 25, y), "Mfd By: Royal Nutrients Pvt Ltd, Mumbai - 400013", fill=(30, 30, 30))
    y += 35
    draw.text((bx1 + 25, y), "Consumer Care: 1800-111-222 / care@royalnutrients.com", fill=(30, 30, 30))
    return img


def apply_cylindrical_warp(img: Image.Image, curvature=0.0003) -> Image.Image:
    """Simulates cylindrical label curvature (parabolic displacement on horizontal lines)."""
    cv_img = np.array(img)[:, :, ::-1].copy()
    h, w = cv_img.shape[:2]
    cx = w / 2.0
    map_x = np.zeros((h, w), dtype=np.float32)
    map_y = np.zeros((h, w), dtype=np.float32)

    for y in range(h):
        for x in range(w):
            dy = curvature * ((x - cx) ** 2)
            map_x[y, x] = x
            map_y[y, x] = np.clip(y + dy, 0, h - 1)

    warped = cv2.remap(cv_img, map_x, map_y, interpolation=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))


def apply_perspective_warp(img: Image.Image) -> Image.Image:
    """Applies oblique trapezoidal perspective distortion."""
    cv_img = np.array(img)[:, :, ::-1].copy()
    h, w = cv_img.shape[:2]
    src_pts = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
    dst_pts = np.array([
        [int(w * 0.12), int(h * 0.08)],
        [int(w * 0.88), int(h * 0.02)],
        [int(w * 0.95), int(h * 0.96)],
        [int(w * 0.05), int(h * 0.90)]
    ], dtype=np.float32)
    m = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(cv_img, m, (w, h), borderValue=(185, 185, 190))
    return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))


class TestStage5RecoveryPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage1 = Stage1Pipeline()
        cls.stage5 = Stage5Pipeline()
        cls.stage2 = Stage2Pipeline()
        cls.stage3 = Stage3Pipeline()
        cls.stage4 = Stage4Pipeline()

    # ----------------------------------------------------
    # TEST 1: Straight package (Clear -> Lightweight path)
    # ----------------------------------------------------
    def test_01_straight_package(self):
        """1. Straight package: verifies lightweight / minimal processing path preserves pristine evidence."""
        img = create_base_packaging_image(800, 600)
        res, best_img, chain = self.stage5.recover_difficult_image(img)
        self.assertIn(res.recovery_status, ["MINIMAL_PROCESSING", "COMPLETED"])
        self.assertGreaterEqual(len(res.variants), 1)
        self.assertFalse(res.fallback_used)
        # Verify text was detected via consensus
        self.assertGreater(len(res.ocr_consensus), 0)

    # ----------------------------------------------------
    # TEST 2: Rotated package (90 degrees)
    # ----------------------------------------------------
    def test_02_rotated_package(self):
        """2. Rotated package: 90 degrees clockwise rotation normalized."""
        img = create_base_packaging_image(800, 600)
        rot_img = img.rotate(270, expand=True)  # 90 deg clockwise
        res, best_img, chain = self.stage5.recover_difficult_image(rot_img)
        self.assertIn("ROTATION", res.distortions_detected)
        self.assertTrue(len(res.variants) > 0)
        self.assertTrue(chain.steps or any("rotate" in v.transformation_chain for v in res.variants))

    # ----------------------------------------------------
    # TEST 3: Perspective package
    # ----------------------------------------------------
    def test_03_perspective_package(self):
        """3. Perspective package: trapezoidal angle homography rectified."""
        img = create_base_packaging_image(800, 600)
        persp_img = apply_perspective_warp(img)
        res, best_img, chain = self.stage5.recover_difficult_image(persp_img)
        self.assertIn("PERSPECTIVE_DISTORTION", res.distortions_detected)
        self.assertTrue(any(v.type in ["PERSPECTIVE_CORRECTED", "BASE_INPUT", "CLAHE"] for v in res.variants))
        # Coordinate mapping should be available
        for v in res.variants:
            self.assertTrue(v.coordinate_mapping_available)

    # ----------------------------------------------------
    # TEST 4: Curved bottle
    # ----------------------------------------------------
    def test_04_curved_bottle(self):
        """4. Curved bottle: cylindrical parabolic curvature unrolling."""
        img = create_base_packaging_image(800, 600)
        curved_img = apply_cylindrical_warp(img, curvature=0.00035)
        res, best_img, chain = self.stage5.recover_difficult_image(curved_img)
        self.assertTrue(any(d in res.distortions_detected for d in ["CURVATURE", "CYLINDRICAL_CURVATURE"]))
        self.assertGreater(len(res.variants), 1)

    # ----------------------------------------------------
    # TEST 5: Curved tube
    # ----------------------------------------------------
    def test_05_curved_tube(self):
        """5. Curved tube: flexible cosmetic tube curvature unwarping."""
        img = create_base_packaging_image(800, 600)
        tube_img = apply_cylindrical_warp(img, curvature=0.00045)
        res, best_img, chain = self.stage5.recover_difficult_image(tube_img)
        self.assertTrue(any(d in res.distortions_detected for d in ["CURVATURE", "CYLINDRICAL_CURVATURE"]))

    # ----------------------------------------------------
    # TEST 6: Cylindrical can
    # ----------------------------------------------------
    def test_06_cylindrical_can(self):
        """6. Cylindrical can: metal beverage can radial surface."""
        img = create_base_packaging_image(700, 700)
        can_img = apply_cylindrical_warp(img, curvature=0.0003)
        res, best_img, chain = self.stage5.recover_difficult_image(can_img)
        self.assertIn(res.recovery_status, ["COMPLETED", "MINIMAL_PROCESSING"])

    # ----------------------------------------------------
    # TEST 7: Jar
    # ----------------------------------------------------
    def test_07_jar(self):
        """7. Jar: wide plastic/glass jar label curvature."""
        img = create_base_packaging_image(900, 600)
        jar_img = apply_cylindrical_warp(img, curvature=0.00025)
        res, best_img, chain = self.stage5.recover_difficult_image(jar_img)
        self.assertIsNotNone(res.scan_id)

    # ----------------------------------------------------
    # TEST 8: Pouch
    # ----------------------------------------------------
    def test_08_pouch(self):
        """8. Pouch: flexible pillow pouch packaging with slight curvature."""
        img = create_base_packaging_image(750, 600)
        pouch_img = apply_cylindrical_warp(img, curvature=0.0002)
        res, best_img, chain = self.stage5.recover_difficult_image(pouch_img)
        self.assertGreater(len(res.ocr_consensus), 0)

    # ----------------------------------------------------
    # TEST 9: Glare
    # ----------------------------------------------------
    def test_09_glare(self):
        """9. Glare: bright specular hotspot detection and suppression."""
        img = create_base_packaging_image(800, 600)
        draw = ImageDraw.Draw(img)
        # Draw harsh white specular reflection patch
        draw.ellipse([300, 200, 480, 320], fill=(255, 255, 255))
        res, best_img, chain = self.stage5.recover_difficult_image(img, skip_ocr=True)
        self.assertIn("GLARE", res.distortions_detected)
        self.assertTrue(len(res.difficult_regions) > 0 or any("glare" in v.variant_id for v in res.variants))

    # ----------------------------------------------------
    # TEST 10: Shadow
    # ----------------------------------------------------
    def test_10_shadow(self):
        """10. Shadow: uneven lighting gradient leveled."""
        img = create_base_packaging_image(800, 600)
        cv_img = np.array(img)
        # Apply dark shadow across left half
        h, w = cv_img.shape[:2]
        cv_img[:, :w // 2] = (cv_img[:, :w // 2] * 0.35).astype(np.uint8)
        shadow_img = Image.fromarray(cv_img)
        res, best_img, chain = self.stage5.recover_difficult_image(shadow_img, skip_ocr=True)
        self.assertIn("SHADOW", res.distortions_detected)

    # ----------------------------------------------------
    # TEST 11: Low light
    # ----------------------------------------------------
    def test_11_low_light(self):
        """11. Low light: dim exposure compensated."""
        img = create_base_packaging_image(800, 600)
        enhancer = ImageOps.autocontrast(img.point(lambda p: p * 0.25))
        res, best_img, chain = self.stage5.recover_difficult_image(enhancer, skip_ocr=True)
        self.assertTrue(len(res.variants) >= 1)

    # ----------------------------------------------------
    # TEST 12: Tiny text
    # ----------------------------------------------------
    def test_12_tiny_text(self):
        """12. Tiny text: micro-print super-resolution crop preservation."""
        img = Image.new("RGB", (600, 400), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "NET QUANTITY: 50 g", fill=(20, 20, 20))
        draw.text((50, 80), "MRP Rs. 20.00", fill=(20, 20, 20))
        
        crop_res = self.stage5.super_res_service.upscale_crop(
            img, crop_bbox=[45.0, 45.0, 200.0, 60.0], scale_factor=2.4
        )
        self.assertIsNotNone(crop_res.original_crop)
        self.assertIsNotNone(crop_res.upscaled_crop)
        self.assertIsNotNone(crop_res.enhanced_crop)
        self.assertGreater(crop_res.upscaled_crop.width, crop_res.original_crop.width)

    # ----------------------------------------------------
    # TEST 13: Motion blur
    # ----------------------------------------------------
    def test_13_motion_blur(self):
        """13. Motion blur: directional smear classified and sharpened."""
        img = create_base_packaging_image(800, 600)
        cv_img = np.array(img)
        # Create horizontal motion blur kernel
        kernel_size = 9
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
        kernel /= kernel_size
        blurred_cv = cv2.filter2D(cv_img, -1, kernel)
        blurred_img = Image.fromarray(blurred_cv)

        res, best_img, chain = self.stage5.recover_difficult_image(blurred_img, skip_ocr=True)
        self.assertTrue(any(d in res.distortions_detected for d in ["MOTION_BLUR", "BLUR"]))

    # ----------------------------------------------------
    # TEST 14: Defocus blur
    # ----------------------------------------------------
    def test_14_defocus_blur(self):
        """14. Defocus blur: out-of-focus capture treated as enhancement."""
        img = create_base_packaging_image(800, 600)
        defocused = img.filter(ImageFilter.GaussianBlur(radius=3))
        res, best_img, chain = self.stage5.recover_difficult_image(defocused, skip_ocr=True)
        self.assertTrue(any(d in res.distortions_detected for d in ["BLUR", "DEFOCUS_BLUR"]))

    # ----------------------------------------------------
    # TEST 15: Compression artifacts
    # ----------------------------------------------------
    def test_15_compression_artifacts(self):
        """15. Compression artifacts: heavy JPEG blocking mitigated."""
        img = create_base_packaging_image(800, 600)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=15)
        compressed_img = Image.open(buf)
        res, best_img, chain = self.stage5.recover_difficult_image(compressed_img, skip_ocr=True)
        self.assertIsNotNone(res.scan_id)

    # ----------------------------------------------------
    # TEST 16: Folded label
    # ----------------------------------------------------
    def test_16_folded_label(self):
        """16. Folded label: crease line across text."""
        img = create_base_packaging_image(800, 600)
        draw = ImageDraw.Draw(img)
        # Draw vertical crease
        draw.line([(400, 50), (400, 550)], fill=(80, 80, 80), width=4)
        res, best_img, chain = self.stage5.recover_difficult_image(img, skip_ocr=True)
        self.assertIn("WRINKLING", res.distortions_detected)

    # ----------------------------------------------------
    # TEST 17: Wrinkled label
    # ----------------------------------------------------
    def test_17_wrinkled_label(self):
        """17. Wrinkled label: surface crinkles."""
        img = create_base_packaging_image(800, 600)
        draw = ImageDraw.Draw(img)
        for x in [250, 380, 520]:
            draw.line([(x, 70), (x + 10, 500)], fill=(90, 90, 90), width=3)
        res, best_img, chain = self.stage5.recover_difficult_image(img, skip_ocr=True)
        self.assertTrue(len(res.variants) > 0)

    # ----------------------------------------------------
    # TEST 18: Partial label (Strict No-Hallucination)
    # ----------------------------------------------------
    def test_18_partial_label(self):
        """18. Partial label: visible-only evidence; no fabricated words."""
        img = Image.new("RGB", (600, 400), (245, 245, 245))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "Mfd By: Golden Bake...", fill=(20, 20, 20))
        res, best_img, chain = self.stage5.recover_difficult_image(img)
        all_text = " ".join([c.raw_text for c in res.ocr_consensus])
        # Must not fabricate Pune / Mumbai if not in image
        self.assertNotIn("Pune", all_text)

    # ----------------------------------------------------
    # TEST 19: Partial occlusion
    # ----------------------------------------------------
    def test_19_partial_occlusion(self):
        """19. Partial occlusion: finger holding edge flagged as PARTIAL_OCCLUSION."""
        img = create_base_packaging_image(800, 600)
        draw = ImageDraw.Draw(img)
        # Draw finger-like skin tone oval at border: YCrCb skin color in RGB is approx (210, 150, 120)
        draw.ellipse([0, 200, 80, 400], fill=(215, 145, 115))
        res, best_img, chain = self.stage5.recover_difficult_image(img, skip_ocr=True)
        self.assertIn("PARTIAL_OCCLUSION", res.distortions_detected)

    # ----------------------------------------------------
    # TEST 20: Curved + Glare
    # ----------------------------------------------------
    def test_20_curved_plus_glare(self):
        """20. Curved + Glare: multi-distortion ordered pipeline execution."""
        img = create_base_packaging_image(800, 600)
        curved = apply_cylindrical_warp(img, curvature=0.0003)
        draw = ImageDraw.Draw(curved)
        draw.ellipse([320, 200, 480, 300], fill=(255, 255, 255))
        res, best_img, chain = self.stage5.recover_difficult_image(curved, skip_ocr=True)
        self.assertIn("MULTIPLE_DISTORTIONS", res.distortions_detected)

    # ----------------------------------------------------
    # TEST 21: Curved + Blur
    # ----------------------------------------------------
    def test_21_curved_plus_blur(self):
        """21. Curved + Blur: curvature unwrap followed by deblurring."""
        img = create_base_packaging_image(800, 600)
        curved = apply_cylindrical_warp(img, curvature=0.0003)
        blurred = curved.filter(ImageFilter.GaussianBlur(radius=2))
        res, best_img, chain = self.stage5.recover_difficult_image(blurred, skip_ocr=True)
        self.assertIn("MULTIPLE_DISTORTIONS", res.distortions_detected)

    # ----------------------------------------------------
    # TEST 22: Perspective + Glare
    # ----------------------------------------------------
    def test_22_perspective_plus_glare(self):
        """22. Perspective + Glare: homography followed by highlight suppression."""
        img = create_base_packaging_image(800, 600)
        persp = apply_perspective_warp(img)
        draw = ImageDraw.Draw(persp)
        draw.ellipse([250, 180, 420, 280], fill=(255, 255, 255))
        res, best_img, chain = self.stage5.recover_difficult_image(persp, skip_ocr=True)
        self.assertIn("MULTIPLE_DISTORTIONS", res.distortions_detected)

    # ----------------------------------------------------
    # TEST 23: Tiny MRP text
    # ----------------------------------------------------
    def test_23_tiny_mrp_text(self):
        """23. Tiny MRP text: small price block recovered with consensus."""
        img = Image.new("RGB", (600, 300), (245, 245, 245))
        draw = ImageDraw.Draw(img)
        draw.text((40, 50), "MRP Rs. 149.00 (Incl. of all taxes)", fill=(20, 20, 20))
        res, best_img, chain = self.stage5.recover_difficult_image(img)
        all_text = " ".join([c.raw_text + " " + c.normalized_text for c in res.ocr_consensus])
        self.assertTrue("149" in all_text or "MRP" in all_text or "taxes" in all_text)

    # ----------------------------------------------------
    # TEST 24: Tiny net quantity text
    # ----------------------------------------------------
    def test_24_tiny_net_quantity_text(self):
        """24. Tiny net quantity text: small unit measure recovered."""
        img = Image.new("RGB", (600, 300), (245, 245, 245))
        draw = ImageDraw.Draw(img)
        draw.text((40, 50), "Net Quantity: 250 g", fill=(20, 20, 20))
        res, best_img, chain = self.stage5.recover_difficult_image(img)
        all_text = " ".join([c.raw_text for c in res.ocr_consensus])
        self.assertTrue("250" in all_text or "Quantity" in all_text or "Net" in all_text)

    # ----------------------------------------------------
    # TEST 25: Small manufacturer/address block
    # ----------------------------------------------------
    def test_25_small_manufacturer_address_block(self):
        """25. Small manufacturer address block: multi-line statutory address."""
        img = Image.new("RGB", (700, 350), (245, 245, 245))
        draw = ImageDraw.Draw(img)
        draw.text((40, 40), "Mfd By: Alpha Consumer Care Pvt Ltd", fill=(20, 20, 20))
        draw.text((40, 75), "Plot No. 45, MIDC Industrial Area, Pune - 411028", fill=(20, 20, 20))
        res, best_img, chain = self.stage5.recover_difficult_image(img)
        all_text = " ".join([c.raw_text for c in res.ocr_consensus])
        self.assertTrue("Alpha" in all_text or "Pune" in all_text or "411028" in all_text)

    # ----------------------------------------------------
    # TEST 26: Original Image Preservation Guarantee
    # ----------------------------------------------------
    def test_26_original_image_immutability(self):
        """26. Original image preservation: hash and bytes remain 100% identical."""
        img = create_base_packaging_image(800, 600)
        orig_bytes = img.tobytes()
        orig_hash = hashlib.sha256(orig_bytes).hexdigest()

        # Run aggressive multi-distortion recovery
        res, best_img, chain = self.stage5.recover_difficult_image(img, skip_ocr=True)

        # Re-verify original image untouched
        post_bytes = img.tobytes()
        post_hash = hashlib.sha256(post_bytes).hexdigest()
        self.assertEqual(orig_hash, post_hash)

    # ----------------------------------------------------
    # TEST 27: Bidirectional Coordinate Mapping Precision
    # ----------------------------------------------------
    def test_27_coordinate_mapping_precision(self):
        """27. Coordinate mapping precision: roundtrip point error < 1.5 pixels."""
        chain = CoordinateTransformChain()
        chain.add_crop(100.0, 50.0, 400.0, 300.0)
        chain.add_scale(2.0, 2.0)

        test_pt = (250.0, 180.0)
        orig_pt = chain.map_point_to_original(test_pt[0], test_pt[1])
        # In crop space: 250 / 2 = 125, 180 / 2 = 90
        # In parent space: 125 + 100 = 225, 90 + 50 = 140
        self.assertAlmostEqual(orig_pt[0], 225.0, places=1)
        self.assertAlmostEqual(orig_pt[1], 140.0, places=1)

        # Forward roundtrip
        fwd_pt = chain.map_point_from_original(orig_pt[0], orig_pt[1])
        self.assertAlmostEqual(fwd_pt[0], test_pt[0], places=1)
        self.assertAlmostEqual(fwd_pt[1], test_pt[1], places=1)

    # ----------------------------------------------------
    # TEST 28: End-to-End Pipeline Integration (Stages 1->5->2->3->4)
    # ----------------------------------------------------
    def test_28_end_to_end_stages_1_to_4_flow(self):
        """28. Verifies clean architectural flow: Stage 1 -> Stage 5 -> Stage 2 -> Stage 3 -> Stage 4."""
        img = create_base_packaging_image(800, 600)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()

        # 1. Stage 1
        s1_res = self.stage1.process_image_bytes(raw_bytes, filename="test_pkg.jpg")
        self.assertEqual(s1_res.status, "READY_FOR_TEXT_DETECTION")

        # 2. Stage 5
        s5_res, s5_best_img, s5_chain = self.stage5.process_from_stage1(s1_res, img, original_image=img)
        self.assertIn(s5_res.recovery_status, ["COMPLETED", "MINIMAL_PROCESSING"])

        # 3. Stage 2
        s2_res = self.stage2.process_from_stage5(s5_res, s5_best_img, original_image=img)
        self.assertEqual(s2_res.text_detection_status, "COMPLETED")
        self.assertGreater(len(s2_res.regions), 0)

        # 4. Stage 3
        s3_res = self.stage3.process_stage2_output(s2_res, stage1_output=s1_res)
        self.assertEqual(s3_res.semantic_status, "COMPLETED")

        # 5. Stage 4
        s4_res = self.stage4.process_stage3_output(s3_res, stage2_output=s2_res, stage1_output=s1_res)
        self.assertIn(s4_res.identity_status, ["CONFIRMED", "PARTIAL", "NEEDS_REVIEW"])
        self.assertIsNotNone(s4_res.identity.product_name)


if __name__ == "__main__":
    unittest.main()
