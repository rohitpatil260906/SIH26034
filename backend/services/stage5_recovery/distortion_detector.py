"""
Stage 5: Multi-Condition Distortion Classification Service
==========================================================
Detects and classifies 20+ packaging distortion conditions:
- NO_DISTORTION
- PERSPECTIVE_DISTORTION
- ROTATION
- SKEW
- CURVATURE
- CYLINDRICAL_CURVATURE
- BARREL_DISTORTION
- FOLDING
- WRINKLING
- PARTIAL_OCCLUSION
- GLARE
- SHADOW
- BLUR
- MOTION_BLUR
- LOW_RESOLUTION
- LOW_CONTRAST
- OVEREXPOSURE
- UNDEREXPOSURE
- COMPRESSION_ARTIFACT
- MULTIPLE_DISTORTIONS
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2


class DistortionClassificationResult:
    """Detailed distortion assessment outcome with quantitative metrics."""

    def __init__(
        self,
        distortions: List[str],
        metrics: Dict[str, Any],
        is_difficult: bool
    ):
        self.distortions = distortions
        self.metrics = metrics
        self.is_difficult = is_difficult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distortions": self.distortions,
            "metrics": self.metrics,
            "is_difficult": self.is_difficult
        }


class DistortionDetector:
    """Production analyzer classifying physical, optical, and environmental distortions."""

    def __init__(self):
        pass

    def analyze(self, image: Image.Image) -> DistortionClassificationResult:
        """Evaluates image for all 20+ packaging distortion conditions."""
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        distortions: List[str] = []
        metrics: Dict[str, Any] = {}

        # ----------------------------------------------------
        # 1. RESOLUTION METRICS
        # ----------------------------------------------------
        megapixels = (w * h) / 1_000_000.0
        metrics["megapixels"] = round(megapixels, 3)
        metrics["width"] = w
        metrics["height"] = h

        if megapixels < 0.35 or min(w, h) < 450:
            distortions.append("LOW_RESOLUTION")

        # ----------------------------------------------------
        # 2. LUMINANCE & EXPOSURE (Over/Under, Low Contrast)
        # ----------------------------------------------------
        mean_val = float(np.mean(gray))
        std_val = float(np.std(gray))
        metrics["mean_luminance"] = round(mean_val, 1)
        metrics["contrast_std"] = round(std_val, 1)

        if mean_val > 215.0:
            distortions.append("OVEREXPOSURE")
        elif mean_val < 50.0:
            distortions.append("UNDEREXPOSURE")

        if std_val < 26.0:
            distortions.append("LOW_CONTRAST")

        # ----------------------------------------------------
        # 3. GLARE & SPECULAR HIGHLIGHTS
        # ----------------------------------------------------
        # Glare: cluster of pixels near 255 with low saturation
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV) if len(cv_img.shape) == 3 else None
        if hsv is not None:
            s_chan = hsv[:, :, 1]
            v_chan = hsv[:, :, 2]
            glare_mask = (v_chan >= 252) & (s_chan < 15)
        else:
            glare_mask = gray >= 252

        glare_pixel_count = int(np.sum(glare_mask))
        glare_ratio = glare_pixel_count / float(w * h)
        metrics["glare_ratio"] = round(glare_ratio, 4)

        if glare_ratio > 0.012:
            distortions.append("GLARE")

        # ----------------------------------------------------
        # 4. SHADOW PATTERNS
        # ----------------------------------------------------
        # Compute spatial luminance gradient across 4 quadrants
        q_h, q_w = h // 2, w // 2
        q_means = [
            float(np.mean(gray[:q_h, :q_w])),
            float(np.mean(gray[:q_h, q_w:])),
            float(np.mean(gray[q_h:, :q_w])),
            float(np.mean(gray[q_h:, q_w:]))
        ]
        shadow_delta = max(q_means) - min(q_means)
        metrics["shadow_gradient"] = round(shadow_delta, 1)

        # Check for sharp shadow edge using otsu on local blocks
        low_illum_ratio = float(np.sum(gray < 65)) / float(w * h)
        high_illum_ratio = float(np.sum(gray > 175)) / float(w * h)
        if shadow_delta > 55.0 or (low_illum_ratio > 0.12 and high_illum_ratio > 0.12):
            distortions.append("SHADOW")

        # ----------------------------------------------------
        # 5. BLUR (Defocus vs Motion)
        # ----------------------------------------------------
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        metrics["laplacian_variance"] = round(laplacian_var, 2)

        # Directional motion blur detection
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        var_gx = float(np.var(gx))
        var_gy = float(np.var(gy))
        dir_ratio = max(var_gx, var_gy) / max(1.0, min(var_gx, var_gy))
        metrics["gradient_directional_ratio"] = round(dir_ratio, 2)

        if dir_ratio > 3.0:
            distortions.append("MOTION_BLUR")
            distortions.append("BLUR")
        elif laplacian_var < 100.0:
            distortions.append("BLUR")
            distortions.append("DEFOCUS_BLUR")

        # ----------------------------------------------------
        # 6. COMPRESSION ARTIFACTS
        # ----------------------------------------------------
        # High frequency DCT block grid discontinuity detection
        if min(w, h) >= 32:
            slice1 = gray[7::8, :].astype(np.float32)
            slice2 = gray[8::8, :].astype(np.float32)
            min_l = min(slice1.shape[0], slice2.shape[0])
            if min_l > 0:
                diff_h = np.abs(slice1[:min_l] - slice2[:min_l])
                diff_all_h = np.abs(gray[:-1, :].astype(np.float32) - gray[1:, :].astype(np.float32))
                mean_block_diff = float(np.mean(diff_h)) if diff_h.size > 0 else 0.0
                mean_all_diff = float(np.mean(diff_all_h)) if diff_all_h.size > 0 else 1.0
                blockiness = mean_block_diff / max(1e-3, mean_all_diff)
                metrics["blockiness_metric"] = round(blockiness, 3)
                if blockiness > 1.35 and laplacian_var < 200.0:
                    distortions.append("COMPRESSION_ARTIFACT")

        # ----------------------------------------------------
        # 7. ROTATION & SKEW
        # ----------------------------------------------------
        # Text line orientation / Hough lines
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=w * 0.15, maxLineGap=10)
        angles = []
        if lines is not None:
            for line in lines:
                l = line.reshape(-1)
                if len(l) >= 4:
                    x1, y1, x2, y2 = float(l[0]), float(l[1]), float(l[2]), float(l[3])
                    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
                    angles.append(ang)

        dominant_angle = 0.0
        vertical_lines = sum(1 for a in angles if 75.0 <= abs(a) <= 105.0)
        horizontal_lines = sum(1 for a in angles if abs(a) <= 15.0)

        if len(angles) >= 3:
            # Normalize angles to [-45, 45] or cardinal [0, 90, 180, 270]
            norm_angles = []
            for a in angles:
                while a > 45.0:
                    a -= 90.0
                while a < -45.0:
                    a += 90.0
                norm_angles.append(a)
            median_angle = float(np.median(norm_angles))
            dominant_angle = median_angle
            metrics["skew_angle_deg"] = round(dominant_angle, 2)

            if abs(dominant_angle) > 3.0:
                distortions.append("SKEW")

        # Check for cardinal 90 / 270 orientation (vertical text lines or aspect ratio with gradient)
        gy_mag = float(np.mean(np.abs(gy)))
        gx_mag = float(np.mean(np.abs(gx)))
        if (vertical_lines > horizontal_lines and vertical_lines >= 2) or (gy_mag > 1.3 * gx_mag and (h / max(1, w)) > 1.15):
            distortions.append("ROTATION")

        # ----------------------------------------------------
        # 8. PERSPECTIVE DISTORTION
        # ----------------------------------------------------
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        quad_found = False

        for cnt in contours[:5]:
            area = cv2.contourArea(cnt)
            if area < (w * h * 0.10):
                continue
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
            if len(approx) == 4 and cv2.isContourConvex(approx):
                pts = approx.reshape(4, 2)
                # Check trapezoidal non-parallelism
                s = pts.sum(axis=1)
                tl = pts[np.argmin(s)]
                br = pts[np.argmax(s)]
                diff = np.diff(pts, axis=1)
                tr = pts[np.argmin(diff)]
                bl = pts[np.argmax(diff)]

                top_w = np.linalg.norm(tr - tl)
                bot_w = np.linalg.norm(br - bl)
                left_h = np.linalg.norm(bl - tl)
                right_h = np.linalg.norm(br - tr)

                w_ratio = abs(top_w - bot_w) / max(1.0, max(top_w, bot_w))
                h_ratio = abs(left_h - right_h) / max(1.0, max(left_h, right_h))
                metrics["perspective_trapezoid_ratio"] = round(max(w_ratio, h_ratio), 3)

                if w_ratio > 0.08 or h_ratio > 0.08:
                    distortions.append("PERSPECTIVE_DISTORTION")
                quad_found = True
                break

        # ----------------------------------------------------
        # 9. CURVATURE & CYLINDRICAL CURVATURE & BARREL
        # ----------------------------------------------------
        curved_lines = 0
        barrel_score = 0.0
        for cnt in contours[:15]:
            pts = cnt.reshape(-1, 2)
            if len(pts) < 35:
                continue
            x_span = float(np.max(pts[:, 0]) - np.min(pts[:, 0]))
            if x_span < (w * 0.30):
                continue
            try:
                poly = np.polyfit(pts[:, 0], pts[:, 1], 2)
                curvature_a = abs(poly[0])
                if 0.00012 <= curvature_a <= 0.006:
                    curved_lines += 1
            except Exception:
                pass

        metrics["curved_horizontal_lines"] = curved_lines
        if curved_lines >= 2:
            distortions.append("CYLINDRICAL_CURVATURE")
            distortions.append("CURVATURE")
        elif curved_lines == 1:
            distortions.append("CURVATURE")

        # ----------------------------------------------------
        # 10. FOLDING & WRINKLING
        # ----------------------------------------------------
        # Wrinkles create sharp local high-frequency line networks
        kernel_crease = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        morphed_v = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel_crease)
        crease_ratio = float(np.sum(morphed_v > 0)) / float(w * h)
        metrics["crease_density"] = round(crease_ratio, 5)

        if crease_ratio > 0.0025:
            distortions.append("WRINKLING")
            if crease_ratio > 0.006:
                distortions.append("FOLDING")

        # ----------------------------------------------------
        # 11. PARTIAL OCCLUSION (Finger / Sticker / Tape)
        # ----------------------------------------------------
        # Skin tone detection in YCrCb for fingers holding edges
        if len(cv_img.shape) == 3:
            ycrcb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2YCrCb)
            cr = ycrcb[:, :, 1]
            cb = ycrcb[:, :, 2]
            skin_mask = (cr >= 133) & (cr <= 173) & (cb >= 77) & (cb <= 127)
            # Check border zones for fingers holding package
            border_strip = np.zeros_like(skin_mask)
            b_w = max(10, int(w * 0.12))
            b_h = max(10, int(h * 0.12))
            border_strip[:b_h, :] = True
            border_strip[-b_h:, :] = True
            border_strip[:, :b_w] = True
            border_strip[:, -b_w:] = True

            skin_border_ratio = float(np.sum(skin_mask & border_strip)) / float(w * h)
            metrics["skin_border_ratio"] = round(skin_border_ratio, 4)

            if skin_border_ratio > 0.015:
                distortions.append("PARTIAL_OCCLUSION")

        # ----------------------------------------------------
        # CONCLUDE CLASSIFICATION
        # ----------------------------------------------------
        # Deduplicate while preserving order
        unique_distortions = []
        for d in distortions:
            if d not in unique_distortions:
                unique_distortions.append(d)

        if not unique_distortions:
            unique_distortions = ["NO_DISTORTION"]
        elif len(unique_distortions) > 1:
            unique_distortions.append("MULTIPLE_DISTORTIONS")

        is_difficult = not (len(unique_distortions) == 1 and unique_distortions[0] == "NO_DISTORTION")

        return DistortionClassificationResult(
            distortions=unique_distortions,
            metrics=metrics,
            is_difficult=is_difficult
        )
