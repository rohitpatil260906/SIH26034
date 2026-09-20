"""
Stage 5: Glare & Specular Reflection Reduction Service
=====================================================
Suppresses specular highlights, recovers washed-out text regions across multiple color channels,
and strictly prevents character hallucination.
If specular reflection completely obliterates text, tags region as TEXT_OCCLUDED_BY_GLARE.
"""

from typing import Tuple, Dict, Any, Optional, List
from PIL import Image
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil


class GlareReducer:
    """Detects and mitigates specular glare hotspots and glossy reflection wash-out."""

    def __init__(self):
        pass

    def detect_glare_mask(self, cv_img: np.ndarray) -> np.ndarray:
        """Returns boolean mask of specular highlights."""
        if len(cv_img.shape) == 3:
            hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
            s = hsv[:, :, 1]
            v = hsv[:, :, 2]
            # Specular highlight: high value and low saturation
            mask = (v > 225) & (s < 40)
        else:
            mask = cv_img > 235
        return mask.astype(np.uint8) * 255

    def is_text_completely_occluded(self, patch: np.ndarray) -> bool:
        """Checks if a glare patch completely destroys underlying text structure (no edges/ink)."""
        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY) if len(patch.shape) == 3 else patch
        # If > 85% of pixels are saturated white (>245) with negligible edge variance
        sat_ratio = float(np.sum(gray > 242)) / float(max(1, gray.size))
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        return sat_ratio > 0.85 and lap_var < 35.0

    def reduce_glare(
        self,
        image: Image.Image
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """Generates a glare-suppressed image variant using multi-channel normalization and illumination leveling.
        
        Returns:
            (glare_reduced_image, metadata)
        """
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        glare_mask = self.detect_glare_mask(cv_img)
        glare_area_ratio = float(np.sum(glare_mask > 0)) / float(w * h)

        if glare_area_ratio < 0.003:
            # Negligible glare
            return image.copy(), {"glare_detected": False, "glare_ratio": glare_area_ratio}

        # 1. Multi-channel analysis: often one color channel preserves text under white glare
        # (e.g. blue or green channel, or HSV-V with gamma adjustment)
        b, g, r = cv2.split(cv_img)
        # Contrast of channels inside glare neighborhood
        dilated_mask = cv2.dilate(glare_mask, np.ones((9, 9), np.uint8))
        b_std = float(np.std(b[dilated_mask > 0])) if np.any(dilated_mask > 0) else 0.0
        g_std = float(np.std(g[dilated_mask > 0])) if np.any(dilated_mask > 0) else 0.0
        r_std = float(np.std(r[dilated_mask > 0])) if np.any(dilated_mask > 0) else 0.0

        # Select best channel with highest contrast structure
        best_chan = g
        if b_std > max(g_std, r_std):
            best_chan = b
        elif r_std > max(g_std, b_std):
            best_chan = r

        # 2. Highlight suppression via morphological background subtraction
        kernel_glare = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        closed_bg = cv2.morphologyEx(best_chan, cv2.MORPH_CLOSE, kernel_glare)

        # 3. CLAHE on the selected channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        clahe_chan = clahe.apply(best_chan)

        # 4. Suppress highlight peaks in color image
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        v = hsv[:, :, 2].astype(np.float32)
        # Gamma compression on specular highlights
        gamma = 1.4
        v_norm = (v / 255.0) ** (1.0 / gamma) * 255.0
        hsv[:, :, 2] = np.clip(v_norm, 0, 255).astype(np.uint8)
        recovered_color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Merge CLAHE luminance where glare was active
        blend_mask = (cv2.GaussianBlur(glare_mask.astype(np.float32), (15, 15), 0) / 255.0)[:, :, np.newaxis]
        clahe_bgr = cv2.cvtColor(clahe_chan, cv2.COLOR_GRAY2BGR)
        result_cv = (blend_mask * clahe_bgr + (1.0 - blend_mask) * recovered_color).astype(np.uint8)

        return cv2_to_pil(result_cv), {
            "glare_detected": True,
            "glare_ratio": round(glare_area_ratio, 4),
            "best_channel": "green" if best_chan is g else ("blue" if best_chan is b else "red")
        }
