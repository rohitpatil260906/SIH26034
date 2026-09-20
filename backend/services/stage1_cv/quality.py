"""
Stage 1: Image Quality Analysis Service (18 Dimensions)
======================================================
Evaluates packaging label images across 18 distinct optical & statutory dimensions:
1. Overall Blur (Laplacian variance)
2. Motion Blur (Directional gradient spread)
3. Defocus Blur (Fourier high-frequency attenuation)
4. Image Resolution (Megapixels & dimensional adequacy)
5. Noise Level (High-frequency residual variance)
6. Contrast Level (RMS contrast / dynamic range)
7. Overexposure (Highlight clipping fraction)
8. Underexposure (Shadow clipping fraction)
9. Glare / Specular Reflections (Localized highlight hotspots)
10. Shadow Interference (Local illumination variance)
11. Perspective Distortion Angle (Keystone skew estimation)
12. Curvature Distortion (Cylindrical warp estimation)
13. Occlusion Level (Skin-tone / hand detection on package)
14. Package Border Clipping (Proximity to frame boundaries)
15. Text Size Suitability (Estimated glyph height in px)
16. Compression Artifacts (8x8 DCT grid discontinuity)
17. Color Degradation / Fading (Chroma variance)
18. Overall Quality Categorization (GOOD, DEGRADED, INSUFFICIENT)

Guarantees:
- Never crashes on corrupted, blank, or extreme inputs
- If INSUFFICIENT, provides human-readable reasons and prevents false statutory violations
"""

import math
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np
import cv2

from ...models import Stage1QualityResult
from ..cv_pipeline import pil_to_cv2


