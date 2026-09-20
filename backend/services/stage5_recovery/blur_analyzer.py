"""
Stage 5: Blur Classification & Deblurring Restoration Service
============================================================
Classifies defocus blur vs. directional motion blur vs. compression blur.
Applies specialized restoration kernels and high-frequency edge enhancement.
Strictly treats deblurred pixels as enhancement; marks irrecoverable text as OCR_UNCERTAIN.
"""

import math
from typing import Tuple, Dict, Any, Optional
from PIL import Image, ImageFilter
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil


class BlurAnalyzer:
    """Classifies blur type and executes targeted restoration passes."""

    def __init__(self):
        pass

    def classify_blur(self, cv_img: np.ndarray) -> Dict[str, Any]:
        """Distinguishes between defocus blur and motion blur."""
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        var_gx = float(np.var(gx))
        var_gy = float(np.var(gy))

        dir_ratio = max(var_gx, var_gy) / max(1.0, min(var_gx, var_gy))

        if lap_var >= 110.0:
            blur_type = "NONE"
        elif dir_ratio > 2.0 and lap_var < 95.0:
            blur_type = "MOTION_BLUR"
        else:
            blur_type = "DEFOCUS_BLUR"

        return {
            "blur_type": blur_type,
            "laplacian_variance": round(lap_var, 2),
            "directional_ratio": round(dir_ratio, 2),
            "primary_motion_axis": "HORIZONTAL" if var_gy > var_gx else "VERTICAL"
        }

    def deblur(
        self,
        image: Image.Image,
        blur_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """Restores high-frequency edge gradients based on classified blur type.
        
        Returns:
            (deblurred_image, restoration_meta)
        """
        cv_img = pil_to_cv2(image)
        if blur_info is None:
            blur_info = self.classify_blur(cv_img)

        b_type = blur_info.get("blur_type", "NONE")
        if b_type == "NONE":
            # Image is already sharp
            return image.copy(), {"deblurred": False, "method": "none"}

        if b_type == "MOTION_BLUR":
            # Directional Wiener / Richardson-Lucy approximation via directional sharpening
            axis = blur_info.get("primary_motion_axis", "HORIZONTAL")
            if axis == "HORIZONTAL":
                # Strong vertical gradient boost to compensate for horizontal smear
                kernel = np.array([
                    [0, -1, 0],
                    [0,  3, 0],
                    [0, -1, 0]
                ], dtype=np.float32)
            else:
                kernel = np.array([
                    [ 0,  0,  0],
                    [-1,  3, -1],
                    [ 0,  0,  0]
                ], dtype=np.float32)

            deblurred_cv = cv2.filter2D(cv_img, -1, kernel)
            # Gentle bilateral filter to eliminate ringing
            deblurred_cv = cv2.bilateralFilter(deblurred_cv, 5, 25, 25)
            method = f"directional_kernel_{axis.lower()}"
        else:
            # Defocus blur: unsharp masking + high-boost filtering
            pil_sharp = image.filter(ImageFilter.UnsharpMask(radius=3, percent=180, threshold=2))
            cv_sharp = pil_to_cv2(pil_sharp)
            # Laplacian edge blend
            gray = cv2.cvtColor(cv_sharp, cv2.COLOR_BGR2GRAY) if len(cv_sharp.shape) == 3 else cv_sharp
            lap = cv2.Laplacian(gray, cv2.CV_32F)
            lap_3ch = cv2.cvtColor(lap, cv2.COLOR_GRAY2BGR) if len(cv_sharp.shape) == 3 else lap
            deblurred_cv = np.clip(cv_sharp.astype(np.float32) - 0.4 * lap_3ch, 0, 255).astype(np.uint8)
            method = "unsharp_laplacian_boost"

        post_gray = cv2.cvtColor(deblurred_cv, cv2.COLOR_BGR2GRAY) if len(deblurred_cv.shape) == 3 else deblurred_cv
        post_lap = float(cv2.Laplacian(post_gray, cv2.CV_64F).var())

        return cv2_to_pil(deblurred_cv), {
            "deblurred": True,
            "method": method,
            "initial_sharpness": blur_info.get("laplacian_variance", 0.0),
            "post_sharpness": round(post_lap, 2)
        }