class QualityAnalyzerService:
    """18-dimension image quality evaluator for packaging compliance scans."""

    def __init__(self):
        pass

    def evaluate_image(
        self,
        image: Image.Image
    ) -> Tuple[Stage1QualityResult, Dict[str, Any]]:
        """Evaluates an image across all 18 dimensions.
        
        Returns:
            (Stage1QualityResult, full_metrics_dict)
        """
        try:
            cv_img = pil_to_cv2(image)
        except Exception as e:
            result = Stage1QualityResult(
                status="INSUFFICIENT",
                overall_score=0.0,
                blur_score=0.0,
                resolution_score=0.0,
                contrast_score=0.0,
                glare_score=0.0,
                perspective_score=0.0,
                curvature_score=0.0,
                occlusion_score=0.0,
                issues=[f"Image format unreadable: {str(e)}"],
                explanation="Failed to convert image to CV2 matrix."
            )
            return result, {}

        h, w = cv_img.shape[:2]
        if len(cv_img.shape) == 3:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        else:
            gray = cv_img
            hsv = None

        issues: List[str] = []

        # 1. Overall Blur (Laplacian Variance)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if laplacian_var >= 250.0:
            blur_score = 100.0
        elif laplacian_var >= 80.0:
            blur_score = 70.0 + 30.0 * ((laplacian_var - 80.0) / 170.0)
        elif laplacian_var >= 30.0:
            blur_score = 40.0 + 30.0 * ((laplacian_var - 30.0) / 50.0)
            issues.append(f"Moderate blur detected (Laplacian: {laplacian_var:.1f}). Text may require sharpening.")
        else:
            blur_score = max(5.0, (laplacian_var / 30.0) * 40.0)
            issues.append(f"Severe blur detected (Laplacian: {laplacian_var:.1f} < 30.0). Text illegible.")

        # 2. Motion Blur (Directional gradient anisotropy)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        var_x = float(np.var(sobel_x))
        var_y = float(np.var(sobel_y))
        ratio_xy = (var_x / (var_y + 1e-5)) if var_y > 0 else 1.0
        is_motion_blurred = ratio_xy > 3.5 or ratio_xy < 0.28
        if is_motion_blurred:
            issues.append(f"Directional motion blur detected (Gradient anisotropy: {ratio_xy:.2f}).")

        # 3. Defocus Blur (High frequency energy via Fourier Transform)
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        center_y, center_x = h // 2, w // 2
        r_cutoff = min(h, w) // 8
        y_coords, x_coords = np.ogrid[:h, :w]
        mask_high = ((y_coords - center_y)**2 + (x_coords - center_x)**2) > (r_cutoff**2)
        total_energy = float(np.sum(magnitude_spectrum)) + 1e-5
        high_freq_energy = float(np.sum(magnitude_spectrum[mask_high]))
        high_freq_ratio = high_freq_energy / total_energy
        defocus_blur = high_freq_ratio < 0.25

        # 4. Image Resolution
        megapixels = round((w * h) / 1_000_000.0, 2)
        min_dim = min(w, h)
        if min_dim >= 800:
            resolution_score = 100.0
        elif min_dim >= 450:
            resolution_score = 75.0
        elif min_dim >= 250:
            resolution_score = 45.0
            issues.append(f"Low resolution ({w}x{h}, {megapixels} MP). Small statutory declarations may be pixelated.")
        else:
            resolution_score = 15.0
            issues.append(f"Insufficient resolution ({w}x{h} < 250px). Mandatory text unreadable.")

        # 5. Noise Level
        blurred_gray = cv2.GaussianBlur(gray, (5, 5), 0)
        noise_residual = gray.astype(np.float32) - blurred_gray.astype(np.float32)
        noise_sigma = float(np.std(noise_residual))
        is_noisy = noise_sigma > 18.0
        if is_noisy:
            issues.append(f"High sensor noise detected (Sigma: {noise_sigma:.1f}).")

        # 6. Contrast Level (RMS Contrast)
        norm_gray = gray.astype(np.float32) / 255.0
        rms_contrast = float(np.std(norm_gray))
        if rms_contrast >= 0.14:
            contrast_score = 100.0
        elif rms_contrast >= 0.07:
            contrast_score = 75.0
        elif rms_contrast >= 0.03:
            contrast_score = 50.0
        else:
            contrast_score = 25.0
            issues.append(f"Low image contrast (RMS: {rms_contrast:.2f}). Inadequate contrast with background.")

        # 7. Overexposure (Highlight clipping)
        mean_val = float(np.mean(gray))
        overexposed_pixels = np.sum(gray >= 253)
        overexposure_pct = float(overexposed_pixels) / float(w * h) * 100.0
        # Overexposure is flagged when image is heavily washed out (mean > 240) and highlights exceed 60%
        if mean_val > 242.0 and overexposure_pct > 60.0:
            issues.append(f"Severe overexposure ({overexposure_pct:.1f}% washed out highlights).")

        # 8. Underexposure (Shadow clipping)
        underexposed_pixels = np.sum(gray <= 12)
        underexposure_pct = float(underexposed_pixels) / float(w * h) * 100.0
        if mean_val < 35.0 and underexposure_pct > 40.0:
            issues.append(f"Severe underexposure ({underexposure_pct:.1f}% clipped dark regions).")

        # 9. Glare / Specular Reflections
        # Specular glare occurs in localized hotspots where pixel intensity is saturated (>= 250)
        glare_pixels = int(np.sum(gray >= 250))
        glare_pct = (float(glare_pixels) / float(w * h)) * 100.0

        # If more than 35% of the image is at 250 (common for white paper packaging/labels),
        # inspect ultra-saturated highlight pixels (>= 254) to isolate true specular hotspot
        if glare_pct > 35.0:
            ultra_bright = int(np.sum(gray >= 254))
            ultra_pct = (float(ultra_bright) / float(w * h)) * 100.0
            glare_pct = ultra_pct if ultra_pct <= 35.0 else 0.0

        if glare_pct <= 1.5:
            glare_score = 100.0
        elif glare_pct <= 8.0:
            glare_score = round(max(20.0, 100.0 - (glare_pct * 4.0)), 1)
        elif glare_pct <= 20.0:
            glare_score = round(max(15.0, 70.0 - (glare_pct * 2.5)), 1)
            issues.append(f"Noticeable glare reflections ({glare_pct:.1f}% area). May obscure label text.")
        else:
            glare_score = 15.0
            issues.append(f"Heavy specular glare ({glare_pct:.1f}% area). Portions of label completely obliterated.")

        # 10. Shadow Interference (Local illumination variance)
        block_h = max(16, h // 8)
        block_w = max(16, w // 8)
        block_means = []
        for r in range(0, h - block_h + 1, block_h):
            for c in range(0, w - block_w + 1, block_w):
                block = gray[r : r + block_h, c : c + block_w]
                block_means.append(np.mean(block))
        illum_std = float(np.std(block_means)) if block_means else 0.0
        has_shadow_interference = illum_std > 52.0
        if has_shadow_interference:
            issues.append("Uneven illumination / deep shadow across package label.")

        # 11. Perspective Distortion Angle
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 80, minLineLength=min(w, h) // 6, maxLineGap=10)
        max_skew_deg = 0.0
        if lines is not None and len(lines) > 0:
            angles = []
            for l in lines:
                pts = l.flatten()
                if len(pts) < 4:
                    continue
                x1, y1, x2, y2 = int(pts[0]), int(pts[1]), int(pts[2]), int(pts[3])
                ang = abs(math.degrees(math.atan2(y2 - y1, x2 - x1)))
                # Normalize to deviation from horizontal (0) or vertical (90)
                dev_h = min(ang, abs(180.0 - ang))
                dev_v = abs(90.0 - ang)
                angles.append(min(dev_h, dev_v))
            if angles:
                max_skew_deg = float(np.percentile(angles, 75))
        perspective_detected = max_skew_deg > 14.0
        perspective_score = max(20.0, 100.0 - (max_skew_deg * 3.5))
        if perspective_detected:
            issues.append(f"Significant perspective tilt detected ({max_skew_deg:.1f}°). Rectification recommended.")

        # 12. Curvature Distortion (Detect nonlinear curved edges)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        has_curvature = False
        for cnt in contours:
            if cv2.contourArea(cnt) > (w * h * 0.05):
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                cnt_area = cv2.contourArea(cnt)
                solidity = cnt_area / (hull_area + 1e-5)
                if solidity < 0.75:
                    has_curvature = True
                    break
        curvature_score = 70.0 if has_curvature else 95.0

        # 13. Occlusion Level (Detect human skin tone / fingers holding label)
        occlusion_pct = 0.0
        if hsv is not None:
            # Human skin HSV range
            lower_skin = np.array([0, 25, 60], dtype=np.uint8)
            upper_skin = np.array([25, 250, 255], dtype=np.uint8)
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            # Focus on border regions where fingers usually hold package
            border_mask = np.zeros((h, w), dtype=np.uint8)
            border_thickness = int(min(h, w) * 0.15)
            border_mask[:border_thickness, :] = 255
            border_mask[-border_thickness:, :] = 255
            border_mask[:, :border_thickness] = 255
            border_mask[:, -border_thickness:] = 255
            skin_in_border = cv2.bitwise_and(skin_mask, border_mask)
            occlusion_pct = (float(np.sum(skin_in_border > 0)) / float(w * h)) * 100.0
        occlusion_score = max(10.0, 100.0 - (occlusion_pct * 4.0))
        if occlusion_pct > 12.0:
            issues.append(f"Fingers/hands occluding package border ({occlusion_pct:.1f}% border occlusion).")

        # 14. Package Border Clipping (Check if edges touch the frame border)
        border_pixels = np.sum(gray[0, :] < 240) + np.sum(gray[-1, :] < 240) + np.sum(gray[:, 0] < 240) + np.sum(gray[:, -1] < 240)
        total_border = 2 * w + 2 * h
        is_clipped = (border_pixels / total_border) > 0.85
        if is_clipped:
            issues.append("Package borders appear clipped by camera frame. Portions of label may be cut off.")

        # 15. Estimated Text Size (Connected components)
        thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh_otsu)
        heights = []
        for i in range(1, num_labels):
            box_h = stats[i, cv2.CC_STAT_HEIGHT]
            box_w = stats[i, cv2.CC_STAT_WIDTH]
            area = stats[i, cv2.CC_STAT_AREA]
            if 6 <= box_h <= 120 and 4 <= box_w <= 300 and area > 12:
                heights.append(box_h)
        est_glyph_h = float(np.median(heights)) if heights else 14.0

        # 16. Compression Artifacts (8x8 DCT boundary discontinuities)
        min_h_blocks = min(gray[7::8, :].shape[0], gray[8::8, :].shape[0])
        if min_h_blocks > 0:
            diff_h = np.abs(gray[7:7 + min_h_blocks * 8:8, :].astype(np.float32) - gray[8:8 + min_h_blocks * 8:8, :].astype(np.float32))
        else:
            diff_h = np.array([0.0])

        min_w_blocks = min(gray[:, 7::8].shape[1], gray[:, 8::8].shape[1])
        if min_w_blocks > 0:
            diff_w = np.abs(gray[:, 7:7 + min_w_blocks * 8:8].astype(np.float32) - gray[:, 8:8 + min_w_blocks * 8:8].astype(np.float32))
        else:
            diff_w = np.array([0.0])

        comp_score = float(np.mean(diff_h) + np.mean(diff_w)) / 2.0
        has_heavy_compression = comp_score > 22.0
        if has_heavy_compression:
            issues.append("High JPEG compression artifacts detected. Text edges may have ringing noise.")

        # 17. Color Degradation / Fading
        if hsv is not None:
            sat_channel = hsv[:, :, 1]
            chroma_mean = float(np.mean(sat_channel))
        else:
            chroma_mean = 0.0

        # 18. Overall Quality Categorization
        # Composite score
        overall_score = round(
            0.30 * blur_score +
            0.20 * resolution_score +
            0.15 * contrast_score +
            0.15 * glare_score +
            0.10 * perspective_score +
            0.10 * occlusion_score,
            1
        )

        # Gating conditions
        # INSUFFICIENT when:
        # 1. Laplacian variance < 20.0 (unusable blur)
        # 2. Glare covers > 30% of the frame
        # 3. Min dimension < 180px (extreme low-res)
        # 4. Occlusion > 45%
        # 5. overall_score < 30.0
        is_insufficient = (
            laplacian_var < 20.0 or
            glare_pct > 30.0 or
            min_dim < 180 or
            occlusion_pct > 45.0 or
            overall_score < 30.0
        )

        if is_insufficient:
            status = "INSUFFICIENT"
            explanation = (
                "Image quality is insufficient for legal compliance verification. "
                "Please retake the photo with good lighting, sharp focus, and all borders visible."
            )
        elif overall_score < 70.0 or len(issues) > 1:
            status = "DEGRADED"
            explanation = (
                "Image has degraded optical quality (e.g. minor blur, glare, or skew). "
                "Preprocessing pipelines will enhance image before text extraction."
            )
        else:
            status = "GOOD"
            explanation = "Image quality is optimal for packaging label compliance scanning."

        quality_result = Stage1QualityResult(
            status=status,
            overall_score=overall_score,
            blur_score=round(blur_score, 1),
            resolution_score=round(resolution_score, 1),
            contrast_score=round(contrast_score, 1),
            glare_score=round(glare_score, 1),
            perspective_score=round(perspective_score, 1),
            curvature_score=round(curvature_score, 1),
            occlusion_score=round(occlusion_score, 1),
            issues=issues,
            explanation=explanation
        )

        full_metrics = {
            "laplacian_variance": laplacian_var,
            "is_motion_blurred": is_motion_blurred,
            "defocus_blur": defocus_blur,
            "megapixels": megapixels,
            "width": w,
            "height": h,
            "noise_sigma": noise_sigma,
            "rms_contrast": rms_contrast,
            "overexposure_pct": overexposure_pct,
            "underexposure_pct": underexposure_pct,
            "glare_pct": glare_pct,
            "shadow_illum_std": illum_std,
            "max_skew_deg": max_skew_deg,
            "has_curvature": has_curvature,
            "occlusion_pct": occlusion_pct,
            "is_border_clipped": is_clipped,
            "est_glyph_h_px": est_glyph_h,
            "compression_artifact_score": comp_score,
            "chroma_mean": chroma_mean,
            "quality_status": status,
            "overall_score": overall_score,
            "issues_count": len(issues)
        }

        return quality_result, full_metrics
